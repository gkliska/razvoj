# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

try:
    from cStringIO import StringIO
    _hush_pyflakes = [ StringIO ]
except ImportError:
    from StringIO import StringIO

import logging
from lxml import etree
from reportlab import platypus

from report.preprocess import report as report_preprocess
from report.report_sxw import report_sxw, rml_parse
from report.render.rml import rml
from report.render.rml2pdf.trml2pdf import _rml_doc
from report.render.rml2pdf.trml2pdf import _rml_draw
from report.render.rml2pdf.trml2pdf import _rml_flowable
from report.render.rml2pdf.trml2pdf import _rml_styles
from report.render.rml2pdf.trml2pdf import _rml_template
from report.render.rml2pdf.trml2pdf import TinyDocTemplate
from report.render.rml2pdf import utils
from report.render.rml2pdf import color
from report.render.rml2pdf import trml2pdf as server_trml2pdf

import trml2pdf_interface

# _rml_style:
#
# override _table_style_get to allow overriding style per row (<tr/>)
class customized_rml_styles(_rml_styles):
    def _table_style_get(self, style_node):
        styles = []
        for node in style_node:
            start = utils.tuple_int_get(node, 'start', [0,0] )
            stop = utils.tuple_int_get(node, 'stop', [-1,-1] )
            if node.tag=='blockValign':
                styles.append(['VALIGN', start, stop, str(node.get('value'))])
            elif node.tag=='blockFont':
                styles.append(['FONT', start, stop, str(node.get('name'))])
            elif node.tag=='blockTextColor':
                styles.append(['TEXTCOLOR', start, stop, color.get(str(node.get('colorName')))])
            elif node.tag=='blockLeading':
                styles.append(['LEADING', start, stop, utils.unit_get(node.get('length'))])
            elif node.tag=='blockAlignment':
                styles.append(['ALIGNMENT', start, stop, str(node.get('value'))])
            elif node.tag=='blockSpan':
                styles.append(['SPAN', start, stop])
            elif node.tag=='blockLeftPadding':
                styles.append(['LEFTPADDING', start, stop, utils.unit_get(node.get('length'))])
            elif node.tag=='blockRightPadding':
                styles.append(['RIGHTPADDING', start, stop, utils.unit_get(node.get('length'))])
            elif node.tag=='blockTopPadding':
                styles.append(['TOPPADDING', start, stop, utils.unit_get(node.get('length'))])
            elif node.tag=='blockBottomPadding':
                styles.append(['BOTTOMPADDING', start, stop, utils.unit_get(node.get('length'))])
            elif node.tag=='blockBackground':
                styles.append(['BACKGROUND', start, stop, color.get(node.get('colorName'))])
            if node.get('size'):
                styles.append(['FONTSIZE', start, stop, utils.unit_get(node.get('size'))])
            elif node.tag=='lineStyle':
                kind = node.get('kind')
                kind_list = [ 'GRID', 'BOX', 'OUTLINE', 'INNERGRID', 'LINEBELOW', 'LINEABOVE','LINEBEFORE', 'LINEAFTER' ]
                assert kind in kind_list
                thick = 1
                if node.get('thickness'):
                    thick = float(node.get('thickness'))
                styles.append([kind, start, stop, thick, color.get(node.get('colorName'))])
        return platypus.tables.TableStyle(styles)

server_trml2pdf._rml_styles = customized_rml_styles

# _rml_flowable:
#
# add support from extra flowable comming from _rml_doc.
# 'extra_flowables' will have priority over system flowables
class customized_rml_flowable(_rml_flowable):
    def __init__(self, doc, localcontext, images=None, path='.', title=None):
        super(customized_rml_flowable, self).__init__(doc, localcontext, images=images, path=path, title=title)
        if hasattr(doc, '_extra_flowables') and doc._extra_flowables:
            self._extra_flowables = doc._extra_flowables
        else:
            self._extra_flowables = {}

    def _flowable(self, node, extra_style=None):
        tag = node.tag
        if tag in self._extra_flowables:
            return self._extra_flowables[tag](self, node, extra_style)
        else:
            return super(customized_rml_flowable, self)._flowable(node, extra_style)

# monkey patch the server _rml_flowable class with our, support custom
# extra_flowables :)
server_trml2pdf._rml_flowable = customized_rml_flowable

def customized_parseNode(rml, localcontext=None,fout=None, images=None, path='.',title=None, extra_flowables=None):
    node = etree.XML(rml)
    if localcontext is None:
        localcontext = {}
    if images is None:
        images = {}
    r = _rml_doc(node, localcontext, images, path, title=title)
    r._extra_flowables = extra_flowables
    #try to override some font mappings
    try:
        from report.render.rml2pdf.customfonts import SetCustomFonts
        SetCustomFonts(r)
    except ImportError:
        # means there is no custom fonts mapping in this system.
        pass
    except Exception:
        logging.getLogger('report').warning('Cannot set font mapping', exc_info=True)
        pass
    fp = StringIO()
    r.render(fp)
    return fp.getvalue()

class customized_rml(rml):
    def __init__(self, rml, localcontext = None, datas=None, path='.', title=None,
                        extra_flowables=None):
        super(customized_rml, self).__init__(rml, localcontext, datas, path, title)
        self.extra_flowables = extra_flowables

    def _render(self):
        return customized_parseNode(self.rml, self.localcontext,
                                    images=self.bin_datas, path=self.path,
                                    title=self.title,
                                    extra_flowables=self.extra_flowables)

class customized_report_sxw(report_sxw):
    _extra_flowables = {} # contains raw parser: { 'tag': tag_parser}
    _use_extra_flowables = [] # list of extra flowable to automatically register for this report

    def __init__(self, name, table, rml=False, parser=rml_parse, header=True, store=False):
        super(customized_report_sxw, self).__init__(name, table, rml, parser, header, store)
        if self._use_extra_flowables:
            for tag_name in self._use_extra_flowables:
                try:
                    tag_parser = trml2pdf_interface.get_tag(tag_name)
                    self._extra_flowables[tag_name] = tag_parser
                except Exception:
                    pass

    def create_pdf(self, rml, localcontext = None, logo=None, title=None):
        if not localcontext:
           localcontext = {}
        localcontext.update({'internal_header':self.internal_header})
        if logo:
            self.bin_datas['logo'] = logo
        else:
            if 'logo' in self.bin_datas:
                del self.bin_datas['logo']
        obj = customized_rml(rml, localcontext, self.bin_datas, self._get_path(), title,
                             extra_flowables=self._extra_flowables)
        obj.render()
        return obj.get()

class stored_checkbox_position_report_sxw(customized_report_sxw):
    """
    Report SXW which store checkbox position and participation_id
    (currently only working in the training's exam_sheet report)
    """

    def create_single_pdf(self, cr, uid, ids, data, report_xml, context=None):
        if not context:
            context={}
        logo = None
        context = context.copy()
        title = report_xml.name
        rml = report_xml.report_rml_content
        # if no rml file is found
        if not rml:
            return False
        rml_parser = self.parser(cr, uid, self.name2, context=context)
        objs = self.getObjects(cr, uid, ids, context)
        rml_parser.set_context(objs, data, ids, report_xml.report_type)
        processed_rml = etree.XML(rml)
        if report_xml.header:
            rml_parser._add_header(processed_rml, self.header)
        processed_rml = self.preprocess_rml(processed_rml,report_xml.report_type)
        if rml_parser.logo:
            logo = base64.decodestring(rml_parser.logo)
        create_doc = self.generators[report_xml.report_type]
        localcontext = rml_parser.localcontext
        pdf = create_doc(etree.tostring(processed_rml), localcontext, logo, title.encode('utf8'))
        if context.has_key('checkboxes_position'):
            context['checkboxes_position'].extend(localcontext['checkboxes_position'])
        if context.has_key('checkboxes_context'):
            context['checkboxes_context'].extend(localcontext['checkboxes_context'])
        if context.has_key('participation_id'):
            context['participation_id'].extend(localcontext['participation_id'])
        return (pdf, report_xml.report_type)

class TinyDocTemplate_WithPageHeader(TinyDocTemplate):
    def __init__(self, filename, **kw):
        self.extra_header = kw.get('extra_header', None) or None
        TinyDocTemplate.__init__(self, filename, **kw)

    def handle_pageBegin(self):
        TinyDocTemplate.handle_pageBegin(self)
        if self.extra_header:
            # add extra header just after coporate header
            # 1. we generate the flowable object from the rml node (etree)
            f = server_trml2pdf._rml_flowable(*self.extra_header['args'], **self.extra_header['kwargs'])
            r = f.render(self.extra_header['node'])
            # 2. we append it the current Frame
            self.handle_flowable(r)

class customized_rml_template(_rml_template):
    def __init__(self, localcontext, out, node, doc, images={}, path='.', title=None):
        if not localcontext:
            localcontext={'internal_header':True}
        self.localcontext = localcontext
        self.images= images
        self.path = path
        self.title = title

        if not node.get('pageSize'):
            pageSize = (utils.unit_get('21cm'), utils.unit_get('29.7cm'))
        else:
            ps = map(lambda x:x.strip(), node.get('pageSize').replace(')', '').replace('(', '').split(','))
            pageSize = ( utils.unit_get(ps[0]),utils.unit_get(ps[1]) )

        ## OVERRIDE BEGIN

        # search for and extra header (<pageHeader/> tag) in the rml file
        extra_header_node = node.find('pageHeader')
        extra_header = None
        if extra_header_node is not None:
            # extra header will be renderer on TinyDocTemplate.handle_pageBegin(), but
            # this function doesn't have the required element to call _rml_flowable()
            # so we prepare a dict containing all the required stuffs.
            r = report_preprocess() # we need that to correctly handle removeParentNode() calls
            extra_header = {
                'args': [ doc, self.localcontext ],
                'kwargs': {'images': self.images, 'path': self.path, 'title': self.title},
                'node': r.preprocess_rml(extra_header_node),
            }


        self.doc_tmpl = TinyDocTemplate_WithPageHeader(out, pagesize=pageSize, extra_header=extra_header, **utils.attr_get(node, ['leftMargin','rightMargin','topMargin','bottomMargin'], {'allowSplitting':'int','showBoundary':'bool','rotation':'int','title':'str','author':'str'}))

        if self.localcontext:
            self.localcontext.update({'rmldoc': self.doc_tmpl})

        ## OVERRIDE END
        self.page_templates = []
        self.styles = doc.styles
        self.doc = doc
        self.image=[]
        pts = node.findall('pageTemplate')
        for pt in pts:
            frames = []
            for frame_el in pt.findall('frame'):
                frame = platypus.Frame( **(utils.attr_get(frame_el, ['x1','y1', 'width','height', 'leftPadding', 'rightPadding', 'bottomPadding', 'topPadding'], {'id':'str', 'showBoundary':'bool'})) )
                if utils.attr_get(frame_el, ['last']):
                    frame.lastFrame = True
                frames.append( frame )
            try :
                gr = pt.findall('pageGraphics')\
                    or pt[1].findall('pageGraphics')
            except Exception: # FIXME: be even more specific, perhaps?
                gr=''
            if len(gr):
#                self.image=[ n for n in utils._child_get(gr[0], self) if n.tag=='image' or not self.localcontext]
                drw = _rml_draw(self.localcontext,gr[0], self.doc, images=images, path=self.path, title=self.title)
                self.page_templates.append( platypus.PageTemplate(frames=frames, onPage=drw.render, **utils.attr_get(pt, [], {'id':'str'}) ))
            else:
                drw = _rml_draw(self.localcontext,node,self.doc,title=self.title)
                self.page_templates.append( platypus.PageTemplate(frames=frames,onPage=drw.render, **utils.attr_get(pt, [], {'id':'str'}) ))
        self.doc_tmpl.addPageTemplates(self.page_templates)

server_trml2pdf._rml_template = customized_rml_template
