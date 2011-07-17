# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
#    Written by: Cloves J. G. de Almeida <cjalmeida@gvmail.br>
#    Using code written by Tiny Srpl.
#
##############################################################################


from osv import osv, fields
import pooler

class account_chart_orthogonal_wizard(osv.osv_memory):
    
    _name = 'account.chart.orthogonal.wizard'
    
    _columns = {
        'fiscalyear' : fields.many2one('account.fiscalyear', 'Fiscal Year', required=False),
        'target_move' : fields.selection([('all','All Entries'),('posted','All Posted Entries')], 'Target Moves', required=True),
        'analytic_id' : fields.many2one('account.analytic.account', 'Analytic Account', required=False, 
                                        help='The moves not related to this analytic account will be filtered out.')
    }
    
    _defaults = {
        'fiscalyear' : lambda self, cr, uid, c : pooler.get_pool(cr.dbname).get('account.fiscalyear').find(cr, uid),
        'target_move' : lambda *a: 'all'          
    }
    
    def action_open(self, cr, uid, ids, context={}):
        for _id in ids:
            data = self.read(cr, uid, [_id])[0]
            mod_obj = pooler.get_pool(cr.dbname).get('ir.model.data')
            act_obj = pooler.get_pool(cr.dbname).get('ir.actions.act_window')

            result = mod_obj._get_id(cr, uid, 'account', 'action_account_tree')
            id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
            result = act_obj.read(cr, uid, [id], context=context)[0]
            result['context'] = str({'fiscalyear': data['fiscalyear'],'state':data['target_move'], 'analytic_id':data['analytic_id']})
        if data['fiscalyear']:
            result['name']+=':'+pooler.get_pool(cr.dbname).get('account.fiscalyear').read(cr,uid,[data['fiscalyear']])[0]['code']
        return result
    
    def action_cancel(self, cr, uid, ids, context={}):
        pass

account_chart_orthogonal_wizard()

    
class account_move_line(osv.osv):
    _name="account.move.line"
    _inherit="account.move.line"
    _description = "Entry lines"

    def _query_get(self, cr, uid, obj='l', context={}):
        query = super(account_move_line, self)._query_get(cr, uid, obj, context)
        if context.get('analytic_id',False):
            query += ' AND (id in (select move_id from account_analytic_line where account_id = ' + str(context['analytic_id']) + ') or analytic_account_id = ' + str(context['analytic_id']) + ') '  
        return query

account_move_line()

