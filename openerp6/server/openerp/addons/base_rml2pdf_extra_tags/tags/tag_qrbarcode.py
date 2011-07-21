# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

try:
    from cStringIO import StringIO
    _hush_pyflakes = [ StringIO ]
except ImportError:
    from StringIO import StringIO

from reportlab import platypus
from reportlab.lib.utils import ImageReader
from report.render.rml2pdf import utils
from base_rml2pdf_extra_tags.trml2pdf_interface import register_tag

# ported patch from Julien Thewys <jth@openerp.com>, all credits
# goes to him

class QrBarcode(platypus.Flowable):
    def __init__(self, text='', x=0, y=0, version='9', eclevel='M', appendPageNumber=False, absolutePos=False, model=None, localcontext={}):
        platypus.Flowable.__init__(self)
        self.text = text
        self.model = model
        self.version=version
        self.eclevel=eclevel
        self.x = x
        self.y = y
        self.appendPageNumber = appendPageNumber
        self.absolutePos = absolutePos
        self.createBarcode(self.text)
        localcontext.setdefault('participation_id', []).append(self.text)

    def createBarcode(self, text):
        import elaphe
        self.barcode = elaphe.barcode('qrcode', text, options=dict(version=self.version, eclevel=self.eclevel), data_mode='8bits')

    def draw(self):
        text = '%s-%s' % (self.model, self.text)
        if self.appendPageNumber:
            # auto append pagenumber to barcode data
            text += "-%s" % (self.canv._pageNumber)
            # TODO append page count
        self.createBarcode(text)
        self.canv.saveState()
        # move to document position (0,0) is required
        if self.absolutePos:
            abs_pos = self.canv.absolutePosition(0, 0)
            self.canv.translate(-1 * abs_pos[0], -1 * abs_pos[1])
        # draw QR code
        # actually it is drawn like a JPEG image with max quality to avoid
        # errors in generated pdf (PDFImage sometime give errors in PDF)
        bc_buf = StringIO()
        self.barcode.save(bc_buf, format='JPEG', quality=95, optimize=True)
        bc_buf.seek(0)
        bc_img = ImageReader(bc_buf)
        (bc_imgx, bc_imgy) = bc_img.getSize()
        self.canv.drawImage(bc_img, self.x, self.y)

        self.canv.restoreState()

    def wrap(self, availableWidth, availableHeight):
        if self.absolutePos:
            # fake size as we won't be display in place where we are.
            return (0,0)
        return self.barcode.size

def qrbarcode_parser(fobj, node, extra_style=None):
    attrs = utils.attr_get(node,
                    ['version', 'eclevel', 'x', 'y','appendPageNumber',
                     'absolutePos', 'model'],
                    {
                        'version': 'int',
                        'eclevel': 'int',
                        'appendPageNumber': 'bool',
                        'absolutePos': 'bool',
                        'model': 'str',
                    })
    attrs['text'] = fobj._textual(node)
    attrs['localcontext'] = fobj.localcontext
    return QrBarcode(**attrs)

register_tag('qrBarCode', qrbarcode_parser)
