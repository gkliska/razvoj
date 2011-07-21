=======================
Starting the Web Client
=======================

The simplest way to launch the Web Client is to use the command line
script:

Command-line web client
=======================

.. program:: openerp-web.py

The main launcher script is ``openerp-web.py``. It can take a number
of options to customize its behavior:

.. option:: -c <file>, --config <file>

   Explicitly provide a configuration file for the web client,
   bypasses configuration file discovery.

   If no configuration file is provided explicitly, the Web Client go
   through its configuration file discovery process, as described in
   :func:`openobject.config.find_file`.

.. option:: -a <address>, --address <address>

   Binds the web client's HTTP server to an alternate host name,
   different than the one provided in the configuration file.

.. option:: -p <port>, --port <port>

   Binds the web client's HTTP server to an alternate port, different
   than the one provided in the configuration file.

.. option:: --no-static

   By default, the web client will serve static files (images,
   javascript or CSS files) through its own HTTP server. This is
   convenient, but not necessarily efficient. If you are using a
   separate server for static files, you need to disable the web
   client's handling of them.

.. _commandline-logging-configuration:

Logging options
---------------

These options are specific to the configuration of the :doc:`logging
subsystem <logging>`.

.. option:: -q, --quiet

   Quieten all logging, can be used several times to make it even
   quieter.

.. option:: -v, --verbose

   Increases all logging, can be used several times to get even more
   logging.

.. option:: -l <logger[:level]>, --log <logger[:level]>

   Quick logger configuration: explicitly sets the logging level on
   the provided (Python) logger.

   If no level is provided, sets it to ``DEBUG`` (maximum
   verbosity). The possible values for ``level`` are (in order of
   increased verbosity) ``CRITICAL``, ``ERROR``, ``WARNING``, ``INFO``
   and ``DEBUG``. It is also possible to use ``NOTSET`` to remove a
   value previously set on a given logger (via a logging configuration
   file for instance). The default level for loggers is generally
   ``WARNING``.

   Can be used to increase the logging on a given subsystem or -- in
   conjunction with ``-v`` -- to lower the logging verbosity on some
   sub-systems in order to ignore them.

.. _commandline-logging-configuration-file:

.. option:: --logging-config <file>

   A path to a `logging configuration file
   <http://docs.python.org/library/logging.html#configuration-file-format>`_,
   which will be used to set up the web server's logging system.

The most explicit options (``-l``, ``-v`` and ``q``) take precedence
over settings from the logging configuration file provided (if any).
