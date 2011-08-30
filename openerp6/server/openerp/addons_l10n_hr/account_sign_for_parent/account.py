# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: account_storno
#    Author: Goran Kliska,  gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#    Contributions: 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import netsvc
import pooler
from osv import fields, osv
import decimal_precision as dp
from tools.translate import _


from tools.misc import profile
@profile('output.data')
class account_account(osv.osv):
    _inherit = "account.account"
    
    #unchanged
    def _get_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []

            if record.child_consol_ids:
                for acc in record.child_consol_ids:
                    if acc.id not in result[record.id]:
                        result[record.id].append(acc.id)
        return result

    #unchanged
    def _get_children_and_consol(self, cr, uid, ids, context=None):
        #this function search for all the children and all consolidated children (recursively) of the given account ids
        ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)], context=context)
        ids3 = []
        for rec in self.browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3

    def __compute_sign(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        """ compute the balance, debit and/or credit for the provided account ids
        Arguments:
        `ids`: account ids
        `field_names`: the fields to compute (a list of any of
                       'balance', 'debit' and 'credit')
        `arg`: unused fields.function stuff
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        """
        mapping = {
            'balance': "COALESCE(SUM(l.debit),0) " \
                       "- COALESCE(SUM(l.credit), 0) as balance",
            'debit': "COALESCE(SUM(l.debit), 0) as debit",
            'credit': "COALESCE(SUM(l.credit), 0) as credit"
        }
        field_names=['debit', 'credit'] # for balance we need debit and credit

        #get all the necessary accounts
        children_and_consolidated = self._get_children_and_consol(cr, uid, ids, context=context)
        #compute for each account the debit/credit from the move lines
        accounts = {}
        res = {}
        if children_and_consolidated:
            aml_query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)
            #TODO OPTIMIZE
            #l.state <> 'draft' 
            # AND l.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (1))   
            # AND l.move_id IN (SELECT id FROM account_move WHERE account_move.state = 'posted') => l.state="posted"
            wheres = [""]
            if query.strip():
                wheres.append(query.strip())
            if aml_query.strip():
                wheres.append(aml_query.strip())
            filters = " AND ".join(wheres)
            self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Filters: %s'%filters)
            # TO DO OPTIMIZE--log-level=debug_sql
            # IN might not work ideally in case there are too many
            # children_and_consolidated, in that case join on a values() e.g.:
            # SELECT l.account_id as id FROM account_move_line l
            # INNER JOIN (VALUES (id1), (id2), (id3), ...) AS tmp (id)
            # ON l.account_id = tmp.id
            # or make _get_children_and_consol return a query and join on that
            request = ("SELECT l.account_id as id, " +\
                       ', '.join(map(mapping.__getitem__, field_names)) +
                       " FROM account_move_line l" \
                       " WHERE l.account_id IN %s " \
                            + filters +
                       " GROUP BY l.account_id")
            params = (tuple(children_and_consolidated),) + query_params
            cr.execute(request, params)
            self.logger.notifyChannel('addons.'+self._name, netsvc.LOG_DEBUG,
                                      'Status: %s'%cr.statusmessage)


            for res in cr.dictfetchall(): 
                accounts[res['id']] = res 

            # consolidate accounts with direct children
            # TODO: check currency
            children_and_consolidated.reverse()
            brs = list(self.browse(cr, uid, children_and_consolidated, context=context))
            sums = dict([(id, {'debit': accounts.get(id, {}).get('debit', 0.0),
                               'credit': accounts.get(id, {}).get('credit', 0.0),
                              }) for id in children_and_consolidated])
            while brs:
                current = brs[0]
                brs.pop(0)
                if current.child_id:
                    sums[current.id]['debit']  += sum(sums[c.id]['debit'] 
                                                      * c.parent_sign_debit for c in current.child_id)
                    sums[current.id]['credit'] += sum(sums[c.id]['credit']
                                                      * c.parent_sign_credit for c in current.child_id)

            res = dict([(id, {'debit'  : sums.get(id,{}).get('debit' , 0.0),
                              'credit' : sums.get(id,{}).get('credit', 0.0),
                              'balance': sums.get(id,{}).get('debit', 0.0)
                                        - sums.get(id,{}).get('credit', 0.0),
                              }) for id in ids])

        else:
            for id in ids:
                res[id] = 0.0
        return res

    _columns = {
        #new fields         
        'parent_sign_debit' : fields.float('Debit Coefficent for parent', required=True, help='You can specify here the coefficient that will be used when consolidating the debit amount of this account into its parent. For example, set 1/-1 if you want to add/substract it.'),
        'parent_sign_credit': fields.float('Credit Coefficent for parent', required=True, help='You can specify here the coefficient that will be used when consolidating the credit amount of this account into its parent. For example, set 1/-1 if you want to add/substract it.'),
        # redeclaration of fields because of private __compute() func  
        'balance': fields.function(__compute_sign, digits_compute=dp.get_precision('Account'), string='Balance', multi='balance'),
        'credit': fields.function(__compute_sign, digits_compute=dp.get_precision('Account'), string='Credit', multi='balance'),
        'debit': fields.function(__compute_sign, digits_compute=dp.get_precision('Account'), string='Debit', multi='balance'),
    }

    _defaults = {
        'parent_sign_debit': 1.0,
        'parent_sign_credit': 1.0,
    }
    
 
 
account_account()  

