import logging
from optparse import OptionParser, OptionGroup
import sys

import cherrypy

import openobject
import openobject.config
import openobject.release
import openobject.paths

def loglevel(option, str_opt, value, parser):
    if ':' not in value:
        parser.values.log.append((value, 'DEBUG'))
        return
    logger, level = value.rsplit(':', 1)
    if level.isdigit():
        level = int(level)
    parser.values.log.append((logger, level))

def start():
    parser = OptionParser(version=openobject.release.version)
    parser.add_option("-c", "--config", metavar="FILE",
                      help="configuration file", default=None)
    parser.add_option("-a", "--address", help="host address, overrides server.socket_host")
    parser.add_option("-p", "--port", help="port number, overrides server.socket_port")
    parser.add_option("--no-static", dest="static",
                      action="store_false", default=True,
                      help="Disables serving static files through CherryPy")

    logging_options = parser.add_option_group(
        "Logging", description="Alternatives to providing a logging "
                               "configuration file via the Web Client's "
                               "config file, the `verbose` and `quiet` "
                               "options configure the logging level of the "
                               "root logger itself (from a default of "
                               "'WARNING')")
    logging_options.add_option('-q', '--quiet', action='count', default=0,
                               help="Makes the web client talk less")
    logging_options.add_option('-v', '--verbose', action='count', default=0,
                               help="Makes the web client talk more")
    logging_options.add_option('-l', '--log', metavar='LOGGER[:LEVEL=DEBUG]',
                               default=[], action="callback",
                               callback=loglevel, type="str",
                               help="Fast logger configuration: changes the "
                                    "logging level of the provided logger. "
                                    "This option can be called several times "
                                    "to set up multiple loggers. Available "
                                    "levels are NOTSET (to reset an existing "
                                    "level), DEBUG, INFO, WARNING, ERROR and "
                                    "CRITICAL in order of gravity. A given "
                                    "level implies all previous levels. It is "
                                    "also possible to use values between 0 "
                                    "(NOTSET) and 50 (CRITICAL)")
    logging_options.add_option("--logging-config", metavar="FILE",
                               help="path to a configuration file for "
                                    "Python's logging module, will be used "
                                    "to configure the web client's logging")

    options, args = parser.parse_args(sys.argv)

    overrides = {'global': {}}
    if options.address:
        overrides['global']['server.socket_host'] = options.address
    if options.port:
        try:
            overrides['global']['server.socket_port'] = int(options.port)
        except ValueError:
            pass
    if options.verbose or options.quiet:
        options.log.append(
            (logging.root,
             logging.WARNING - 10 * options.verbose + 10 * options.quiet))
    try:
        openobject.configure(options.config,
                             enable_static=options.static,
                             logging_configuration=options.logging_config,
                             loggers=dict(options.log),
                             **overrides)
    except openobject.config.ConfigurationError, e:
        parser.error(e.args[0])

    cherrypy.engine.start()
    cherrypy.engine.block()
