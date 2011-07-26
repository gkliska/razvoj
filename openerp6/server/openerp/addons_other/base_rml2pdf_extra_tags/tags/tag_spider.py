# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from reportlab.graphics.shapes import Circle
from tag_spider_internal import SpiderChart
from report.render.rml2pdf import utils
from base_rml2pdf_extra_tags.trml2pdf_interface import register_tag

def spider_parser(fobj, node, extra_style=None):
    attr_max = node.get('max', False)
    attr_display_scale = node.get('display_scale', False)
    attrs = utils.attr_get(node,
                        ['max', 'display_scale'],
                        {
                            'max': 'int',
                            'display_scale': 'bool',
                        })
    datas = eval(fobj._textual(node))

    domains = []
    ideal_values = []
    real_values = []

    for i in datas:
        if 'max' in attrs:
            scale = attrs['max'] / ((i[1] * 2) or i[3])
        else:
            scale = 1.0
        domains.append(i[0])
        ideal_values.append(i[1] * scale)
        real_values.append(i[2] * scale)

    ideal_values = tuple(ideal_values)
    real_values = tuple(real_values)

    from reportlab.graphics.charts.legends import Legend
    from reportlab.lib.colors import CMYKColor, PCMYKColor
    #colour names as comments at the end of each line are as a memory jogger ONLY
    #NOT HTML named colours!

    #Main colours as used for bars etc
    color01 = PCMYKColor(40,40,0,0, alpha=70)    # Lavender
    color02 = PCMYKColor(0,66,33,39, alpha=70)   # Maroon
    color03 = PCMYKColor(0,0,20,0)     # Yellow
    color04 = PCMYKColor(20,0,0,0)     # Cyan
    color05 = PCMYKColor(0,100,0,59)   # Purple
    color06 = PCMYKColor(0,49,49,0)    # Salmon
    color07 = PCMYKColor(100,49,0,19,alpha=50)  # Blue
    color08 = PCMYKColor(20,20,0,0)    # PaleLavender
    color09 = PCMYKColor(100,100,0,49) # NavyBlue
    color10 = PCMYKColor(0,100,0,0)    # Purple

    #Highlight colors - eg for the tops of bars
    color01Light = PCMYKColor(39,39,0,25)   # Light Lavender
    color02Light = PCMYKColor(0,66,33,54)   # Light Maroon
    color03Light = PCMYKColor(0,0,19,25)    # Light Yellow
    color04Light = PCMYKColor(19,0,0,25)    # Light Cyan
    color05Light = PCMYKColor(0,100,0,69)   # Light Purple
    color06Light = PCMYKColor(0,49,49,25)   # Light Salmon
    color07Light = PCMYKColor(100,49,0,39)  # Light Blue
    color08Light = PCMYKColor(19,19,0,25)   # Light PaleLavender
    color09Light = PCMYKColor(100,100,0,62) # Light NavyBlue
    color10Light = PCMYKColor(0,100,0,25)   # Light Purple

    #Lowlight colors - eg for the sides of bars
    color01Dark = PCMYKColor(39,39,0,49)   # Dark Lavender
    color02Dark = PCMYKColor(0,66,33,69)   # Dark Maroon
    color03Dark = PCMYKColor(0,0,20,49)    # Dark Yellow
    color04Dark = PCMYKColor(20,0,0,49)    # Dark Cyan
    color05Dark = PCMYKColor(0,100,0,80)   # Dark Purple
    color06Dark = PCMYKColor(0,50,50,49)   # Dark Salmon
    color07Dark = PCMYKColor(100,50,0,59)  # Dark Blue
    color08Dark = PCMYKColor(20,20,0,49)   # Dark PaleLavender
    color09Dark = PCMYKColor(100,100,0,79) # Dark NavyBlue
    color10Dark = PCMYKColor(0,100,0,49)   # Dark Purple

    #for standard grey backgrounds
    backgroundGrey = PCMYKColor(0,0,0,24)

    from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String
    from reportlab.graphics.charts.textlabels import Label

    class RadarChart(_DrawingEditorMixin,Drawing):
        def __init__(self,width=0,height=0,*args,**kw):
            vmax = kw.get('max', False)
            display_scale = kw.get('display_scale', True)

            if 'max' in kw:
                del kw['max']
            if 'display_scale' in kw:
                del kw['display_scale']

            apply(Drawing.__init__,(self,width,height)+args,kw)
            self._add(self,SpiderChart(),name='chart',validate=None,desc="The main chart")

            textInterval     = 30
            self.chart.width      = self.chart.height     = 250
            self.chart.x          = (535 / 2.0) - (self.chart.width / 2.0)
            self.chart.y          = -self.chart.width - textInterval

            ######################
            ## Peripheric Circle
            ######################
            XCenter = 535 / 2.0
            YCenter = self.chart.y / 2.0 - (textInterval / 2.0)
            rayon = self.chart.width / 2.0

            self._add(self, Circle(XCenter, YCenter, rayon, fillColor=None, strokeWidth = 0.4, strokeDashArray = (1,1)), name="Circle")
            #######################
            ## Intermediate Circles
            #######################

            # What is the max value ?
            valueMax = vmax and vmax or max(max(ideal_values), max(real_values))

            # And the space between each intermediate circle ?
            step = rayon / valueMax

            from math import radians, cos, sin
            from reportlab.graphics.shapes import String

            def placeNumber(angle, step, string):
                """return a string for number scale placement"""
                x = XCenter + (cos(radians(angle)) * step)
                y = YCenter + (sin(radians(angle)) * step)
                return String(x, y, string)

            # Let's go !!

            for i in range(1, int(valueMax)+1, 1):
                self._add(self, Circle(XCenter, YCenter, i * step, fillColor=None, strokeWidth = 0.2, strokeDashArray = (1, 1)), name="Circle")
                #if display_scale:
                self._add(self, placeNumber(45, step * i, "%d" % i))

            self.chart.vmax = valueMax
            self.chart.strands[0].strokeColor= color01
            self.chart.strands[1].strokeColor= color02
            self.chart.strands[0].fillColor  = color01
            self.chart.strands[1].fillColor  = color02
            #self.chart.strands.strokeWidth   = 1
            #self.chart.strandLabels.fontName = 'Helvetica'
            #self.chart.strandLabels.fontSize = 6
            #self.chart.fillColor             = backgroundGrey

            self.chart.data                  = [ideal_values, real_values]
            self.chart.labels                = domains

            self._add(self,Legend(),name='Legend',validate=None,desc="The legend or key for the chart")
            self.Legend.colorNamePairs = [(color01, 'Ideal Value'), (color02, 'Real Value')]
            self.Legend.fontName       = 'Helvetica'
            self.Legend.fontSize       = 7
            # placing Legend on the top-left of the graphic
            self.Legend.x              = 0
            self.Legend.y              = self.chart.y + self.chart.height
            self.Legend.dxTextSpace    = 5
            self.Legend.dy             = 5
            self.Legend.dx             = 5
            self.Legend.deltay         = 5
            self.Legend.alignment      ='right'

            self.chart.strands.strokeWidth     = 1
            self.chart.spokes.strokeDashArray = (1,1)       ## Dotted lines
            self._add(self,0,name='preview',validate=None,desc=None)

    return RadarChart(**attrs)

register_tag('spider', spider_parser)
