=============
Configuration
=============

The OpenERP Web Client's configuration mostly relies on `CherryPy's
configuration system
<http://docs.cherrypy.org/dev/refman/_cpconfig.html#architecture>`_.

A basic understanding of CherryPy's configuration is therefore a good
starting point, but will not be covered in this document.

Configuration Process
=====================

The Web Client starts by configuring a number of default properties,
mostly to set up CherryPy itself and various tools.

Some of the default options can be overridden if need be, those will
be described in the `configuration keys`_ section.

Following the loading of the default keys, the Web Client finds its
external configuration file by using a file or file-like object
explicitly provided to :func:`openobject.configure` or -- if none is
provided -- calling :func:`openobject.config.find_file`. See its
documentation for the precise configuration discovery steps.

Configuration API
=================

.. warning:: Configuring the Web Client is not an option, an
   unconfigured web client will either fail to start at all or behave
   incorrectly.

.. autofunction:: openobject.configure

Configuration Keys
==================

Titles correspond to configuration file sections, sub-titles to actual
keys.

global
------

The ``global`` section is mostly dedicated to CherryPy and
CherryPy-related settings.

environment
+++++++++++

CherryPy environment configuration, for CherryPy's built-in
environment templates.

See `CherryPy Config API: Environment
<http://www.cherrypy.org/wiki/ConfigAPI#environments>`_ for details.

server.*
++++++++

Configuration of the CherryPy server. See the `CherryPy Server API
<http://www.cherrypy.org/wiki/ServerAPI>`_ for reference.

tools.sessions.*
++++++++++++++++

Configuration for the CherryPy session tool. See the `CherryPy
Sessions Tool <http://www.cherrypy.org/wiki/CherryPySessions>`_ for
reference.

The session tools are enabled by default

tools.proxy.*
+++++++++++++

Configuration for the CherryPy proxy tool. See `CherryPy Builtin
Tools: Proxy <http://www.cherrypy.org/wiki/BuiltinTools#tools.proxy>`_
for reference.

The proxy tool is needed if you set up the Web Client behind a server
proxy (Apache mod_proxy for instance): it tells CherryPy that it is
behind a proxy and correctly interprets some important
informations. Without this, the web client behind a proxy will not
work correctly.

Depending on your precise proxy software and configuration, you may
not need it or may need specific configurations. See your proxy's and
CherryPy's documentation for details.

.. _access-log-configuration:

log.*
+++++

Configuration for `CherryPy's logging system
<http://www.cherrypy.org/wiki/Logging>`_. In the Web Client,
CherryPy's logging is used *only* for `Apache/NCSA Combined Log Format
access log <http://httpd.apache.org/docs/2.0/logs.html#combined>`_,
all other logging is handled directly via Python's logging library.

There are two important keys for access logging:

* ``log.screen`` indicates whether the access logging should be sent
  to ``stderr``, it is ``True`` by default. Set to ``False`` if you
  want to disable access logging to stderr.

* ``log.access_file`` is used to send access logging to an arbitrary
  file on the filesystem. The user having launched the Web Client
  needs to have write access on the file.

tools.csrf.on
+++++++++++++

OpenERP Web Client's `Cross-Site Request Forgery
<http://en.wikipedia.org/wiki/Cross-site_request_forgery>`_
protection.

Enabled by default, simply add this key and set its value to ``False``
if you need to disable the CSRF tool.

tools.cgitb.*
+++++++++++++

Web Client's extended error logging tool: in case of error within the
Web Client, logs more extensive information than the normal CherryPy
output.

Enabled by default, you can disable it by setting ``tools.cgitb.on =
False``.

It is possible to filter the errors logged by ignoring specific errors
via the ``tools.cgitb.ignore`` key: it's a sequence of error class
names (full).

openerp-web
-----------

This section is dedicated to the web client's own configuration and
needs.

opener.server.*
+++++++++++++++

Configuration of the communication settings with an OpenERP server.

``openerp.server.host`` is the host name of the server,
``openerp.server.port`` is the port name for contacting the server,
``openerp.server.protocol`` is the communication protocol with the
OpenERP server (current values are ``'socket'`` for NetRPC and
``'http'`` or ``'https'`` for XMLRPC).

The last value is ``openerp.server.timeout``, it is used by the web
client to cut off communications with the server when the server
doesn't reply after the specified length of time (in seconds). The
more powerful your OpenERP server, the lower this value can be.

By default, it is set to 450 seconds (7mn 30s).

dblist.filter
+++++++++++++

Should the list of databases (on the login screen) be filtered by the
client based on the host name of the site.

Possible values are:

``None``
  Do not filter the database names
``'EXACT'``
  Display only the database whose name is the same as the host name
``'UNDERSCORE'``
  Display only the databases whose name starts with the host name and
  an underscore (if the host is ``somehost``, will allow any database
  name starting with ``somehost_``)
``'BOTH'``
  Display any database matching the conditions for ``EXACT`` *or*
  ``UNDERSCORE``.


dbbutton.visible
++++++++++++++++

Set to ``True`` if the database-management button should appear on the
login screen, ``False`` otherwise.

.. _error-log-configuration:

logging.config.file
+++++++++++++++++++

If set, provides a configuration file path for the :doc:`logging
<logging>` subsystem.

The file must use the `Python logging configuration file format
<http://docs.python.org/library/logging.html#configuration-file-format>`_.

Other docs I don't know how to name
===================================

.. autofunction:: openobject.config.find_file

.. envvar:: OPENERP_WEB_SERVER

   Filesystem path to an Openerp Web Client configuration file. Can
   contain references to other environment variables or to ``~``
   (e.g. ``~foo/config`` or ``%APPDATA%/stuff.ini``), they will be
   expanded (once).
