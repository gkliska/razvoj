# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from tag_barchart_internal import Barchart
from report.render.rml2pdf import utils
from base_rml2pdf_extra_tags.trml2pdf_interface import register_tag

def barchart_parser(fobj, node, extra_style=None):
    attrs = utils.attr_get(node,
                ['width', 'height', 'orientation', 'fontName',
                 'fontSize', 'xticks', 'yticks', 'legend_display',
                 'stacked', 'flip_barlabel'],
                {
                    'width': 'int',
                    'height': 'int',
                    'orientation': 'str',
                    'fontName': 'str',
                    'fontSize': 'int',
                    'xticks': 'int',
                    'yticks': 'int',
                    'legend_display': 'str',
                    'stacked': 'bool',
                    'valueMax': 'float',
                    'flip_barlabel': 'bool'
                })
    datas = eval(fobj._textual(node))
    return [ Barchart(datas, **attrs) ]

register_tag('barchart', barchart_parser)
