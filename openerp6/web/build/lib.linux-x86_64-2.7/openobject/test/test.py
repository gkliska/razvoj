import cherrypy
import unittest2
import openobject.tools._tools

class TestCustomHeadersOnRedirection(unittest2.TestCase):
    def setUp(self):
        cherrypy.request.headers['X-Requested-With'] = 'header'
        cherrypy.request.params = {'requested_with': 'param'}
        cherrypy.response.status = 303
        cherrypy.response.headers['Location'] = 'http://example.org/foo?bar=true'
        self.fixer = openobject.tools._tools.CustomHeadersRedirectionFix()
        self.fixer.custom_headers = [
            ('X-Requested-With', 'requested_with')
        ]
    def tearDown(self):
        del cherrypy.request.headers['X-Requested-With']
        del cherrypy.request.params
        del cherrypy.response.status
        del cherrypy.response.headers['Location']

    def testHeaderToParam(self):
        self.assertEqual(
            'http://example.org/foo?bar=true',
            cherrypy.response.headers['Location'])
        self.fixer.header_to_parameter_on_redirection()
        self.assertEqual(
            'http://example.org/foo?bar=true&requested_with=header',
            cherrypy.response.headers['Location'])

    def testParamToHeader(self):
        self.assertEqual(
            'header',
            cherrypy.request.headers['X-Requested-With'])
        self.assertEqual(
            {'requested_with': 'param'},
            cherrypy.request.params)
        self.fixer.pop_parameter_to_header()
        self.assertEqual(
                'param',
                cherrypy.request.headers['X-Requested-With'])
        self.assertEqual({}, cherrypy.request.params)
