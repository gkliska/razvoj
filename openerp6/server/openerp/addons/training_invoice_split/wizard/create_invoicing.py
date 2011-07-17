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

class create_invoicing_wizard(osv.osv_memory):
    _name = 'training.create.invoicing.wizard'

    def _invoice_ids(self, cr, uid, context={}):
        result = []
        result.append( ('default',_('Default Payment')) )
        if context['active_model'] == 'training.subscription.line':
            subscription_line_id = context['active_id']

            subscription_line = self.pool.get("training.subscription.line").browse(cr, uid, context['active_id'])
            for invoice in subscription_line.session_id.offer_id.invoice_ids:
                result.append( (invoice.id,invoice.name) )
        return result

    _columns = {
        'invoice': fields.selection(_invoice_ids, 'Invoicing Type', method=True, required=True),
    }

    def create_invoicing(self, cr, uid, ids, data, context={}):
        """
        Create list of invoices history from Offer Payment
        Invoices will create from training.offer.invoicing
        All invoices will create draft state and add new Request Training Manager Users
        """

        form = self.browse(cr, uid, ids[0])
        subscription_line_obj = self.pool.get("training.subscription.line")
        subscription_invoicing_obj = self.pool.get("training.offer.invoicing")

        subscription_line_ids = subscription_line_obj.search(cr, uid, [('id','=',data['active_id'])])
        subscription_line = subscription_line_obj.browse(cr, uid, subscription_line_ids[0])

        offer_invoicings = []

        if form.invoice != 'default':
            offer_invoice_obj = self.pool.get("training.offer.invoice")
            offer_invoice_line_obj = self.pool.get("training.offer.invoice.line")

            offer_invoice = offer_invoice_obj.browse(cr, uid, form.invoice)
            offer_invoice_line_ids = offer_invoice_line_obj.search(cr, uid, [('invoice_id','=',form.invoice)], order='sequence')

            for offer_invoice_line in offer_invoice_line_obj.browse(cr, uid, offer_invoice_line_ids):
                if offer_invoice_line.reference_date == 'session_date':
                    date = subscription_line.session_id.date[:10] #session date
                else:
                    date = subscription_line.subscription_id.create_date[:10] #subscription date

                date = (datetime.strptime(date, '%Y-%m-%d') + relativedelta(days=offer_invoice_line.days))

                if offer_invoice_line.company_id.id:
                    company_id = offer_invoice_line.company_id.id
                else:
                    raise osv.except_osv(_('Error'),_("Company are not avaible"))

                values = {
                    'date': date,
                    'price': offer_invoice_line.price,
                    'subscription_line_id': data['active_id'],
                    'invoice_type': offer_invoice.id,
                    'payment_type': offer_invoice_line.payment_type.id,
                    'seq': offer_invoice_line.sequence,
                    'company_id': company_id,
                }
#                subscription_invoicing_ids = subscription_invoicing_obj.search(cr, uid, [('subscription_line_id','=',data['active_id']),('invoice_code','=',form.invoice),('seq','=',offer_invoice_line.sequence)])

                values['state'] = 'wait'
                offer_invoicing = self.pool.get("training.offer.invoicing").create(cr, uid, values)
                offer_invoicings.append(offer_invoicing)

        else: #default invoice
            pricelist = subscription_line.price_list_id.id
            price = self.pool.get('product.pricelist').price_get(cr,uid,[pricelist], subscription_line.session_id.offer_id.product_id.id, 1.0, context=context)[pricelist]

            subscription_invoicing_ids = subscription_invoicing_obj.search(cr, uid, [('subscription_line_id','=',data['active_id']),('invoice_code','=',form.invoice)])

            user = self.pool.get('res.users').browse(cr, uid, uid, context)

            journal = self.pool.get('account.journal').search(cr, uid, [('type','=','sale'),('company_id','=',user.company_id.id)])
            if journal:
                company_id = user.company_id.id
            else:
                company_ids = self.pool.get('res.company').search(cr, uid, [('parent_id','=',user.company_id.id)])
                if len(company_ids) > 0:
                    company_id = company_ids[0]
                else:
                    raise osv.except_osv(_('Error'),_("Company not available. Configure Parent Company"))

            values = {
                'date': time.strftime('%Y-%m-%d'),
                'price': price,
                'subscription_line_id': data['active_id'],
                'invoice_type':'',
                'seq': 10,
                'company_id': company_id,
            }

            values['state'] = 'wait'
            offer_invoicing = self.pool.get("training.offer.invoicing").create(cr, uid, values)
            offer_invoicings.append(offer_invoicing)

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
            
        mod_id = mod_obj.search(cr, uid, [('name', '=', 'action_training_offer_invoicing_action')])[0]
        res_id = mod_obj.read(cr, uid, mod_id, ['res_id'])['res_id']
        act_win = act_obj.read(cr, uid, res_id, [])
        act_win['domain'] = [('id','in',offer_invoicings)]
        act_win['name'] = _('Training Offer Invoicing')

        return act_win

create_invoicing_wizard()
