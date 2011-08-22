Simple XML (de)serialization for OpenObject.

Summary:
--------
The goal of this module is to provide a very simple, yet powerful mechanism for
serializing and deserializing into/from XML OpenObject records.

Usage:
------
You can check general usage on test_*.py files, which provide unit tests.

To serialize a object you simply
	>>> self.pool.get('myobject').to_xml(cr, uid, ids, 'root_tag', bindings, context)
which will return a lxml.etree.Element object with can be further manipulated.

The "'root_tag'" string is the the tag of the root element.

The only strange argument is the 'bindings' where you map object column's into
XML elements. Check osv_xml.to_xml method's documentation for details and the
unit test for usage.

To deserialize
	>>> self.pool.get('myobject').from_xml(cr, uid, xml, bindings)
which will result in a dictionary just like the one needed as argument for 'write' or 'create'
osv methods.

Running Tests:
--------------
1) Start an OpenERP server instance
2) Install the base_xml_simple module
3) Check the parameters for XML-RPC connection in run_tests.py
   * By default, will connect to:
     - server: localhost
     - database: terp
     - username: admin
     - password: admin
4) $ python run_tests.py



FAQ:
----

1) Why not use OpenObjects unit testing?
A: Because it runs every time the server is started and I don't like this behavior.
   So I've chosen to create a RPC accessible class that will run the tests and blows
   up on any error.
