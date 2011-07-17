# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jesús Martín <jmartin@zikzakmedia.com>
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
    "name": "base_contact_vat",
    "version": "0.1",
    "author": "Zikzakmedia SL",
    "website": "http://www.zikzakmedia.com",
    "category": "Base",
    "description": "Add VAT field to contact",
    "depends": [
        'base_contact',
        'base_vat',
    ],
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "update_xml" : [
        'res_partner_contact_view.xml',
    ],
    "installable": True,
}
