# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from reportlab import platypus
from report.render.rml2pdf.trml2pdf import utils
from base_rml2pdf_extra_tags.trml2pdf_interface import register_tag

class ParagraphNoWrap(platypus.Paragraph):
    def wrap(self, availableWidth, availableHeight):
        para_wrap = platypus.Paragraph.wrap(self, availableWidth, availableHeight)
        # fake null size
        self.height = 0
        self.width = 0
        # return real right
        return (para_wrap[0], para_wrap[1])


def paranowrap_parser(fobj, node, extra_style=None):
    style = fobj.styles.para_style_get(node)
    if extra_style:
        style.__dict__.update(extra_style)
    result = []
    text = fobj._textual(node).replace('\n','<br/>')
    attrs = utils.attr_get(node, [], {'bulletText':'str'})
    result.append(ParagraphNoWrap(text, style, **attrs))
    return result

register_tag('para-nowrap', paranowrap_parser)
