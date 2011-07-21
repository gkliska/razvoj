# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution - module extension
#    Copyright (C) 2010- O4SB (<http://openforsmallbusiness.co.nz>).
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account Reporting and Multicompany extension',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'O4SB - Graeme Gellatly',
    'website': 'http://www.openforsmallbusiness.co.nz',
    'depends': ['base', 'account', 'report_aeroo'],
    'description': """
    *** This module is AGPLv3 and incompatible with OpenERP Enterprise Private Use License.  It may also depend on other AGPLv3 moudles
    for which neither OpenERP or I hold copyright, so sorry Private Use customers, I am unable to dual license ***
    This module provides :
        differentiated default journal sequences, journal names and account codes for multicompany
        removes required restriction from account code_digits
        adds short_name to company
        adds new account types to allow better balance sheet and P & L reporting
        replaces default Balance Sheet and P & L.
        
        in order to use effectively you must code your account templates / accounts in to the correct category
            Current Assets
            Non Current Assets
            Current Liabilities
            Non Current Liabilities
            Equity
            
            Income
            COGS
            Expenses
            Non Operating Income
            Non Operating Expenses
        
        or in xml and csv import terms here is the selection field code for your account.account.type
        
        ('none','/'),
        ('income','Profit & Loss (Operating Income Accounts)'),
        ('cogs', 'Profit & Loss (Cost of Goods Sold Accounts)'),
        ('expense','Profit & Loss (Operating Expense Accounts)'),
        ('other_income', 'Profit & Loss (Other Income Accounts)'),
        ('other_expenses', 'Profit & Loss (Other Expense Accounts)'),
        ('asset','Balance Sheet (Current Asset Accounts)'),
        ('fixed_asset', 'Balance Sheet (Non Current Asset Accounts'),
        ('liability','Balance Sheet (Current Liability Accounts)')
        ('fixed_liability', 'Balance Sheet (Non Current Liability Accounts)')
        ('equity', 'Balance Sheet (Equity Accounts)'),
        
        Note while not entirely accurate codes, original codes were reused to keep backward compatibility in case you are importing a chart 
        from a wizard or installer and they have not been updated, because you didn't read these instructions, or you don't know how and will
        change them in GUI afterwards.        
        
        Designed for 6.0.2 by Graeme Gellatly
    """,
    "init_xml": [],
    'update_xml': ['account_extension_view.xml', 'wizard/account_extension_wizard_view.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}