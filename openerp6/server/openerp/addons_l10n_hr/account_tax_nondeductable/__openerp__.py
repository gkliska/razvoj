# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_tax
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#    Contributions: 
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

#import 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


{
    "name" : "Croatian localization - taxes",
    "description" : """
Croatian localisation.
======================

Author: Goran Kliska @ Slobodni programi d.o.o.
Contributions: 

Description:

Croatian purchase taxes. 30-70% taxes

TODO :


""",
    "version" : "11.1",
    "author" : "Slobodni programi d.o.o.",
    "category" : "Localisation/Croatia",
    "website": "http://www.slobodni-programi.hr",

    'depends': [
               'base_vat',
                ],
    'init_xml': [],
    'update_xml': [
                   'data/res.bank.csv'
                   'data/l10n_hr_base.nkd.csv'
                   ],
    "demo_xml" : [],
    'test' : [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
