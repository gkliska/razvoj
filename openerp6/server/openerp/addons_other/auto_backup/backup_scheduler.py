# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

from osv import fields,osv
import xmlrpclib
import socket
import os
import time
import base64
import tools
import netsvc

logger = netsvc.Logger()

def execute(connector, method, *args):
    res = False
    try:        
        res = getattr(connector,method)(*args)
    except socket.error,e:        
            raise e
    return res

addons_path = tools.config['addons_path'] + '/auto_backup/DBbackups'

class db_backup(osv.osv):
    _name = 'db.backup'
    
    def get_db_list(self, cr, user, ids, host='localhost', port='8069', context={}):
        uri = 'http://' + host + ':' + port
        conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
        db_list = execute(conn, 'list')
        return db_list
        
    def get_addons_path(selfcr, user, context={}):
        addons_path = tools.config['addons_path'] + '/auto_bkp/DBbackups'
        return addons_path
    
    _columns = {
                    'host' : fields.char('Host', size=100, required='True'),
                    'port' : fields.char('Port', size=10, required='True'),
                    'name' : fields.char('Database', size=100, required='True',help='Database you want to schedule backups for'),
                    'bkp_dir' : fields.char('Backup Directory', size=100, help='Absolute path for storing the backups', required='True')
                }
    
    _defaults = {
                    'bkp_dir' : lambda *a : addons_path,
                    'host' : lambda *a : 'localhost',
                    'port' : lambda *a : '8069'
                 }
    
    def _check_db_exist(self, cr, user, ids):
        for rec in self.browse(cr,user,ids):
            db_list = self.get_db_list(cr, user, ids, rec.host, rec.port)
            if rec.name in db_list:
                return True
        return False
    _constraints = [
                    (_check_db_exist, 'Error ! No such database exist.', [])
                    ]
    
    def schedule_backup(self, cr, user, context={}):
        conf_ids= self.search(cr, user, [])
        confs = self.browse(cr,user,conf_ids)
        for rec in confs:
            db_list = self.get_db_list(cr, user, [], rec.host, rec.port)
            if rec.name in db_list:
                try:
                    if not os.path.isdir(rec.bkp_dir):
                        os.makedirs(rec.bkp_dir)
                except:
                    raise
                bkp_file='%s_%s.sql' % (rec.name, time.strftime('%Y%m%d_%H_%M_%S'))
                file_path = os.path.join(rec.bkp_dir,bkp_file)
                fp = open(file_path,'wb')
                uri = 'http://' + rec.host + ':' + rec.port
                conn = xmlrpclib.ServerProxy(uri + '/xmlrpc/db')
                bkp=''
                try:
                    bkp = execute(conn, 'dump', 'admin', rec.name)
                except:
                    logger.notifyChannel('backup', netsvc.LOG_INFO, "Could'nt backup database %s. Bad database administrator password for server running at http://%s:%s" %(rec.name, rec.host, rec.port))
                    continue
                bkp = base64.decodestring(bkp)
                fp.write(bkp)
                fp.close()
            else:
                logger.notifyChannel('backup', netsvc.LOG_INFO, "database %s doesn't exist on http://%s:%s" %(rec.name, rec.host, rec.port))
                
db_backup()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
