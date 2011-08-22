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

from lxml import etree
from test_helpers import *

## SETUP ##

# Define base bindings for a partner object
_bindings = [
        'id', 
        'name', 
        'active', 
        'credit_limit',
        ('address','address', [
                'id',
                'name',
                'type',
                'street',
                'street2',
                'city',
                ('state_id', 'state_code', 'code'),
                ('country_id', 'country_code', 'code'),
                'zip',
                'email',
                'phone',
                'fax',
                'mobile'
            ]
        )
]

## TESTS ##

def partner_serialization_test(suite, cr, uid):

        # Serialize
        obj = suite.pool.get('res.partner')
        oid = _fetch_main_company_id(suite, cr, uid)
        root = obj.to_xml(cr, uid, [oid], 'partner', _bindings)
        
        # Fetch original object
        data = obj.browse(cr, uid, oid)
        
        # Assert the returned object
        assertEqual(type(etree.Element('root')), type(root))        
        
        # Assert simple binding partner name
        assertEqual(data.name, root.xpath('/partner/name/text()')[0])
        
        # Assert a deep binding address city
        assertEqual(data.address[0].city, root.xpath('/partner/address/item[1]/city/text()')[0])
        
        # Assert a subcol binding country
        assertEqual(data.address[0].country_id.code, root.xpath('/partner/address/item[1]/country_code/text()')[0])


def partner_deserialization_test(suite, cr, uid):

        # Serialize into XML
        obj = suite.pool.get('res.partner')
        oid = _fetch_main_company_id(suite, cr, uid)
        root = obj.to_xml(cr, uid, [oid], 'partner', _bindings)
        xml = etree.tostring(root, pretty_print=True)

        # Fetch original object
        orig = obj.browse(cr, uid, oid)
        
        # Deserialize the object
        action, oid, data = obj.from_xml(cr, uid, xml, _bindings)
        
        # Assert action
        assertEqual(1, action)
        
        # Assert it resolves the object using id property
        assertEqual(orig.id, oid)
        
        # Assert simple binding of various types
        assertEqual(orig.name, data['name']) # char
        assertEqual(orig.active, data['active']) # boolean
        
        # Assert a deep binding address id, address city
        
        address_action, address_id, address_data = data['address'][0]
        assertEqual(1, address_action)
        assertEqual(orig.address[0].id, address_id)
        assertEqual(orig.address[0].city, address_data['city'])
        
        # Assert a subcol binding country
        assertEqual(orig.address[0].country_id.id, address_data['country_id'])

        # Modify bindings and assert it finds by name (hope there's no other partner with the same name)
        _bindings.remove('name')
        _bindings.append('#name')
        action, oid, data = obj.from_xml(cr, uid, xml, _bindings)
        assertEqual(1, action)
        assertEqual(orig.id, oid)
        
        # Modify xml and assert it DOES NOT find by name
        root.find('name').text = 'BOGUS'
        xml = etree.tostring(root, pretty_print=True)
        action, oid, data = obj.from_xml(cr, uid, xml, _bindings)
        assertEqual(0, action)
        assertEqual(0, oid)
        assertNotEqual(orig.name, data['name'])
        
        # Restore bindings value
        _bindings.remove('#name')
        _bindings.append('name')
        
        
def _fetch_main_company_id(suite, cr, uid):
    md = suite.pool.get('ir.model.data')
    ids = md.search(cr, uid, [('module','=','base'),('name','=', 'main_company')])
    return md.read(cr, uid, ids,['res_id'])[0]['res_id']
    





