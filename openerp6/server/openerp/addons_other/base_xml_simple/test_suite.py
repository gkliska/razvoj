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


from __future__ import with_statement
from osv import osv
from lxml import etree
import test_partner

class xml_simple_test_suite(osv.osv):
    """ 
    This class provides way to run tests using the rpc mechanism. 
    Useful for writing server-side tests when using tools like OERPScenario.
    """
    
    _description = 'Test suite object for base_xml_simple'
    _name = "xml.simple.test.suite"
    _auto = False
    
    def run_tests(self, cr, uid):
        test_partner.partner_serialization_test(self, cr, uid)
        test_partner.partner_deserialization_test(self, cr, uid)
        return True
        
    
xml_simple_test_suite()
