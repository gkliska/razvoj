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

class account_invoice(osv.osv):
	def _amount_ecotaxe(self, cr, uid, ids, name, args, context={}):
		id_set=",".join(map(str,ids))
		cr.execute("SELECT s.id,COALESCE(SUM(l.ecotaxe_invoice*l.quantity))::decimal(16,2) AS amount FROM account_invoice s LEFT OUTER JOIN account_invoice_line l ON (s.id=l.invoice_id) WHERE s.id IN ("+id_set+") GROUP BY s.id ")
		res=dict(cr.fetchall())
		return res

	def _amount_untaxed(self, cr, uid, ids, name, args, context={}):
		res = super(account_invoice, self)._amount_untaxed(cr, uid, ids, name, args, context)
		res1 =  self._amount_ecotaxe( cr, uid, ids, name, args, context)
		for id in ids:
			if res1.get(id,0.0): 
				res[id] = res[id] + res1.get(id,0.0) 				
		return res

	
	_name = "account.invoice"
	_inherit = "account.invoice"
	_description = 'eco participation Invoice'
	_columns = {
		'amount_ecotaxe': fields.function(_amount_ecotaxe, method=True, digits=(16,2),string='Eco Part.'),
		'amount_untaxed': fields.function(_amount_untaxed, method=True, string='Untaxed Amount (with ecopart.)', store=True),
	}
account_invoice()

class account_invoice_line(osv.osv):

	def _amount_line(self, cr, uid, ids, prop, unknow_none,unknow_dict):
		res = super(account_invoice_line, self)._amount_line(cr, uid, ids, prop, unknow_none,unknow_dict)
		for line in self.browse(cr, uid, ids):
			res[line.id] += line.ecotaxe_invoice * line.quantity 
		return res

	_name = "account.invoice.line"
	_inherit = "account.invoice.line"
	_description = "Eco participation"

	_columns = {
		'ecotaxe_invoice': fields.float('Eco Part'),
		'price_subtotal': fields.function(_amount_line, method=True, string='Subtotal'),
		}
	def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, price_unit=False, address_invoice_id=False, context={}):
		res = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qt, name, type, partner_id, price_unit, address_invoice_id, context)
		res2 = self.pool.get('product.product').browse(cr, uid, product)		
		res['value']['ecotaxe_invoice']=res2.ecotaxe
		print res
		return res


account_invoice_line()


class account_invoice_tax(osv.osv):
	_name = "account.invoice.tax"
	_description = "Invoice Tax"
	_inherit = "account.invoice.tax"

	def compute(self, cr, uid, invoice_id):	
		tax_grouped = {}
		tax_obj = self.pool.get('account.tax')
		cur_obj = self.pool.get('res.currency')
		inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
		cur = inv.currency_id

		for line in inv.invoice_line:
			for tax in tax_obj.compute(cr, uid, line.invoice_line_tax_id, (line.price_unit* (1-(line.discount or 0.0)/100.0)+line.ecotaxe_invoice), line.quantity, inv.address_invoice_id.id, line.product_id, inv.partner_id):
				val={}
				val['invoice_id'] = inv.id
				val['name'] = tax['name']
				val['amount'] = cur_obj.round(cr, uid, cur, tax['amount'])
				val['manual'] = False
				val['sequence'] = tax['sequence']
				val['base'] = tax['price_unit'] * line['quantity'] * (1-(line.discount or 0.0)/100.0)

				if inv.type in ('out_invoice','in_invoice'):
					val['base_code_id'] = tax['base_code_id']
					val['tax_code_id'] = tax['tax_code_id']
					val['base_amount'] = val['base'] * tax['base_sign']
					val['tax_amount'] = val['amount'] * tax['tax_sign']
					val['account_id'] = tax['account_collected_id'] or line.account_id.id
				else:
					val['base_code_id'] = tax['ref_base_code_id']
					val['tax_code_id'] = tax['ref_tax_code_id']
					val['base_amount'] = val['base'] * tax['ref_base_sign']
					val['tax_amount'] = val['amount'] * tax['ref_tax_sign']
					val['account_id'] = tax['account_paid_id'] or line.account_id.id

				key = (val['tax_code_id'], val['base_code_id'], val['account_id'])
				if not key in tax_grouped:
					tax_grouped[key] = val
				else:
					tax_grouped[key]['amount'] += val['amount']
					tax_grouped[key]['base'] += val['base']
					tax_grouped[key]['base_amount'] += val['base_amount']
					tax_grouped[key]['tax_amount'] += val['tax_amount']

		return tax_grouped
account_invoice_tax()

