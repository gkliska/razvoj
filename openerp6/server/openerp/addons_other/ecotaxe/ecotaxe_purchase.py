#!/usr/bin/env python
#coding: utf-8

# (c) 2007 Sednacom <http://www.sednacom.fr>
# authors : Gaël <gael@sednacom.fr>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from osv import osv, fields
from tools import config
from mx import DateTime

class purchase_order(osv.osv):
	def _amount_ecotaxe(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		for order in self.browse(cr, uid, ids):
			res[order.id] = 0
			for oline in order.order_line:
				res[order.id] += oline.ecotaxe_purchase * oline.product_qty
		return res	

	def _calc_amount(self, cr, uid, ids, prop, unknow_none, unknow_dict):
		res = {}
		for order in self.browse(cr, uid, ids):
			res[order.id] = 0
			for oline in order.order_line:
				res[order.id] += (oline.price_unit + oline.ecotaxe_purchase) * oline.product_qty
		return res

	def _amount_tax(self, cr, uid, ids, field_name, arg, context):
		res = super(purchase_order, self)._amount_tax(cr, uid, ids, field_name, arg, context)		
		res2 = {}
		cur_obj=self.pool.get('res.currency')
		for order in self.browse(cr, uid, ids):
			val = 0.0
			cur=order.pricelist_id.currency_id
			for line in order.order_line:
				for c in self.pool.get('account.tax').compute(cr, uid, line.taxes_id, line.ecotaxe_purchase, line.product_qty, order.partner_address_id.id, line.product_id, order.partner_id):
					val+= cur_obj.round(cr, uid, cur, c['amount'])
			res2[order.id]=cur_obj.round(cr, uid, cur, val)
		for id in ids:
			if res2.get(id,0.0):
				res[id] = res[id] + res2.get(id,0.0) 
		return res

	def _amount_untaxed(self, cr, uid, ids, field_name, arg, context):
		res = super(purchase_order, self)._amount_untaxed(cr, uid, ids, field_name, arg, context)
		return res	
	_columns = {		
		'amount_ecotaxe': fields.function(_amount_ecotaxe, method=True, string='Ecotaxe'),
		'amount_tax': fields.function(_amount_tax, method=True, string='Taxes'),
		'amount_untaxed': fields.function(_amount_untaxed, method=True, string='Untaxed Amount (with ecopart.)'),	
	}
	
	_name = "purchase.order"
	_inherit = "purchase.order"
	_description = "Purchase order with Eco participation"
	_order = "name desc"

	def action_invoice_create(self, cr, uid, ids, *args):
		res = False
		for o in self.browse(cr, uid, ids):
			il = []
			for ol in o.order_line:

				if ol.product_id:
					a = ol.product_id.product_tmpl_id.property_account_expense.id
					if not a:
						a = ol.product_id.categ_id.property_account_expense_categ.id
					if not a:
						raise osv.except_osv('Error !', 'There is no income account defined for this product: "%s" (id:%d)' % (line.product_id.name, line.product_id.id,))
				else:
					a = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category')
				il.append((0, False, {
					'name': ol.name,
					'account_id': a,
					'price_unit': ol.price_unit or 0.0,
					'quantity': ol.product_qty,
					'product_id': ol.product_id.id or False,
					'uos_id': ol.product_uom.id or False,
					'invoice_line_tax_id': [(6, 0, [x.id for x in ol.taxes_id])],
					'account_analytic_id': ol.account_analytic_id.id,
					'ecotaxe_invoice' : ol.ecotaxe_purchase,					
				}))

			a = o.partner_id.property_account_payable.id
			inv = {
				'name': o.name,
				'reference': "P%dPO%d" % (o.partner_id.id, o.id),
				'account_id': a,
				'type': 'in_invoice',
				'partner_id': o.partner_id.id,
				'currency_id': o.pricelist_id.currency_id.id,
				'address_invoice_id': o.partner_address_id.id,
				'address_contact_id': o.partner_address_id.id,
				'origin': o.name,
				'invoice_line': il,
			}
			inv_id = self.pool.get('account.invoice').create(cr, uid, inv, {'type':'in_invoice'})
			self.pool.get('account.invoice').button_compute(cr, uid, [inv_id], {'type':'in_invoice'}, set_total=True)

			self.write(cr, uid, [o.id], {'invoice_id': inv_id})
			res = inv_id
		return res

purchase_order()

class purchase_order_line(osv.osv):
	def _amount_line(self, cr, uid, ids, prop, unknow_none,unknow_dict):
		res = super(purchase_order_line, self)._amount_line(cr, uid, ids, prop, unknow_none,unknow_dict)
		for line in self.browse(cr, uid, ids):
			res[line.id] += line.ecotaxe_purchase * line.product_qty
		return res
	
	_columns = {
		'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),		
		'ecotaxe_purchase': fields.float('Ecotaxe', required=True, digits=(16,2)),
		}
	_defaults = {
		'ecotaxe_purchase': lambda *a: 0.00
	}
	_table = 'purchase_order_line'
	_name = 'purchase.order.line'
	_inherit = 'purchase.order.line'
	_description = 'Purchase Order line with Eco participation'
	
	def product_id_change(self, cr, uid, ids, pricelist, product, qty, uom, partner_id, date_order=False):
		res = super(purchase_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, partner_id, date_order)
		if product:
			res2 = self.pool.get('product.product').browse(cr, uid, product)		
			res['value']['ecotaxe_purchase']=res2.ecotaxe
		else:
			res['value']['ecotaxe_purchase']=0.00	
		return res		


purchase_order_line()
