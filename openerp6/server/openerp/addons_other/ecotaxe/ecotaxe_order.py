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

class sale_order_line(osv.osv):

	def _amount_line_net(self, cr, uid, ids, field_name, arg, context):
		res = super(sale_order_line, self)._amount_line_net(cr, uid, ids, field_name, arg, context)	
		for line in self.browse(cr, uid, ids):
			res[line.id] += line.ecotaxe_order
		return res

	def _amount_line(self, cr, uid, ids, field_name, arg, context):
		res = super(sale_order_line, self)._amount_line(cr, uid, ids, field_name, arg, context)
		for line in self.browse(cr, uid, ids):
			res[line.id] += line.ecotaxe_order * line.product_uom_qty
		return res


	_name = "sale.order.line"
	_inherit = "sale.order.line"
	_description = "eco participation"

	_columns = {
		'ecotaxe_order' : fields.float('Eco part'),
		'price_net': fields.function(_amount_line_net, method=True, string='Net Price', digits=(16, int(config['price_accuracy']))),
		'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
		}
	_defaults = {
		'ecotaxe_order': lambda *a : 0.00,
	}


	def product_id_change(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False):
		res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id, lang, update_tax, date_order)
		if product:
			res2 = self.pool.get('product.product').browse(cr, uid, product)		
			res['value']['ecotaxe_order']=res2.ecotaxe
		else:
			res['value']['ecotaxe_order']=0.00	
		return res
	
	def invoice_line_create(self, cr, uid, ids, context={}):
		def _get_line_qty(line):
			if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
				return line.product_uos_qty or line.product_uom_qty
			else:
				return self.pool.get('mrp.procurement').quantity_get(cr, uid, line.procurement_id.id, context)
		create_ids = []
		for line in self.browse(cr, uid, ids, context):
			if not line.invoiced:
				if line.product_id:
					a =  line.product_id.product_tmpl_id.property_account_income.id
					if not a:
						a = line.product_id.categ_id.property_account_income_categ.id
					if not a:
						raise osv.except_osv('Error !', 'There is no income account defined for this product: "%s" (id:%d)' % (line.product_id.name, line.product_id.id,))
				else:
					a = self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ', 'product.category', context=context)
				uosqty = _get_line_qty(line)
				uos_id = (line.product_uos and line.product_uos.id) or line.product_uom.id
				pu = line.price_unit
				if line.product_uos_qty:
					pu = round(pu * line.product_uom_qty / line.product_uos_qty, int(config['price_accuracy']))
				inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
					'name': line.name,
					'account_id': a,
					'price_unit': pu,
					'quantity': uosqty,
					'discount': line.discount,
					'uos_id': uos_id,
					'product_id': line.product_id.id or False,
					'invoice_line_tax_id': [(6,0,[x.id for x in line.tax_id])],
					'note': line.notes,
					'account_analytic_id': line.order_id.project_id.id,
					'ecotaxe_invoice':line.ecotaxe_order
				})
				cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%d,%d)', (line.id, inv_id))
				self.write(cr, uid, [line.id], {'invoiced':True})
				create_ids.append(inv_id)
		return create_ids				

sale_order_line()

class sale_order(osv.osv):
	_name = "sale.order"
	_inherit = "sale.order"
	_description = "eco participation"

	def _amount_ecotaxe(self, cr, uid, ids, field_name, arg, context):
		res2 = {}
		cur_obj=self.pool.get('res.currency')
		for sale in self.browse(cr, uid, ids):
			res2[sale.id] = 0.0
			for line in sale.order_line:				
				res2[sale.id] += line.ecotaxe_order * line.product_uom_qty
			cur = sale.pricelist_id.currency_id
			res2[sale.id] = cur_obj.round(cr, uid, cur, res2[sale.id])
		return res2

	

	def _amount_tax(self, cr, uid, ids, field_name, arg, context):
		res=super(sale_order, self)._amount_tax(cr, uid, ids, field_name, arg, context)
		res2={}
		cur_obj=self.pool.get('res.currency')
		for sale in self.browse(cr, uid, ids):
			val = 0.0
			cur=sale.pricelist_id.currency_id
			for line in sale.order_line:
				for c in self.pool.get('account.tax').compute(cr, uid, line.tax_id, line.ecotaxe_order, line.product_uom_qty, sale.partner_invoice_id.id, line.product_id, sale.partner_id):
					val+= cur_obj.round(cr, uid, cur, c['amount'])
			res2[sale.id]=cur_obj.round(cr, uid, cur, val)
		for id in ids:
			if res2.get(id,0.0):
				res[id] = res[id] + res2.get(id,0.0) 
		return res

	

	



	_columns = {
		'amount_ecotaxe': fields.function(_amount_ecotaxe, method=True, string='Ecotaxe'),
		'amount_tax': fields.function(_amount_tax, method=True, string='Taxes'),		
	}
sale_order()

