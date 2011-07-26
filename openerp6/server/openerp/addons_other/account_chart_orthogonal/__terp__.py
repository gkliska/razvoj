# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
#    Written by: Cloves J. G. de Almeida <cjalmeida@gvmail.br>
#
##############################################################################


{
    'name': 'Chart of accounts filtered by an analytical account.',
    'version': '0.9',
    'category': 'Generic Modules',
    'description': """
Add the option to display the chart of accounts filtered by an analytical account. This orthogonal view could be used as
very simple way to enable multi-company. 

Originally, this is used by the mbi_pos module to use multiple stores in a single chart of account, instead of creating cash, inventory,
etc. accounts for every store. 
    """,
    'author': 'Ville Douro LTDA',
    'depends': ['account'],
    'init_xml': ['account_view.xml'],
    'update_xml': [],
    'demo_xml': [],
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
