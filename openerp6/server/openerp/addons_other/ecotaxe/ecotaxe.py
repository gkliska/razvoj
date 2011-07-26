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


class product_product(osv.osv):
	_name = "product.product"
	_inherit = "product.product"
	_description = "eco participation"

	def _calc_seller_ecotaxe(self, cr, uid, ids, name, arg, context={}):
		result = {}
		for product in self.browse(cr, uid, ids, context):
			if product.seller_ids:
				result[product.id] = product.seller_ids[0].ecotaxe
			else:
				result[product.id] = 0.00
		return result




	_columns = {
		'ecotaxe' : fields.function(_calc_seller_ecotaxe, method=True, type='float', string='Eco Participation'),
	}
	_defaults = {
		'ecotaxe': lambda *a : 0.00,
	}
product_product()

class product_supplierinfo(osv.osv):
	_name = "product.supplierinfo"
	_inherit = "product.supplierinfo"
	_description = "eco participation"
	_columns = {
		'ecotaxe' : fields.float('Eco participation'),
	}
	_defaults = {
		'ecotaxe': lambda *a : 0.00,
	}
product_supplierinfo()


