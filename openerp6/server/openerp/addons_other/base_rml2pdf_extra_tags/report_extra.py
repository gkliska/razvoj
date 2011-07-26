# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import base64
import netsvc
import pooler
from report import report_sxw
from report.pyPdf import PdfFileReader, PdfFileWriter

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

class report_with_attachment(object):
    def get_attachment_data_from_attachment_ids(self, cr, uid, attachment_ids, context=None):
        if not attachment_ids:
            return []
        attach_proxy = pooler.get_pool(cr.dbname).get('ir.attachment')
        return ( base64.decodestring(attach.datas) for attach in attach_proxy.browse(cr, uid, attachment_ids, context=context) )

    def get_attachment_data(self, cr, uid, record, context=None):
        raise NotImplementedError()

    def append_raw_data_to_document(self, document, rawdata):
        rawdoc = PdfFileReader(StringIO.StringIO(rawdata))
        for pagenum in range(rawdoc.getNumPages()):
            document.addPage(rawdoc.getPage(pagenum))

    def hook_before_document_generation(self, cr, uid, record, data, context=None):
        # XXX: TODO
        pass

    def hook_after_document_generation(self, cr, uid, record, data, context=None):
        # XXX: TODO
        pass

    def create_single_pdf(self, cr, uid, ids, data, report_xml, context=None):
        if isinstance(ids, (int, long)):
            ids = [ ids ]
        original_results = []
        original_records = self.getObjects(cr, uid, ids, context)
        final_document = PdfFileWriter()

        for record in original_records:
            # TODO: call "hook_before_document_generation"
            original_data, original_type = super(report_with_attachment, self).create_single_pdf(cr, uid, [record.id], data, report_xml, context)
            # TODO: call "hook_after_document_generation"
            self.append_raw_data_to_document(final_document, original_data)
            for data in self.get_attachment_data(cr, uid, record, context):
                self.append_raw_data_to_document(final_document, data)

        s = StringIO.StringIO()
        final_document.write(s)
        return (s.getvalue(), 'pdf')

