# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright: Slobodni programi d.o.o., Zagreb
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

{
    "name" : "Croatia - localization with RRIF's 2011 chat of accounts",
    "description" : """
Croatian localisation.
======================

Author: Goran Kliska @ Slobodni programi d.o.o.
Contributions: 

Description:

RRIF-ov računski plan za poduzetnike za 2011.
Vrste konta
Kontni plan prema RRIF-u, dorađen u smislu kraćenja naziva i dodavanja analitika
Porezne grupe prema poreznoj prijavi
Porezi PDV-a
Ostali porezi (samo češće korišteni) povezani s kontima kontnog plana

Izvori podataka:
 http://www.rrif.hr/dok/preuzimanje/rrif-rp2011.rar

TODO :
- Unaprijediti vrste konta
- Dodati i ostale poreze i trošarine


""",
    "version" : "2011.1",
    "author" : "Slobodni programi d.o.o.",
    "category" : "Localisation/Account Charts",
    "website": "http://www.slobodni-programi.hr",

    "depends" : ["account",],
    'init_xml': [],
    'update_xml': [
                'data/account.account.type.csv',
                'data/account.tax.code.template.csv',
                'data/account.account.template.csv',
                'l10n_hr_wizard.xml',
                'data/account.tax.template.csv',
                   ],
    "demo_xml" : [],
    'test' : [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
