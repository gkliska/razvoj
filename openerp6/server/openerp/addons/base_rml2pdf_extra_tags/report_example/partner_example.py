# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from report import report_sxw
from base_rml2pdf_extra_tags.trml2pdf import customized_report_sxw

#report_sxw.report_sxw('report.res.partner.example.report',
#                      'res.partner',
#                      'addons/base_rml2pdf_extra_tags/report_example/partner_example.rml',
#                      header=True)
#

class res_partner_report_sxw(customized_report_sxw):
    _use_extra_flowables = ['radioButton']

res_partner_report_sxw('report.res.partner.example.report',
                      'res.partner',
                      'addons/base_rml2pdf_extra_tags/report_example/partner_example.rml',
                      header=True)
