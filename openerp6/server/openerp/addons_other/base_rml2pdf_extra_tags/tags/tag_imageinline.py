# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import base64
import cStringIO
from reportlab import platypus
from reportlab.lib.utils import ImageReader
from base_rml2pdf_extra_tags.trml2pdf_interface import register_tag

class ImageInline(platypus.Flowable):
    def __init__(self, img, width=-1, height=-1):
        platypus.Flowable.__init__(self)
        if img:
            imgdata = base64.decodestring(img)
            imgfile = cStringIO.StringIO(imgdata)
            self.img = ImageReader(imgfile)
            self.width, self.height = self.img.getSize()
        else:
            self.img = False

    def draw(self):
        if self.img:
            self.canv.drawImage(self.img, 0, 0, self.width, self.height)

def imageinline_parser(fobj, node, extra_style=None):
    _imagedata = fobj._textual(node)
    return ImageInline(_imagedata)

register_tag('imageinline', imageinline_parser)
