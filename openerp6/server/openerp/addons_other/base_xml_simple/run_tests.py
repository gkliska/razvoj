import xmlrpclib
from xmlrpclib import Fault

username = 'admin' 
pwd = 'admin'      
dbname = 'terp'
server = 'localhost'

sock_common = xmlrpclib.ServerProxy ('http://%s:8069/xmlrpc/common' % server)
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://%s:8069/xmlrpc/object' % server)

try:
    print "Connecting to OpenERP (server: %s, dbname: %s, username: %s)" % (server, dbname, username) 
    sock.execute(dbname, uid, pwd, 'xml.simple.test.suite', 'run_tests')
    print "No problems found!"
except Fault, f:
    print f.faultString
    raise f