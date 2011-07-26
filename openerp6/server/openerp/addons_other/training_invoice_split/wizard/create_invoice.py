# -*- encoding: utf-8 -*-
############################################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2011 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
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
############################################################################################

from osv import fields,osv
from tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta

import time

class create_invoice_wizard(osv.osv_memory):
    _name = 'training.create.invoice.wizard'

    def create_invoice(self, cr, uid, ids, data, context={}):
        """
        Create a draft invoice from Training Offer Invoicing
        """

        offer_invoicing_obj = self.pool.get('training.offer.invoicing')
        res_partner_obj = self.pool.get('res.partner')
        account_payment_term_obj = self.pool.get('account.payment.term')
        analytic_account_obj = self.pool.get('account.analytic.account')
        account_payment_term_obj = self.pool.get('account.payment.term')

        form = self.browse(cr, uid, ids[0])

        for id in data['active_ids']:
            invoicing = offer_invoicing_obj.browse(cr, uid, id)

            invoices = []

            partner_id = invoicing.subscription_line_id.subscription_id.partner_id.id

            if invoicing.company_id.id:
                company_id = invoicing.company_id.id
            else:
                raise osv.except_osv(_('Error'),_("Company are not avaible"))

            journal = self.pool.get('account.journal').search(cr, uid, [('type','=','sale'),('company_id','=',company_id)])

            partner = res_partner_obj.browse(cr, uid, partner_id)

            if not partner.property_account_receivable:
                raise osv.except_osv(_('Error'),_("Account Receivable Partner not avaible. Edit Partner and select an account receivable"))

            #TODO: Search account ID same code property partner. Redesign
            account_ids = self.pool.get('account.account').search(cr, uid, [('code','=',partner.property_account_receivable.code),('company_id','=',company_id)])
            if len(account_ids) == 0:
                raise osv.except_osv(_('Error'),_("Account Receivable in this company is not avaible"))

            curr_invoice = {
                'name': invoicing.subscription_line_id.name+' '+invoicing.subscription_line_id.session_id.name+' ('+invoicing.subscription_line_id.session_id.date[:10]+')',
                'partner_id': partner_id,
                'company_id': company_id,
                'journal_id': journal[0],
                'account_id': account_ids[0],
                'currency_id': invoicing.company_id.currency_id.id,
                'date_invoice': invoicing.date,
            }

            if invoicing.payment_type.id:
                curr_invoice['payment_type'] = invoicing.payment_type.id

            values = self.pool.get('account.invoice').onchange_partner_id(cr, uid, [], 'out_invoice', invoicing.subscription_line_id.subscription_id.partner_id.id)
            curr_invoice.update(values['value'])

            if len(account_ids) >0:
                curr_invoice['account_id'] = account_ids[0]

            if invoicing.subscription_line_id.subscription_id.payment_term_id:
                curr_invoice['payment_term'] = invoicing.subscription_line_id.subscription_id.payment_term_id.id

            if invoicing.subscription_line_id.subscription_id.partner_id.property_payment_term:
                pterm_list= account_payment_term_obj.compute(cr, uid,
                    invoicing.subscription_line_id.subscription_id.partner_id.property_payment_term.id, value=1,
                    date_ref=time.strftime('%Y-%m-%d'))
                if pterm_list:
                    pterm_list = [line[0] for line in pterm_list]
                    pterm_list.sort()
                    curr_invoice['date_due'] = pterm_list[-1]

            last_invoice = self.pool.get('account.invoice').create(cr, uid, curr_invoice)
            invoices.append(last_invoice)

            product = invoicing.subscription_line_id.session_id.offer_id.product_id

            taxes = product.taxes_id
            tax = self.pool.get('account.fiscal.position').map_tax(cr, uid, partner.property_account_receivable, taxes)
            account_id = product.product_tmpl_id.property_account_income.id or product.categ_id.property_account_income_categ.id

            if not account_id:
                raise osv.except_osv(_('Error'),_("Not account available for product or category product"))

            #TODO: Search account ID same code property product/category. Redesign
            account = self.pool.get('account.account').browse(cr, uid, account_id)
            account_ids = self.pool.get('account.account').search(cr, uid, [('code','=',account.code),('company_id','=',company_id)])
            if len(account_ids) == 0:
                raise osv.except_osv(_('Error'),_("Income Account in this company is not avaible"))

            curr_line = {
                'price_unit': invoicing.price,
                'quantity': 1,
                'invoice_line_tax_id': [(6,0,tax)],
                'invoice_id': last_invoice,
                'company_id': company_id,
                'name': product.name,
                'product_id': product.id,
                'uos_id': product.uom_id.id,
                'account_id': account_ids[0],
                #'account_analytic_id': ,
            }

            self.pool.get('account.invoice.line').create(cr, uid, curr_line)

            # change state invoicing
            self.pool.get('training.offer.invoicing').write(cr, uid, invoicing.id, {'invoice_id':last_invoice,'state':'inv_done'})

            # change state subscription line
            ids = self.pool.get('training.offer.invoicing').search(cr, uid, [('state','=','wait'),('subscription_line_id','=',invoicing.subscription_line_id.id)])
            if len(ids) == 0:
                self.pool.get('training.subscription.line').write(cr, uid, [invoicing.subscription_line_id.id], {'state':'done'})

                # change state subscription
                subscription = self.pool.get('training.subscription').browse(cr, uid, invoicing.subscription_line_id.subscription_id.id) #reload state value
                subscription_lines = subscription.subscription_line_ids
                subscription_done = True

                for subscription_line in subscription_lines:
                    if subscription_line.state != 'done' and subscription_done:
                        subscription_done = False

                if subscription_done:
                    self.pool.get('training.subscription').write(cr, uid, [invoicing.subscription_line_id.subscription_id.id], {'state':'done'})

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
            
        mod_id = mod_obj.search(cr, uid, [('name', '=', 'action_invoice_tree1')])[0]
        res_id = mod_obj.read(cr, uid, mod_id, ['res_id'])['res_id']
        act_win = act_obj.read(cr, uid, res_id, [])
        act_win['domain'] = [('id','in',invoices),('type','=','out_invoice')]
        act_win['name'] = _('Invoices')

        return act_win

create_invoice_wizard()
