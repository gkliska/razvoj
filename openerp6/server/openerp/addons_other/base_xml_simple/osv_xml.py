# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 Ville D'ouro (<http://villedouro.com.br>). All Rights Reserved
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
#    Author: Cloves J. G. de Almeida <cjalmeida@gvmail.br>
#
##############################################################################

"""
This module add xml serialization and deserialization capabilities to osv.osv objects
"""
from lxml import etree
from lxml import objectify
from osv import osv
import logging
log = logging.getLogger('osv_xml')

def to_xml(obj, cr, uid, ids, root_tag, bindings, context=None):
    """
    Convert an OpenObject object into a xml representation.

    The bindings argument is a list of strings or tuples of the following form:

      * 'colname' or ('colname')
          Creates a element named 'colname' bound to 'colname' column

      * ('colname', 'element')
          Creates a element named 'element' bound to 'colname' column

      * ('colname', 'element', 'subcol')
          For relations, creates a element named 'element' bound to 'colname' column
          but instead of object id, uses subcol as value. The subcol must be unique,
          else the deserializer will return the ID of the first match.

      * ('colname', 'element', bindings) -- for relations
          Creates a element named 'colname' bound to 'colname' column. The bindings
          represents the structure for the subelements.
          
    'colname' might optionally start with the '#' character, which is useful for de-serialization. See the from_xml method.

    On shallow serializations, relations are represented by their ID, unless specified using the 3 element tuple form.

    One2Many relations are serialized as a list of the form
        <colname>
            <item>data</item>
            <item>data</item>
        </colname>
    where 'data' is either the ID or a XML fragment (if deep serialization)

    The return object is an lxml (http://codespeak.net/lxml) root element that can be further manipulated. You can
    generate a XML string with etree.tostring(root), where root is the output of this function.
    """

    columns = []
    for rule in bindings:
        # get the binding column
        if type(rule) == tuple:
            columns.append(rule[0].replace('#',''))
        else:
            columns.append(rule.replace('#',''))

    # Build data set
    data = obj.read(cr, uid, ids, columns, context)[0]

    # create document
    root = etree.Element(unicode(root_tag))

    # do the binding for each binding rule
    for rule in bindings:
        # get the binding column
        if type(rule) == tuple:
            col = rule[0].replace('#','')
        else:
            col = rule.replace('#','')

        # get the element name
        if type(rule) == tuple and len(rule) > 1:
            ename = rule[1]
        else:
            ename = col

        # get the subcol if necessary
        if type(rule) == tuple and len(rule) > 2 and type(rule[2]) == str:
            subcol = rule[2]
        else:
            subcol = None

        # get the bindings for deep serialization
        if type(rule) == tuple and len(rule) > 2 and type(rule[2]) == list:
            deep_bindings = rule[2]
        else:
            deep_bindings = None

        # Create the element
        e = etree.SubElement(root,unicode(ename))

        # Append the value to the xml element
        def append(elem, value):

            if deep_bindings:
                if value:
                    # seek relation object (very specific to OpenObject's ORM)
                    rel_obj_name = obj.fields_get(cr, uid, [col])[col]['relation']
                    rel_obj = obj.pool.get(rel_obj_name)

                    # get xml fragment from recursion
                    frag_root = to_xml(rel_obj, cr, uid, [value], 'root', deep_bindings, context)

                    # append children
                    for el in frag_root:
                        elem.append(el)

            elif subcol:
                if value:
                    # seek relation object (very specific to OpenObject's ORM)
                    rel_field = obj.fields_get(cr, uid, [col])[col]
                    rel_obj_name = rel_field['relation']
                    rel_obj = obj.pool.get(rel_obj_name)

                    # query for value
                    sub_value = rel_obj.read(cr, uid, [value], [subcol])[0][subcol]
                    elem.text = unicode(sub_value)

            else:
                # OpenObject return False if the relation is not defined.
                # we should print False only if a boolean field. Else
                # print nothing
                if value or obj.fields_get(cr, uid, [col])[col]['type'] == 'boolean':
                    elem.text = unicode(value)


        # Parse according to data return type
        if type(data[col]) == list:
            for _id in data[col]:
                e_item = etree.SubElement(e,u'item')
                append(e_item, _id)

        elif type(data[col]) == tuple:
            append(e, data[col][0])

        else:
            append(e, data[col])

    return root

def from_xml(obj, cr, uid, xml, bindings, context=None):
    """
    Returns a tuple  where:
        * (0, 0, fields) if no record was resolved
        * (1, id, fields) if a record was resolved and it's id.
        
    'fields' is a dict according to OpenERP's expected format to be supplied in 'vals' argument in
    'create' and 'write' methods.

    The 'bindings' parameter is expected to be in the same format used for serialization in 'to_xml'.
    
    By default, all child elements not included in XML are to be discarded. For instance, if a res.partner record
    has two addresses and only one is included in XML, the other is removed.   
    
    In order to correctly resolve the the object, the function uses the following rules:
        1) If the (col, tag, subcol) form is used, will search for the subcol.
        2) If there is one or more column names prefixed with the '#' char, search for a record matching those columns.
        2a) If more than one ID, return the first returned (you REALLY shouldn't rely on this) 
        3) Else, search for the record matching the 'id' element if such exist.
           
    For example, the following binding
        [ '#id1','#id2', 'name']
    will issue a search using 
        [('id1','=',id1_value), ('id2','=',id2_value)]
    as argument.
            
    """


    if not context:
        context = {'active_test': False}
        
    if type(xml) == str or type(xml) == unicode:
        xml = objectify.fromstring(xml)
    
    data = dict()
    deep_cols = []
    search_cols = []
    search_vals = []
    
    # do the binding for each binding rule
    for rule in bindings:
        try:
            # get the binding column
            if type(rule) == tuple:
                col = rule[0]
            else:
                col = rule
            
            # check if it's a search argument
            if col[0] == '#':
                search_cols.append(col[1:])
            col = col.replace('#','')    
            
            # get the element name
            if type(rule) == tuple and len(rule) > 1:
                ename = rule[1]
            else:
                ename = col
    
    
            # get the subcol if necessary
            if type(rule) == tuple and len(rule) > 2 and type(rule[2]) == str:
                subcol = rule[2]
            else:
                subcol = None
    
            # get the bindings for deep serialization
            if type(rule) == tuple and len(rule) > 2 and type(rule[2]) == list:
                deep_bindings = rule[2]
                deep_cols.append(col)
            else:
                deep_bindings = None
    
            # seek field object (very specific to OpenObject's ORM)
            if col == 'id':
                field = {'type': None}
            else:
                field = obj.fields_get(cr, uid, [col])[col]
                if 'relation' in field:
                    field_obj = obj.pool.get(field['relation'])
    
    
            # Expect a string value
            # or a xml fragment
            def append(value):
                if deep_bindings:
                    if value:
    
                        # get the tuple from recursion and append
                        frag_tupl = from_xml(field_obj, cr, uid, value, deep_bindings)
                        data[col].append(frag_tupl)
    
    
                else:
                    if subcol:
                        if value:
                            # query for id.
                            res = field_obj.search(cr, uid, [(subcol, '=', str(value))])
                            assert len(res) > 0, 'Value "%s" not found in column "%s" for object %s' % (value, subcol, field['relation'])
                            assert len(res) == 1, 'More then one value "%s" found in column "%s" for object %s' % (value, subcol, field['relation'])
                            value = res[0]
    
    
                    if field['type'] in ('boolean', 'integer', 'integer_big', 'float'):
                        if value:
                            data[col] = eval(str(value))
                        else:
                            data[col] = False
    
                    elif field['type'] in ('one2many', 'many2many'):
                        if value:
                            data[col][0][2].append(value)
                        
                    elif field['type'] in ('many2one', ):
                        if value:
                            data[col] = int(value)
                            
                    else:
                        if value:
                            data[col] = unicode(value)
    
    
            if field['type'] in ('one2many', 'many2many'):
                if deep_bindings:
                    data[col] = []
                else:
                    data[col] = [(6,0,[])]
    
                for e in getattr(xml, ename).iterchildren():
                    append(e)
            else:
                try:
                    append(getattr(xml, ename))
                except AttributeError:
                    data[col] = None
            
            if col in search_cols:
                search_vals.append(data[col])
                
        except Exception, e:
            log.exception(e)
            raise Exception("Error while processing binding rule %s" % str(rule))


    obj_id = 0
    action = 0
    
    # Try the id column if no id columns have been specified
    if not search_cols and 'id' in data:
        search_cols.append('id')
        search_vals.append(data['id'])
    
    # Resolve the object
    # Try columns with the hash character
    if search_cols:
        
        criteria = []
        for c,v in zip(search_cols, search_vals):
            criteria.append((c,'=',v))
        
        res = obj.search(cr, uid, criteria)
        if res:
            obj_id = int(res[0])
            action = 1
    
    # Build the tuple
    tup = (action, obj_id, data)

    # Unlink child objects in deep serialization if not referenced in xml
    for col in deep_cols:
        field = obj.fields_get(cr, uid, [col])[col]
        xml_ids = set([x[1] for x in data[col]])
        all_ids = set(obj.read(cr, uid, [tup[1]], [col])[0][col])
        surplus_ids = all_ids - xml_ids
        for x in surplus_ids:
            data[col].append((2,x,{}))

    return tup


# Add to osv.osv
osv.osv.to_xml = to_xml
osv.osv.from_xml = from_xml
