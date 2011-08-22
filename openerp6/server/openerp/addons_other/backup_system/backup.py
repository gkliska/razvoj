# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Gábor Dukai <gdukai@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import uuid
import os
import tarfile
import sys
import StringIO
import zlib
import datetime
import shutil
import string

from osv import osv, fields

from _utils import make_archive

class backup(osv.osv):
    _name = 'backup'
    _description = 'Backup Configuration'

    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'task_ids': fields.one2many('backup.task', 'backup_id', 'Tasks'),
        'target_ids': fields.one2many('backup.target', 'backup_id', 'Targets'),
        'param_ids': fields.one2many('backup.param', 'backup_id', 'Parameters'),
    }

backup()

class backup_task(osv.osv):
    """
    It holds the backup python code itself. It needs the Target to get
    a destination directory for the created archive.
    """
    _name = 'backup.task'
    _description = 'Task'

    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'backup_id': fields.many2one('backup', 'Configuration', required=True),
        'code': fields.text('Python Code', required=True, help='Python code to be executed'),
        'log': fields.text('Latest Log', readonly=True),
        'type': fields.selection([
            ('immutable', 'Create new archive'),
            ('sync', 'Keep a dir. in sync'),
        ], 'Type', required=True),
        'delete_archived': fields.boolean('Delete archived files'),
        'from_path': fields.char('Source Path', size=64, required=True),
    }

    def _2filename(self, name):
        safe_name = name.replace(' ', '_')
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in safe_name if c in valid_chars)

    def run(self, cr, uid, ids, target_id):
        target_obj = self.pool.get('backup.target')
        job_obj = self.pool.get('backup.job')
        target = target_obj.browse(cr, uid, target_id)
        target_obj.connect_verify(cr, uid, [target_id])
        try:
            for task in self.browse(cr, uid, ids):
                job_path = None
                if task.type == 'sync':
                    job_ids = job_obj.search(cr, uid, [
                        ('task_id', '=', task.id),
                        ('storage_id', '=', target.storage_id.id)])
                    if job_ids:
                        job = job_obj.browse(cr, uid, job_ids[0])
                        job_path = os.path.join(target.path, job.name)
                params = {}
                for param in target.backup_id.param_ids:
                    params[param.name] = param.value
                localdict = {
                    'task_name': self._2filename(task.name),
                    'target_path': target.path,
                    'date': datetime.datetime.today(),
                    'make_archive': make_archive,
                    'job_path': job_path,
                    'from_path': task.from_path,
                    'params': params,
                    }
                exec task.code in localdict
                if 'log' in localdict:
                    self.write(cr, uid, task.id, {'log': localdict['log']})
                    cr.commit()
                if not localdict['success']:
                    raise osv.except_osv('Error', "There was an error running %s" % task.name)
                if task.type == 'immutable':
                    t = tarfile.open(localdict['job_path'])
                    s = StringIO.StringIO()
                    orig = sys.stdout
                    sys.stdout = s
                    t.list()
                    sys.stdout = orig
                    t.close()
                    job_content = s.getvalue()
                    t = open(localdict['job_path'])
                    job_checksum = zlib.adler32(t.read())
                    t.close()
                else:
                    job_content = ''
                    strip = None
                    try:
                        for directory in os.walk(localdict['job_path']):
                            if not strip:
                                strip = len(directory[0])
                            for filename in directory[2]:
                                job_content += os.path.join(
                                    directory[0][strip:], filename) + '\n'
                    except UnicodeDecodeError:
                        job_content = \
                            "UnicodeDecodeError while listing files. This means no harm to the archive's content itself."
                    job_checksum = False
                if task.type == 'immutable' or not job_path:
                    job_obj.create(cr, uid, {
                        'name': os.path.split(localdict['job_path'])[1],
                        'date': localdict['date'].strftime('%Y-%m-%d %H:%M:%S'),
                        'task_id':task.id,
                        'storage_id': target.storage_id.id,
                        'contents': job_content,
                        'checksum': job_checksum,
                        'type': task.type,
                    })
                else:
                    job_obj.write(cr, uid, job.id, {
                        'date': localdict['date'].strftime('%Y-%m-%d %H:%M:%S'),
                        'contents': job_content,
                    })
                target_obj.update_freespace(cr, uid, target)
                #delete archived files if requested
                if task.type == 'immutable' and task.delete_archived:
                    t = tarfile.open(localdict['job_path'])
                    for filename in t.getnames():
                        filename = filename.decode('utf8')
                        if filename == '.':
                            continue
                        os.unlink(os.path.join(task.from_path, filename))
                    t.close()
        finally:
            target_obj.disconnect(cr, uid, [target_id])
        return True

backup_task()

class backup_storage(osv.osv):
    """
    It's the disc that holds the created backup files.
    """
    _name = 'backup.storage'
    _description = 'Storage'

    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'uuid': fields.char('UUID', size=36, readonly=True),
        'target_ids': fields.one2many('backup.target', 'storage_id', 'Targets'),
        'job_ids': fields.one2many('backup.job', 'storage_id', 'Jobs'),
        'freespace': fields.integer('Free Space (MB)', readonly=True),
    }

    def set_identifier(self, cr, uid, target_id):
        target_obj = self.pool.get('backup.target')
        target = target_obj.browse(cr, uid, target_id)
        idpath = os.path.join(target.path, '.backup_system_identifier')
        if os.path.isfile(idpath):
            raise osv.except_osv('Error', 'The storage unit already has an identifier!')
        f = open(idpath, 'w')
        idstr = str(uuid.uuid1())
        f.write(idstr)
        f.close()
        self.write(cr, uid, target.storage_id.id, {'uuid': idstr})
        return True

    def verify_identifier(self, cr, uid, target_id):
        target_obj = self.pool.get('backup.target')
        target = target_obj.browse(cr, uid, target_id)
        idpath = os.path.join(target.path, '.backup_system_identifier')
        f = open(idpath)
        idstr = f.read()
        f.close()
        if target.storage_id.uuid != idstr:
            return False
        return True

    def action_enable(self, cr, uid, ids, *args):
        target_obj = self.pool.get('backup.target')
        for storage in self.browse(cr, uid, ids):
            target_obj.connect(cr, uid, [storage.target_ids[0].id])
            self.set_identifier(cr, uid, storage.target_ids[0].id)
            target_obj.disconnect(cr, uid, [storage.target_ids[0].id])
        return True

backup_storage()

class backup_target(osv.osv):
    """
    It's the connection and disconnection code for the disks described in
    Storage. A Storage could have more Targets if the same disk is
    connected from several machines.
    """
    _name = 'backup.target'
    _description = 'Target'

    _columns = {
        'name': fields.char('Name', size=32, required=True),
        'backup_id': fields.many2one('backup', 'Configuration', required=True),
        'storage_id': fields.many2one('backup.storage', 'Storage'),
        'connect_code': fields.text('Connect Code', required=True),
        'disconnect_code': fields.text('Disconnect Code', required=True),
        'path': fields.char('Current Path', size=64, readonly=True),
        'log': fields.text('Latest Log', readonly=True),
        'freespace': fields.related('storage_id', 'freespace', type='integer',
            relation='backup.storage', string='Free Space (MB)', readonly=True),
        'freespace_code': fields.text('Free Space Code'),
        'type': fields.selection([
            ('hdd', 'HDD'),
            ('cd', 'CD/DVD'),
        ], 'Type', required=True),
    }

    _defaults = {
        'type': lambda *a: 'hdd',
    }

    def connect(self, cr, uid, ids, *args):
        """This method commits the transaction!"""
        for target in self.browse(cr, uid, ids):
            if target.path:
                #skip already connected
                if os.path.isdir(target.path):
                    continue
                else:
                    #db is not in sync with the fs
                    self.write(cr, uid, target.id, {'path': False})
            params = {}
            for param in target.backup_id.param_ids:
                params[param.name] = param.value
            localdict = {
                'params': params,
            }
            exec target.connect_code in localdict
            if 'log' in localdict:
                self.write(cr, uid, target.id, {'log': localdict['log']})
                cr.commit()
            if not localdict['success']:
                raise osv.except_osv('Error', "Couldn't connect to %s" % target.name)
            self.write(cr, uid, target.id, {'path': localdict['path']})
            self.update_freespace(cr, uid, target, localdict['path'])
        cr.commit()
        return True

    def connect_verify(self, cr, uid, ids, *args):
        storage_obj = self.pool.get('backup.storage')
        self.connect(cr, uid, ids)
        for target in self.browse(cr, uid, ids):
            if not storage_obj.verify_identifier(cr, uid, target.id):
                self.disconnect(cr, uid, ids)
                raise osv.except_osv('Error', "The storage ID is wrong!")
        return True

    def disconnect(self, cr, uid, ids, *args):
        """This method commits the transaction!"""
        failed = {}
        for target in self.browse(cr, uid, ids):
            #skip not connected
            if not target.path:
                continue
            params = {}
            for param in target.backup_id.param_ids:
                params[param.name] = param.value
            localdict = {
                'params': params,
                'path': target.path,
            }
            exec target.disconnect_code in localdict
            if 'log' in localdict:
                self.write(cr, uid, target.id, {
                    'log': target.log + localdict['log'].decode('utf8')
                })
            if not localdict['success']:
                failed[target.id] = target.name
                #if path is not accessible, empty the path variable
                if not os.path.isdir(target.path):
                    self.write(cr, uid, target.id, {'path': False})
            else:
                self.write(cr, uid, target.id, {'path': False})
        if failed:
            cr.commit()
            raise osv.except_osv('Error',
                "Couldn't disconnect from %s" % ' '.join(failed.values()))
        cr.commit()
        return True

    def update_freespace(self, cr, uid, target, path=None):
        storage_obj = self.pool.get('backup.storage')
        if target.freespace_code:
            localdict = {
                'path': path or target.path,
            }
            exec target.freespace_code in localdict
            from tools.misc import debug
            debug(localdict['freespace'])
            if 'freespace' in localdict:
                storage_obj.write(cr, uid, target.storage_id.id,
                    {'freespace': localdict['freespace']})

backup_target()

class backup_param(osv.osv):
    """
    Parameters that can be accessed in scripts.
    """
    _name = 'backup.param'
    _description = 'Parameters'

    _columns = {
        'backup_id': fields.many2one('backup', 'Configuration', required=True),
        'name': fields.char('Name', size=32, required=True),
        'value': fields.char('Value', size=32, required=True),
    }

backup_param()

class backup_job(osv.osv):
    """
    Holds information about the archives created on disk.
    Deleting it deletes the archive, too.
    """
    _name = 'backup.job'

    _columns = {
        'name': fields.char('Filename', size=48, required=True, readonly=True),
        'date': fields.datetime('Date', required=True, readonly=True),
        'task_id': fields.many2one('backup.task', 'Task', required=True, readonly=True),
        'storage_id': fields.many2one('backup.storage', 'Storage', required=True, readonly=True),
        'contents': fields.text('Archive file list', readonly=True),
        'checksum': fields.integer('Checksum', readonly=True),
        'backup_id': fields.related('task_id', 'backup_id', type='many2one',
            relation='backup', string='Configuration', invisible=True),
        'type': fields.selection([
            ('immutable', 'Archive'),
            ('sync', 'Directory to sync'),
        ], 'Type', required=True, readonly=True),
    }

    def unlink(self, cr, uid, ids, context=None):
        target_obj = self.pool.get('backup.target')
        target_ids = set()
        jobs = self.browse(cr, uid, ids)
        for job in jobs:
            target_ids.add(job.storage_id.target_ids[0].id)
        target_ids = list(target_ids)
        target_obj.connect_verify(cr, uid, target_ids)
        #connect() commits the transaction, unlink() can only go after
        #to be transaction safe
        res = super(backup_job, self).unlink(cr, uid, ids, context=context)
        for job in jobs:
            job_path = os.path.join(job.storage_id.target_ids[0].path, job.name)
            if job.type == 'immutable':
                os.unlink(job_path)
            elif job.type == 'sync':
                shutil.rmtree(job_path)
        for target in target_obj.browse(cr, uid, target_ids):
            target_obj.update_freespace(cr, uid, target)
        target_obj.disconnect(cr, uid, target_ids)
        return res

backup_job()

class backup_run(osv.osv_memory):
    """
    Wizard to run the backup operation.
    """
    _name = 'backup.run'

    _columns = {
        'backup_id': fields.many2one('backup', 'Configuration', \
            invisible=True),
        'task_ids': fields.many2many('backup.task', 'backup_task_run', \
            'wizard_ids', 'task_ids', 'Select Tasks to Run', required=True,
            domain="[('backup_id', '=', backup_id)]"),
        'target_id': fields.many2one('backup.target', 'Target', \
            required=True, domain="[('backup_id', '=', backup_id)]"),
    }

    _defaults = {
        'backup_id': lambda self, cr, uid, c: c['active_id'],
    }

    def action_run(self, cr, uid, ids, context=None):
        task_obj = self.pool.get('backup.task')
        wiz = self.browse(cr, uid, ids[0])
        task_ids = []
        for task in wiz.task_ids:
            task_ids.append(task.id)
        task_obj.run(cr, uid, task_ids, wiz.target_id.id)
        return {'type': 'ir.actions.act_window_close'}

backup_run()