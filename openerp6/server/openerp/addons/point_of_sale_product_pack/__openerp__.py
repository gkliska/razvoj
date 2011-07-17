# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
#
#    Based on the work of nan_product_pack:
#    Copyright (c) 2009 Àngel Àlvarez - NaN  (http://www.nan-tic.com) All Rights Reserved.
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
##############################################################################

{
	"name" : "Point of Sale Product Pack",
	"version" : "0.1",
	"description" : """
Allows adding product packs (collection of other products) in the point of sale. If such a product is added in a point of sale order, all the products of the pack will be added automatically (when storing the order) as children of the pack product.
        """,
	"author" : "Zikzakmedia SL",
	"website" : "http://www.zikzakmedia.com",
	"depends" : [ 
		'nan_product_pack',
		'point_of_sale',
	], 
	"category" : "Custom Modules",
	"init_xml" : [],
	"demo_xml" : [],
	"update_xml" : [
	],
	"active": False,
	"installable": True
}
