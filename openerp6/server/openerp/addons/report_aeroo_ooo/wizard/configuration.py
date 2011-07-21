##############################################################################
#
# Copyright (c) 2008-2010 SIA "KN dati". (http://kndati.lv) All Rights Reserved.
#                    General contacts <info@kndati.lv>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import wizard
from osv import osv
import netsvc
import pooler
import tempfile
import tools
from report_aeroo_ooo.DocumentConverter import DocumentConverter, DocumentConversionException
from report_aeroo_ooo.report import OpenOffice_service
import ir

_form = '''<?xml version="1.0"?>
<form string="OpenOffice.org connection">
    <field name="host" colspan="4"/>
    <field name="port" colspan="4"/>
</form>'''

_error_form = '''<?xml version="1.0"?>
<form string="Error">
    <label string="Connection to OpenOffice.org instance was not established or convertion to PDF unsuccessful!" colspan="2"/>
    <separator string="Details" colspan="4"/>
    <field name="error" colspan="2" nolabel="1"/>
</form>'''

_done_form = '''<?xml version="1.0"?>
<form string="OpenOffice.org connection successfully">
    <label string="Connection to the OpenOffice.org instance was successfully established and PDF convertion is working." colspan="2"/>
</form>'''

_fields = {
    'host': {'string':'Host', 'type':'char', 'size':128, 'required':True, 'default':'localhost'},
    'port': {'string':'Port', 'type':'integer', 'required':True, 'default':8100},
}

_error_fields = {
    'error': {'string':'Details', 'type':'text','readonly':True},
}

class aeroo_config_wizard(wizard.interface):

    def _load_data(self, cr, uid, data, ctx={}):
        pool = pooler.get_pool(cr.dbname)
        obj = pool.get('oo.config')
        id = obj.search(cr, uid, [])
        if len(id) != 0:
            config = obj.read(cr, uid, id, {})[0]
            if len(config) > 1:
                data['form']['host'] = config['host']
                data['form']['port'] = config['port']
            form = data['form']
        return data['form']

    def _save_data(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        obj = pool.get('oo.config')
        id = obj.search(cr, uid, [])
        if id:
            obj.write(cr, uid, id, data['form'])
        else:
            obj.create(cr, uid, data['form'])

        return {}

    def _get_error_data(self, cr, uid, data, ctx={}):
        data['form']['error'] = ctx['error_text']
        return data['form']

    def _check(self, cr, uid, data, context):
        try:
            fp = tools.file_open('report_aeroo_ooo/test_temp.odt', mode='rb')
            file_data = fp.read()
            DC = netsvc.Service._services.setdefault('openoffice', \
                    OpenOffice_service(cr, data['form']['host'], data['form']['port']))
            DC.putDocument(file_data)
            DC.saveByStream()
            fp.close()
            DC.closeDocument()
            del DC
            return 'done'
        except DocumentConversionException, e:
            netsvc.Service.remove('openoffice')
            context['error_text'] = str(e)#e.message
            return 'error'
        except Exception, e:
            context['error_text'] = str(e)#e.Message
            return 'error'

    states = {
        'init': {
            'actions': [_load_data],
            'result': {'type': 'form', 'arch':_form, 'fields':_fields, 'state':[('end','Cancel', 'gtk-cancel'),('check','Connect', 'gtk-ok', True)]}
        },
        'check': {
            'actions': [_save_data],
            'result': {'type':'choice','next_state':_check}
        },
        'error': {
            'actions': [_get_error_data],
            'result': {'type': 'form', 'arch':_error_form, 'fields':_error_fields, 'state':(('end','Close', '', True),)},
        },
        'done': {
            'actions': [],
            'result': {'type': 'form', 'arch':_done_form, 'fields':{}, 'state':(('end','Ok', 'gtk-ok', True),)},
        }
    }
aeroo_config_wizard('aeroo.config_wizard')

