# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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
    "name" : "Email Invoice - Use to Send Customers or Suppliers the selected invoices attachment by Email.",
    "version" : "1.0",
    "depends" : ["smtpclient","account"],
    "author" : "Zikzakmedia SL",
    "website" : "www.zikzakmedia.com",
    "license" : "GPL-3",
    "description": """Use Email client module to send to customers or suppliers
the selected invoices attached by Email.

  * The sale order, invoice and shipping emails addresses are proposed
  * An email subject and text with the user signature are proposed
  * Later, the emails addresses, subject and text can be modified
  * A partner event is created with information of the email (partner,
    description, channel, document, user)
  * Historical and statistical data is recorded in the smtpclient module
""",
    "category" : "Generic Modules",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["account_invoice_wizard.xml"],
    "active": False,
    "installable": True
}
