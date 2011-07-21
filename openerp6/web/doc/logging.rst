===============================
Logging configuration and usage
===============================

Most applications produce tracing and debugging, and the web client is
no different.

The Web Client uses `Python's built-in logging library
<http://docs.python.org/library/logging.html>`_ for most of its needs,
though it also relies on `CherryPy for the Apache/NCSA access logging
<http://www.cherrypy.org/wiki/Logging>`_.

Access Logging
==============

CherryPy provides built-in facilities for generating an Apache/NCSA
access log (listing all the requests received by the webserver and a
few meta-informations).

See :ref:`the log.* configuration keys <access-log-configuration>` for
more details.

Error logging
=============

Configuring the error logging
-----------------------------

During development, it is expected that the default logging (to
``stderr``) and simply change the logging level as they wish depending
on their information need, using the :ref:`command-line logging
options <commandline-logging-configuration>`.

Once a Web Client has been set up in a headless configuration
(testing, staging, production, ...) a more robust (and flexible) way
to configure its output is usually required.

For this, the Web Client relies on `the logging library's
configuration files
<http://docs.python.org/library/logging.html#configuration-file-format>`_
which -- while fairly complex -- are flexible in the extreme and give
access to `logging's array of built-in handlers
<http://docs.python.org/library/logging.html#streamhandler>`_ which
allow sending logging data to just about any destination possible.

There are two ways to provide a logging configuration file to the Web
Client:

#. By using the :ref:`logging configuration file option
   <commandline-logging-configuration-file>` or the corresponding
   parameter on :func:`openobject.configure`

#. By using the :ref:`error-log-configuration` configuration key

.. warning::
   If both options are used, the first one takes precedence over the
   second one (the configuration files are *not* merged).

See the official documentation for the exact file format and available
options.

Logging usage and conventions
-----------------------------

.. todo::
   Need an API doing the equivalent of Python 2.7's `Logger.getChild
   <http://docs.python.org/library/logging.html#logging.Logger.getChild>`_
   to make getting the children of an existing logger easier (instead
   of having to write everything by hand)

.. todo::
   Need an API which does the prefixing crap on its own when getting a
   logger, and maybe even checks from which module it's called to
   setup the whole module prefix e.g.::

       openobject.logging.getLogger()

   from within ``openerp.widgets.listgrid`` would return the logger
   ``openobject.addons.openerp.widgets.listgrid``, and a (string)
   parameter would be appended. That way, the loggerizer would only
   need to give the function/class/method he's logging from, if
   desired.

* Logger names should contain at least the complete module name

  * In Web Client addons, the module name should be prefixed by
    ``openobject.addons`` so it is possible to filter all addons at
    once if needed::

      logging.getLogger('openobject.config')

    but::

      logging.getLogger('openobject.addons.openerp.widgets.listgrid')
* If logging from a function, the logger should be either module-level
  or (if there are lots of logging calls and it clarifies the log
  file) function-level (as a child logger to the module's)
* If logging from a method, the logger should be either class-level or
  method-level
* ``Logger.log`` should be avoided, the more expressive logging calls
  should be used instead
* To log a traceback, use either ``Logger.exception`` (logs at the
  ``ERROR`` level) or pass the ``exc_info=True`` kwarg to other
  logging calls
* String formatting should *always* be performed by ``logging``
  itself, never use the string formatting operator (``%``) to create a
  logging message

.. warning::
   *Never* catch an exception, log it and re-raise it: somebody in a
   stack above you will probably catch-and-log it as well, and the
   exception will end up being logged twice or thrice.

   Either log and handle it, or cleanup and re-raise it, but do not
   both log it and re-raise it.

.. note::
   If you raise a *different* exception, logging the original one
   might still be a good idea as Python 2 does not have exception
   chaining, so the original exception is lost.


Loggers hierarchy in the web client
-----------------------------------

Python loggers are hierarchical, configuring a given logger will have
an effect on all the messages logged by its children. It can therefore
be interesting to know and understand the hierarchy of loggers.

.. List and document the loggers here, if possible?

.. Create a file to generate loggers.txt?

.. literalinclude:: loggers.txt
