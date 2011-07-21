# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from reportlab import platypus
from report.render.rml2pdf import utils
from base_rml2pdf_extra_tags.trml2pdf_interface import register_tag

# ported patch from Julien Thewys <jth@openerp.com>, all credits
# goes to him

class CheckBox(platypus.Flowable):
    def __init__(self, x=0, y=0, size=10, checked=False, context='', color='black', bordercolor='black', localcontext={}):
        platypus.Flowable.__init__(self)
        self.color = color
        self.bordercolor = bordercolor
        self.width = size + 2
        self.height = size + 2
        self.checked = checked
        self._context = context
        self.localcontext = localcontext

    def drawOn(self, canvas, x, y, _sW=0):
        # Get absolute drawing position on page in top-left coordinate
        # (0,0) is located on top-left corner.
        x_abs, y_abs = canvas.absolutePosition(x, y)
        x_rel_min = x_abs
        y_rel_min = canvas._pagesize[1] - (y_abs + self.height)
        x_rel_max = x_abs + self.width
        y_rel_max = canvas._pagesize[1] - (y_abs)
        coordinates = [x_rel_min, y_rel_min, x_rel_max, y_rel_max]
        if self.localcontext.has_key('checkboxes_position'):
            while len(self.localcontext['checkboxes_position']) - 1 < canvas._pageNumber:
                self.localcontext['checkboxes_position'].append([])
            self.localcontext['checkboxes_position'][canvas._pageNumber].append(coordinates)

        if self.localcontext.has_key('checkboxes_context'):
            while len(self.localcontext['checkboxes_context']) - 1 < canvas._pageNumber:
                self.localcontext['checkboxes_context'].append([])
            self.localcontext['checkboxes_context'][canvas._pageNumber].append(self._context)
        return platypus.Flowable.drawOn(self, canvas, x, y, _sW)

    def draw(self):
        self.canv.saveState()
        self.canv.setStrokeColor(self.bordercolor)
        self.canv.rect(x=1,y=1,width=self.width,height=self.height)
        if self.checked:
            self.canv.setStrokeColor(self.color)
            self.canv.line(2, 2, self.width, self.height)
            self.canv.line(2, self.height, self.width, 2)
        self.canv.restoreState()

def checkbox_parser(fobj, node, extra_style=None):
    _cb_data = fobj._textual(node)
    attrs =  utils.attr_get(node,
                        ['x','y','size','context', 'checked',
                         'color', 'bordercolor'],
                        {
                            'x': 'int',
                            'y': 'int',
                            'size': 'int',
                            'checked': 'bool',
                            'color': 'str',
                            'bordercolor': 'str',
                        })
    # XXX rename variable: context is unicode string containing text node content inside checkbox
    if 'context' not in attrs and _cb_data:
        attrs['context'] = _cb_data
    attrs['localcontext'] = fobj.localcontext
    return CheckBox(**attrs)

register_tag('CheckBox', checkbox_parser)
