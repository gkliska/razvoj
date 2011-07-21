###############################################################################
#
#  Copyright (C) 2007-TODAY OpenERP SA. All Rights Reserved.
#
#  $Id$
#
#  Developed by OpenERP (http://openerp.com) and Axelor (http://axelor.com).
#
#  The OpenERP web client is distributed under the "OpenERP Public License".
#  It's based on Mozilla Public License Version (MPL) 1.1 with following 
#  restrictions:
#
#  -   All names, links and logos of OpenERP must be kept as in original
#      distribution without any changes in all software screens, especially
#      in start-up page and the software header, even if the application
#      source code has been changed or updated or code has been added.
#
#  You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
#
###############################################################################
import cgi
import cgitb
import logging
import sys
import urllib
import urlparse

import cherrypy
import cherrypy._cptools
from formencode import NestedVariables

import openobject.dispatch
import openobject.errors
import openobject.pooler
import openobject.addons

def nestedvars_tool():
    if hasattr(cherrypy.request, 'params'):
        cherrypy.request.params = NestedVariables.to_python(cherrypy.request.params or {})

cherrypy.tools.nestedvars = cherrypy.Tool("before_handler", nestedvars_tool)
cherrypy.lowercase_api = True

def csrf_check():
    if not cherrypy.request.method == 'POST': return;

    referer = cherrypy.request.headers.get('Referer', '')
    if not(urlparse.urlsplit(referer).path and referer.startswith(cherrypy.request.base)):
        raise cherrypy.HTTPError(403, "Request Forbidden -- You are not allowed to access this resource.")
cherrypy.tools.csrf = cherrypy.Tool('before_handler', csrf_check)

def cgitb_traceback(ignore=None, severity=logging.DEBUG):
    typ, value, tb = sys.exc_info()
    if ignore and issubclass(typ, tuple(ignore)):
        return
    cherrypy.log(cgitb.text((typ, value, tb)), 'HTTP', severity=severity)
cherrypy.tools.cgitb = cherrypy.Tool('before_error_response', cgitb_traceback)

class CustomHeadersRedirectionFix(cherrypy._cptools.Tool):
    """ Firefox doesn't forward headers it has no reason to touch
    (standard or custom headers, doesn't matter) during redirection.

    This tool round-trips custom headers via GET parameters using the
    `custom_headers` mapping provided as argument. It adds the header
    as a query string parameter before request finalization and pops that
    parameter (if it exists) and sets it as a header right after the processing
    of the request body (so it takes form parameters in account)

    The setting is *unconditional* to avoid differences in behavior between
    Firefox and everybody else.

    Because the tool sets the custom header as requests come it, code within
    does not have to care about the issue.

    Firefox bug ref: https://bugzilla.mozilla.org/show_bug.cgi?id=553888
    """
    def __init__(self):
        self._name = None

    def _setup(self):
        self.custom_headers = self._merged_args().pop('custom_headers', ())

        hooks = cherrypy.request.hooks

        hooks.attach("before_handler", self.pop_parameter_to_header)
        hooks.attach("before_finalize", self.header_to_parameter_on_redirection)

    def pop_parameter_to_header(self):
        request = cherrypy.request
        for header, param in self.custom_headers:
            if param not in request.params: continue
            request.headers[header] = request.params.pop(param)

    def header_to_parameter_on_redirection(self):
        response = cherrypy.response
        headers = cherrypy.request.headers
        # You can have a redirect without a location?
        # Apparently since I'm getting one, but it's weird.
        if not 300 <= response.status < 400\
            or 'Location' not in response.headers:
            return

        # get the redirection URL
        scheme, netloc, path, query, _fragment =\
            urlparse.urlsplit(response.headers['Location'])
        params = cgi.parse_qs(query)

        for header, param in self.custom_headers:
            if header not in headers: continue
            # move our custom header to the query parameter for survival
            # through the redirection
            params[param] = headers[header]

        response.headers['Location'] = \
            urlparse.urlunsplit((
                scheme,
                netloc,
                path,
                urllib.urlencode(params, True),
                ''))
cherrypy.tools.fix_custom_headers_redirection = CustomHeadersRedirectionFix()

def clear_cache_buster():
    """ There are situations where we use jQuery's cache buster against IE's
    propensity to cache stuff it's not supposed to. But our CherryPy handlers
    tend to be strict in the params they accept, so we need to clean the
    cache-busting GET parameter if it's present.
    """
    params = cherrypy.request.params
    if '_' in params:
        del params['_']
cherrypy.tools.clear_cache_buster = cherrypy.Tool(
    'on_start_resource', clear_cache_buster, priority=0)

def check_web_modules():
    # only execute if text/html request, not e.g. JS
    if not any(media.value == 'text/html'
               for media in cherrypy.request.headers.elements('Accept')):
        return
    cherrypy.request.loading_addons = False
    autoreloader_enabled = bool(
            getattr(cherrypy.engine.autoreload, 'thread', None))
    if autoreloader_enabled:
        # stop (actually don't listen to) the auto-reloader the process
        # doesn't restart due to downloading new add-ons or refreshing
        # existing ones
        cherrypy.engine.autoreload.unsubscribe()
    try:
        if openobject.addons.has_new_modules():
            openobject.pooler.restart_pool()
    except openobject.errors.AuthenticationError:
        pass

    if autoreloader_enabled:
        # re-enable auto-reloading if it was enabled before
        cherrypy.engine.autoreload.subscribe()
cherrypy.tools.web_modules = cherrypy.Tool(
    'before_handler', check_web_modules, priority=60)

# The dispatcher has to run after we've (potentially) reloaded the
# web modules
cherrypy.tools.openobject_dispatcher = cherrypy.Tool(
    'before_handler', openobject.dispatch.Dispatcher(), priority=70)
