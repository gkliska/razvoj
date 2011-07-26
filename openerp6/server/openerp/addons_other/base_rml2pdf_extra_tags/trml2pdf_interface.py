# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import logging
TAG_REPOSITORY = {}

def get_tag(tag):
    tag_parser = TAG_REPOSITORY.get(tag, None)
    if tag_parser is None:
        raise Exception("No tag '%s' registered" % (tag))
    return tag_parser

def register_tag(tag, tag_klass, force=False):
    """
    Register a new extra tag in the tag repository
    :param tag: name of the tag used in the rml file
    :param tag_klass: reference to a parse method returning a platypus.Flowable instance
    :param force: if True the tag will be registered even if existing
    """
    logger = logging.getLogger('trml2pdf')
    if tag in TAG_REPOSITORY and not force:
        raise Exception("Tag '%s' already exists" % (tag))
    logger.debug('registering new tag: %s' % (tag))
    TAG_REPOSITORY[tag] = tag_klass

def unregister_tag(tag):
    """
    Remove a the provided extra tag from the tag repository
    """
    logger = logging.getLogger('trml2pdf')
    logging.debug('un-registering tag: %s' % (tag))
    TAG_REPOSITORY.pop(tag, False)


