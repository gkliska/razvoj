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

from osv import osv, fields
from tools.translate import _

import decimal_precision as dp

class training_offer_invoice(osv.osv):
    _name = "training.offer.invoice"
    _description = "Training Offer Invoice"

    def _amount_total(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        res = {}
        invoice_line_obj = self.pool.get('training.offer.invoice.line')
        for invoice in self.browse(cr, uid, ids, context=context):
            amount_total = 0.0
            invoice_line_ids = invoice_line_obj.search(cr, uid, [('invoice_id','=',invoice.id)])
            if len(invoice_line_ids) > 0:
                for invoice_line_id in invoice_line_ids:
                    pay = invoice_line_obj.browse(cr, uid, invoice_line_id)
                    amount_total += pay.price
                res[invoice.id] = amount_total
        return res

    _columns = {
        'name': fields.char('Name', size=32, required=True, translate=True),
        'active': fields.boolean('Active'),
        'invoice_line_ids': fields.one2many('training.offer.invoice.line', 'invoice_id', string='Invoice'),
        'amount_total': fields.function(_amount_total, string="Total Amount", method=True, type='float', digits_compute=dp.get_precision('Account')),
        'offer_id': fields.many2one('training.offer','Offer'),
    }

    _defaults = {
        'active': lambda *a: 1,
    }

training_offer_invoice()

class training_offer_invoice_line(osv.osv):
    _name = "training.offer.invoice.line"
    _description = "Training Offer Invoice Line"
    _rec_name = 'reference_date'

    _columns = {
        'reference_date': fields.selection([('session_date','Session Date'),('subscription_date','Subscription Date')],'Reference Date'),
        'days': fields.integer('Days'),
        'price': fields.float('Price', required=True, digits_compute= dp.get_precision('Account')),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when create Account Invoice."),
        'invoice_id': fields.many2one('training.offer.invoice','Payment'),
        'company_id': fields.many2one('res.company', 'Company', select=1, required=True),
        'payment_type': fields.many2one('payment.type','Payment Type'),
    }

    _order = 'sequence, id desc'

    _defaults = {
        'sequence': 10,
        'reference_date': 'session_date',
    }

training_offer_invoice_line()

class training_offer_invoicing(osv.osv):
    _name = "training.offer.invoicing"
    _description = "Training Offer Invoicing History"
    _rec_name = 'subscription_line_id'

    _columns = {
        'date': fields.date('Date', required=True),
        'price': fields.float('Price', required=True, digits_compute= dp.get_precision('Account')),
        'state': fields.selection([('wait','Waiting'),('inv','Ready to be invoiced'),('inv_done','Invoiced'),('error','Error')],'State', readonly=True),
        'company_id': fields.many2one('res.company', 'Company', select=1, required=True),
        'invoice_id': fields.many2one('account.invoice','Invoice', readonly=True),
        'subscription_line_id': fields.many2one('training.subscription.line','Subscription Line', readonly=True),
        'invoice_type': fields.many2one('training.offer.invoice','Offer Invoicing', readonly=True),
        'payment_type': fields.many2one('payment.type','Payment Type'),
        'seq': fields.integer('Sequence', readonly=True),
        'partner': fields.related('subscription_line_id', 'partner_id', type='many2one', relation='res.partner', string='Partner'),
    }

    _defaults = {
        'state': 'wait',
    }

    def unlink(self, cr, uid, vals, context):
        invoicing_ids = self.read(cr, uid, vals, ['state'])
        unlink_ids = []
        for s in invoicing_ids:
            if s['state'] in ['wait']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid action !'), _('Only wait invoicing could be deleted !'))
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)

training_offer_invoicing()

#========Inherits=========

class training_offer(osv.osv):
    _inherit = 'training.offer'

    _columns = {
        'invoice_ids': fields.one2many('training.offer.invoice', 'offer_id', 'Payments'),
    }

training_offer()

class training_subscription_line(osv.osv):
    _inherit = 'training.subscription.line'

    _columns = {
        'invoicing_ids': fields.one2many('training.offer.invoicing', 'subscription_line_id', 'Invoicing'),
    }

training_subscription_line()
