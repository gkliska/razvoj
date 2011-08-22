# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_base
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
##    Copyright (C) 2008-2009 B2CK, Cedric Krier, Bertrand Chenal (the methods "check_vat_[a-z]{2}"
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
#
# import vatnumber ?
# requires suds&vatnumber libs
"""
Check the VAT number depending of the country based on formula from
http://sima-pc.com/nif.php
http://en.wikipedia.org/wiki/Vat_number


VIES_URL='http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl'

def check_vies(vat):
    '''
    Check VAT number for EU member state using the SOAP Service
    '''
    from suds.client import Client
    client = Client(VIES_URL)
    code = vat[:2]
    number = vat[2:]
    res = client.service.checkVat(countryCode=code, vatNumber=number)
    return bool(res['valid'])


"""

from osv import osv, fields



def mod1110(value):
    '''
    Compute ISO 7064, Mod 11,10
    '''
    t = 10
    for i in value:
        c = int(i)
        t = (2 * ((t + c) % 10 or 10)) % 11
    return (11 - t) % 10



class res_partner(osv.osv):
    _inherit = 'res.partner'

    def check_vat_hr(self, vat):
        '''
        Check Croatia VAT number.
        '''
        if len(vat) != 11:
            return False
        try:
            int(vat)
        except ValueError:
            return False
        check = mod1110(vat[:-1])
        if check != int(vat[10]):
            return False
        return True

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
