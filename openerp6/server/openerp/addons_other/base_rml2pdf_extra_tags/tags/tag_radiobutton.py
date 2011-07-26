# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

# ported patch from Stephane Wirtel <stephane@openerp.com>, all credits
# goes to him

from report.render.rml2pdf import utils
from reportlab import platypus
from base_rml2pdf_extra_tags.trml2pdf_interface import register_tag

class RadioButton(platypus.Flowable):
    def __init__(self, x=0, y=0, size=10, number=5, space=1, context=''):
        platypus.Flowable.__init__(self)
        self.width = size + 2
        self.height = size + 2
        self.number = number
        self.space = space
        self._context = context

    def draw(self):
        pos = 1
        for n in range(0, self.number):
            self.canv.rect(x=pos,y=1,width=self.width,height=self.height)
            pos += self.width + (2*self.space)


def radio_button_parser(fobj, node, extra_style=None):
    """
    RadioButton parser

    :param fobj: report.render.rml2pdf.trml2pdf._rml_flowable instance
    :param node: etree.Element instance, describing the rml current node
    """
    _cb_data = fobj._textual(node)
    attrs =  utils.attr_get(node,
                    ['x', 'y', 'size', 'number', 'context', 'space'],
                    {
                        'x' :'int',
                        'y' :'int',
                        'size': 'int',
                        'number': 'int',
                        'space': 'int'
                    })
    if 'context' not in attrs and _cb_data:
        attrs['context'] = _cb_data
    return RadioButton(**attrs)

register_tag('radioButton', radio_button_parser)

