# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_base
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

from osv import fields, osv, orm


class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'porezna_uprava': fields.char('Porezna uprava', size=64),
        'porezna_ispostava': fields.char('Porezna ispostava', size=64),
        'br_obveze_mirovinsko': fields.char('Br. obveze mirovinsko', size=32, help='Broj obveze mirovinskog osiguranja'),
        'br_obveze_zdravstveno': fields.char('Br. obveze zdravstveno', size=32, help='Broj obveze zdravstvenog osiguranja'),
        'maticni_broj': fields.char('Matični broj', size=16),
    }
res_company()