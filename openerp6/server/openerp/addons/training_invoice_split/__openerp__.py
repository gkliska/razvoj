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

{
    'name' : 'Training Invoice Split',
    'version' : '0.1',
    'author' : 'Zikzakmedia SL',
    'website' : 'http://www.zikzakmedia.com',
    "license" : "GPL-3",
    'category' : 'Enterprise Specific Modules/Training',
    'description' : """Replace Invoicing Subscription of Training Module (total subscription line is one invoice) and add new invoicing system:
- Invoice total subscription line
- Desing Offer Payment and Total subscription line fractional invoicing (create multiple invoices). For example, every month, create one invoice of 20 euros, during 6 month
Multicompany Invoice:
- Create one company (not need create accounts) and others companies need to parent it. OpenERP user are login in company parent (top company) to create invoices two or more companies
- Change Subscription and Subscription Line Sequence for this blank company
    """,
    'depends' : [
        'account_payment_extension',
        'training',
    ],
    'init_xml' : [
    ],
    'demo_xml' : [
    ],
    'update_xml' : [
        'wizard/create_invoicing_view.xml',
        'wizard/create_invoice_view.xml',
        'security/ir.model.access.csv',
        'training_view.xml',
    ],
    'active' : False,
    'installable' : True,
}
