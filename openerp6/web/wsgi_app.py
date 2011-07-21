
import glob
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from cherrypy._cpconfig import as_dict
import openobject

conf = as_dict(os.path.join(os.path.dirname(__file__), 'doc', 'openerp-web.cfg'))
openobject.configure(conf)
openobject.enable_static_paths() # serve static file via the wsgi server

application = openobject.application

