##############################################################################
#
# Copyright (c) 2008-2011 Alistek, SIA. (http://www.alistek.com) All Rights Reserved.
#                    General contacts <info@alistek.com>
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
import pooler
import ir
from tools.translate import _

special_reports = [
    'printscreen.list'
]

class report_actions_wizard(wizard.interface):
    '''
    Add Print Button
    '''
    form = '''<?xml version="1.0"?>
    <form string="Add Print Button">
        <!--<field name="print_button"/>-->
        <field name="open_action"/>
    </form>'''

    exist_form = '''<?xml version="1.0"?>
    <form string="Add Print Button">
        <label string="Report Action already exist for this report."/>
    </form>'''

    exception_form = '''<?xml version="1.0"?>
    <form string="Add Print Button">
        <label string="Can not be create print button for the Special report."/>
    </form>'''

    done_form = '''<?xml version="1.0"?>
    <form string="Remove print button">
        <label string="The print button is successfully added"/>
    </form>'''

    fields = {
        #'print_button': {'string': 'Add print button', 'type': 'boolean', 'default': True, 'help':'Add action to menu context in print button.'},
        'open_action': {'string': 'Open added action', 'type': 'boolean', 'default': False},
    }

    def _do_action(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        report = pool.get(data['model']).browse(cr, uid, data['id'], context=context)
        #if data['form']['print_button']:
        res = ir.ir_set(cr, uid, 'action', 'client_print_multi', report.report_name, [report.model], 'ir.actions.report.xml,%d' % data['id'], isobject=True)
        #else:
	    #    res = ir.ir_set(cr, uid, 'action', 'client_print_multi', report.report_name, [report.model,0], 'ir.actions.report.xml,%d' % data['id'], isobject=True)
        return {'value_id':res[0]}

    def _check(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        report = pool.get(data['model']).browse(cr, uid, data['id'], context=context)
        if report.report_name in special_reports:
            return 'exception'
        ids = pool.get('ir.values').search(cr, uid, [('value','=',report.type+','+str(data['id']))])
        if not ids:
	        return 'add'
        else:
	        return 'exist'

    def _action_open_window(self, cr, uid, data, context):
        form=data['form']
        if not form['open_action']:
            return {}
        return {
            'domain':"[('id','=',%d)]" % (form['value_id']),
            'name': _('Client Actions Connections'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'ir.values',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
    
    states = {
        'init': {
			'actions': [],
			'result': {'type':'choice','next_state':_check}
        },
        'add': {
            'actions': [],
            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state': (('end', _('_Cancel')), ('process', _('_Ok')))},
        },
        'exist': {
            'actions': [],
            'result': {'type': 'form', 'arch': exist_form, 'fields': {}, 'state': (('end', _('_Close')),)},
        },
        'exception': {
            'actions': [],
            'result': {'type': 'form', 'arch': exception_form, 'fields': {}, 'state': (('end', _('_Close')),)},
        },
        'process': {
            'actions': [_do_action],
            'result': {'type': 'state', 'state': 'done'},
        },
        'done': {
            'actions': [],
            'result': {'type': 'form', 'arch': done_form, 'fields': {}, 'state': (('exit', _('_Close')),)},
        },
        'exit': {
            'actions': [],
            'result': {'type': 'action', 'action': _action_open_window, 'state': 'end'},
        },
    }
report_actions_wizard('aeroo.report_actions')

