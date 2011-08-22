# -*- coding: utf-8 -*-
"""
Collection of configuration-related helpers for the OpenERP Web Client
"""
import logging
import logging.config
import operator
import os
import os.path
import platform
import sys

import babel.localedata
import cherrypy

import openobject
import openobject.paths

__all__ = ['configure_babel', 'find_file', 'unbreak_cherrypy_logging',
           'ConfigurationError']

class ConfigurationError(Exception):
    pass

def configure_babel():
    """ If we are in a py2exe bundle, rather than babel being installed in
    a site-packages directory in an unzipped form with all its meta- and
    package- data it is split between the code files within py2exe's archive
    file and the metadata being stored at the toplevel of the py2exe
    distribution.
    """
    if not hasattr(sys, 'frozen'): return

    # the locale-specific data files are in babel/localedata/*.dat, babel
    # finds these data files via the babel.localedata._dirname filesystem
    # path.
    babel.localedata._dirname = openobject.paths.root('babel', 'localedata')

def expand(filepath):
    return os.path.expanduser(
        os.path.expandvars(
            filepath))

SETTINGS_ENVIRON_KEY = 'OPENERP_WEB_SETTINGS'
def find_file():
    """ Attempts to find and return the path to an OpenERP Web Client
    configuration file, according to the discovery process described below.

    If it can not find any configuration file, or a step of the configuration
    discovery process fails, raises ``ConfigurationError``.

    Configuration File Discovery Process for the OpenERP Web Client (steps
    tried in order, the function returns as soon as a step yields a result):

    #. If :envvar:`OPENERP_WEB_SETTINGS` is set, checks that it is a
       valid file path and returns it. If
       :envvar:`OPENERP_WEB_SETTINGS` is not a valid file path, raises
       an error.
    #. On unices (Linux, Mac OS X, BSDs), looks for the file
       ``~/.openerp-web``
    #. On Windows, looks for the file ``%APPDATA%\openerp-web\config.ini``
    #. On unices, looks for the file ``/etc/openerp-web.cfg``
    #. Looks for the file ``openerp-web.cfg`` in the client's own directory

    .. should we also put a plist file in ~/Library/Application
       Support/OpenERP Web in OSX?

    :return: configuration file path
    :rtype: str
    """
    # environ
    if SETTINGS_ENVIRON_KEY in os.environ:
        config_path = os.environ[SETTINGS_ENVIRON_KEY]
        expanded_path = expand(config_path)
        if not os.path.isfile(expanded_path):
            raise ConfigurationError(
                "Path '%s' found in environment key '%s' does not seem to be "
                "a valid configuration file" % (
                    config_path, SETTINGS_ENVIRON_KEY))
        return expanded_path

    config_files_sequence = [
        # per-user config
        (platform.system() != 'Windows', expand('~/.openerp-web')),
        (platform.system() == 'Windows', os.path.join(
            expand('%APPDATA%'), 'openerp-web', 'config.ini')),
        # system
        (platform.system() != 'Windows', '/etc/openerp-web.cfg'),
        # local fallback
        (True, openobject.paths.root('openerp-web.cfg'))
    ]

    for _, config_path in filter(operator.itemgetter(0), config_files_sequence):
        if os.path.isfile(config_path):
            return config_path

    raise ConfigurationError("Failed to find a configuration file for "
                             "the OpenERP Web Client")


def unbreak_cherrypy_logging():
    """
    Because it builds its own logging layer on top of Python's, cherrypy
    sets a number of logging attributes:

    * All logging formatters on ``cherrypy.*`` handlers are set to
      ``%(message)s`` with the message content generated manually during
      logging
    * the logging level on ``cherrypy.error`` is explicitly set to
      ``logging.DEBUG``
    * the logging level on ``cherrypy.access`` is explicitly set to
      ``logging.INFO``
    * cherrypy *will also set those on the cherrypy.{access,error}.\*
      loggers*

    This function does not touch ``cherrypy.access``, but it removes all
    handlers on ``cherrypy.error`` so that CherryPy's own logging follows
    the policies set by configuring Python's own ``logging``.
    """
    # cherrypy.log.error_log is the root ``cherrypy.error`` logger,
    # ``openobject.application.log.error_log`` is the application's
    # ``cherrypy.logger.{bunch of digits}`` error logger
    #
    # we need to set both because cherrypy is kind-of a pain in the ass like
    # that
    for logger in (cherrypy.log.error_log,
                   openobject.application.log.error_log):
        logger.setLevel(logging.NOTSET)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            if hasattr(handler, 'flush'):
                handler.flush()
            if hasattr(handler, 'close'):
                handler.close()

def configure_logging(logging_config=None, loggers=None):
    """
    Sets up logging for the OpenERP Web Client (apart from
    ``cherrypy.access``, mostly):

    * Fixes the handling of the ``cherrypy.error`` logger subtree (removes
      all handlers set up on it by ``cherrypy._cplogging``)
    * Prevents ``cherrypy.access`` messages from propagating to the root
      logger
    * If a logging configuration file is provided, calls
      ``logging.config.fileConfig``
    * Otherwise calls ``logging.basicConfig`` with the following attributes:
      * level=logging.WARNING
      * format=%(asctime)s|%(name)s:%(levelname)s|%(message)s
    * Merges any additional logging configuration from the mapping

    :param logging_config: the path to a ``logging`` configuration file, or
                           a file-like ``logging`` configuration object
    :type logging_config: str | < readline :: () -> str > | None
    :param loggers: a mapping of logger names to logger levels, the levels
                    can be either integers (actual ``logging`` levels) or
                    strings (``logging`` level names).
    :type loggers: {str: (int|"NOTSET"|"DEBUG"|"INFO"|"WARNING"|"ERROR"|"CRITICAL")}
    """
    unbreak_cherrypy_logging()
    logging.getLogger('cherrypy.access').propagate = False

    if logging_config:
        logging.config.fileConfig(expand(logging_config))
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s|%(name)s:%(levelname)s|%(message)s")

    if loggers:
        for logger, level in loggers.iteritems():
            if isinstance(level, basestring):
                level = getattr(logging, level)
            if isinstance(logger, logging.Logger):
                logger.setLevel(level)
            else:
                logging.getLogger(logger).setLevel(level)


def configure_cherrypy():
    """ Sets up CherryPy environment data
    """
    cherrypy.config.defaults.update({
        'engine.autoreload_on': True,
        'checker.on': True,
        'openerp.caching': False,
        'openerp.debug.footer': True,
    })
    cherrypy._cpconfig.environments['production'].update({
        'openerp.caching': True,
        'openerp.debug.footer': False,
    })
    cherrypy.config.reset()
