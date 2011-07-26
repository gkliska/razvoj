# -*- coding: utf-8 -*-
# Copyright 2011 Thamini S.à.R.L    This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

#Autogenerated by ReportLab guiedit do not edit
from reportlab.graphics.charts.legends import Legend, _getWidths
from reportlab.graphics.charts.barcharts import HorizontalBarChart, HorizontalBarChart3D
from reportlab.graphics.charts.barcharts import VerticalBarChart, VerticalBarChart3D
from reportlab.graphics.charts.axes import CategoryAxis, ValueAxis
from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, String
from reportlab.graphics.charts.textlabels import Label
from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from report.render.rml2pdf import color
#from excelcolors import *

def get_color(value):
    if value.startswith('#'):
        return HexColor(value)
    return color.get(value)

def get_label_size(l):
    l.computeSize()
    return (l._right - l._left, l._top - l._bottom)

class MyHorizontalBarChart(HorizontalBarChart):
    pass

class MyVerticalBarChart(VerticalBarChart):
    _flip_barlabel = False

    def _addLabel(self, text, label, g, rowNo, colNo, x, y, width, height):
        if self._flip_barlabel:
            label.angle = 90
            label.boxAnchor = 'w'
        if label.visible:
            labelWidth = stringWidth(text, label.fontName, label.fontSize)
            flipXY = self._flipXY
            if flipXY:
                y0, x0, pm = self._labelXY(label,y,x,height,width)
            else:
                x0, y0, pm = self._labelXY(label,x,y,width,height)
            fixedEnd = getattr(label,'fixedEnd', None)
            if fixedEnd is not None:
                v = fixedEnd._getValue(self,pm)
                x00, y00 = x0, y0
                if flipXY:
                    x0 = v
                else:
                    y0 = v
            else:
                if flipXY:
                    x00 = x0
                    y00 = y+height/2.0
                else:
                    x00 = x+width/2.0
                    y00 = y0
            fixedStart = getattr(label,'fixedStart', None)
            if fixedStart is not None:
                v = fixedStart._getValue(self,pm)
                if flipXY:
                    x00 = v
                else:
                    y00 = v
            if pm<0:
                if flipXY:
                    dx = -2*label.dx
                    dy = 0
                else:
                    dy = -2*label.dy
                    dx = 0
            else:
                dy = dx = 0
            label.setOrigin(x0+dx, y0+dy)
            label.setText(text)
            sC, sW = label.lineStrokeColor, label.lineStrokeWidth
            if sC and sW: g.insert(0,Line(x00,y00,x0,y0, strokeColor=sC, strokeWidth=sW))
            g.add(label)
            alx = getattr(self,'barLabelCallOut',None)
            if alx:
                label._callOutInfo = (self,g,rowNo,colNo,x,y,width,height,x00,y00,x0,y0)
                alx(label)
                del label._callOutInfo

class Barchart(_DrawingEditorMixin,Drawing):
    def __init__(self,data,width=200,height=150,orientation='horizontal',fontName='Helvetica', fontSize=10, xticks=3,yticks=3, valueMax=None, legend_display='c',stacked=False, flip_barlabel=False, *args,**kw):
        Drawing.__init__(self,width,height,*args,**kw)

        chart = orientation == 'horizontal' and MyHorizontalBarChart() or MyVerticalBarChart()
        if flip_barlabel:
            chart._flip_barlabel = True

        xaxis = orientation == 'horizontal' and chart.valueAxis or chart.categoryAxis
        yaxis = orientation == 'horizontal' and chart.categoryAxis or chart.valueAxis
        self._add(self,chart,name='chart',validate=None,desc="The main chart")

        chart_x = 0
        chart_y = 0
        chart_width = width
        chart_height = height

        if data.get('title',''):
            self._add(self,Label(),name='Title',validate=None,desc="The title at the top of the chart")
            self.Title.fontName = 'Helvetica-Bold'
            self.Title.fontSize = fontSize + 2
            self.Title.textAnchor = 'middle'
            self.Title._text = data.get('title','')
            title_w, title_h = get_label_size(self.Title)
            self.Title.y = chart_y + chart_height - title_h
            self.Title.x = chart_x + (chart_width / 2.)
            self.Title.maxWidth   = chart_width
            chart_height -= title_h + 10

        if legend_display.strip():
            self._add(self,Legend(),name='Legend',validate=None,desc="The legend or key for the chart")
            colorNamePairs = [ (get_color(x['color']), x['name']) for x in data['values'] ]
            legend = self.Legend
            legend.colorNamePairs = colorNamePairs
            legend.columnMaximum = 10
            legend.fontName = fontName
            legend.fontSize = fontSize
            legend.dxTextSpace = 5
            legend.dy = 5
            legend.dx = 5
            legend.deltay = 5
            legend.alignment = 'right'
            legend.variColumn = 0
            legend.boxAnchor = 'c'
            legend.x = chart_width
            legend.y = chart_height / 2.

            # calc legend width
            maxWidth = legend._calculateMaxBoundaries(colorNamePairs)
            xW = legend.dx+legend.dxTextSpace+legend.autoXPadding
            deltax = max(maxWidth[-1]+xW,legend.deltax)
            nCols = int((len(colorNamePairs)+legend.columnMaximum-1)/(legend.columnMaximum*1.0))
            lwidth = legend.dx + nCols*deltax
            chart_width -= lwidth

        if data.get('xlabel',''):
            self._add(self,Label(),name='XLabel',validate=None,desc="The label on the horizontal axis")
            self.XLabel.fontName = 'Helvetica-Bold'
            self.XLabel.fontSize = fontSize
            self.XLabel.textAnchor = 'middle'
            self.XLabel._text = data.get('xlabel','')
            xlabel_w, xlabel_h = get_label_size(self.XLabel)
            self.XLabel.x = chart_x + (chart_width / 2.0)
            self.XLabel.y = chart_y + (xlabel_h / 2.)
            chart_y += xlabel_h
            chart_height -= xlabel_h

        if data.get('ylabel', ''):
            self._add(self,Label(),name='YLabel',validate=None,desc="The label on the vertical axis")
            self.YLabel.fontName = 'Helvetica-Bold'
            self.YLabel.fontSize = fontSize
            self.YLabel.angle = 90
            self.YLabel.textAnchor = 'middle'
            self.YLabel._text = data.get('ylabel','')
            ylabel_w, ylabel_h = get_label_size(self.YLabel)
            self.YLabel.x = (ylabel_h / 2.)
            self.YLabel.y = chart_x + (chart_height / 2.)
            self.YLabel.maxWidth = chart_height
            self.YLabel.height = ylabel_h
            chart_x += ylabel_h
            chart_width -= ylabel_h

        # make global configuration to the chart
        self.chart.barWidth = 20
        for i, vdesc in enumerate(data['values']):
            self.chart.bars[i].fillColor = get_color(vdesc['color'])
#        self.chart.fillColor         = backgroundGrey
        self.chart.data = data['datas']
        self.chart.groupSpacing = 8

        if data.get('datas_label',[]):
            self.chart.barLabels.fontName = fontName
            self.chart.barLabels.fontSize = fontSize - 3
            self.chart.barLabels.boxAnchor = 'n'
            self.chart.barLabelFormat = 'values'
            self.chart.barLabelArray = data.get('datas_label',[])

        # configure axis
        xaxis.tickDown = xticks
        yaxis.tickLeft = yticks

        self.chart.valueAxis.labels.fontName = fontName
        self.chart.valueAxis.labels.fontSize = fontSize
        self.chart.valueAxis.forceZero = 1
        self.chart.valueAxis.avoidBoundFrac = 1
        self.chart.valueAxis.visibleGrid = 1 # make this an option
        if valueMax is not None:
            self.chart.valueAxis.valueMax = valueMax

        if stacked:
            self.chart.categoryAxis.style = 'stacked'
        self.chart.categoryAxis.categoryNames = [ x['name'] for x in data['categories'] ]
        self.chart.categoryAxis.labels.fontName       = fontName
        self.chart.categoryAxis.labels.fontSize       = fontSize
        self.chart.categoryAxis.labels.dx             = -3
        self.chart.categoryAxis.labels.boxAnchor = 'autox'
        self.chart.categoryAxis.labels.angle = -45

        self.chart.x = 1000
        self.chart.y = 1000
        self.chart._getConfigureData()
        def get_axis_label_count(a):
            if isinstance(a, CategoryAxis):
                return a._catCount
            if isinstance(a, ValueAxis):
                return len(a._tickValues)
            raise Exception("invalid axis data")
        xaxis.configure(self.chart._configureData)
        xaxis_count = get_axis_label_count(xaxis)
        xaxis_g = xaxis.makeTickLabels()
        xaxis_bd = xaxis_g.getBounds()
        if xaxis_bd is not None:
            xh = xaxis_bd[3] - xaxis_bd[1]
            chart_y += xh
            chart_height -= xh
            del xaxis_bd
            del xaxis_g
            if data.get('ylabel',''):
                self.YLabel.y += xh / 2.
        yaxis.configure(self.chart._configureData)
        yaxis_count = get_axis_label_count(yaxis)
        yaxis_g = yaxis.makeTickLabels()
        yaxis_bd = yaxis.getBounds()
        if yaxis_bd is not None:
            yw = yaxis_bd[2] - yaxis_bd[0]
            chart_x += yw
            chart_width -= yw
            del yaxis_bd
            del yaxis_g
            if data.get('xlabel',''):
                self.XLabel.x += yw

        # force chart position and size depending of elements flying around
        self.chart.width      = chart_width
        self.chart.height     = chart_height
        self.chart.x          = chart_x
        self.chart.y          = chart_y

        self._add(self,0,name='preview',validate=None,desc=None)

if __name__=="__main__": #NORUNTESTS
    COLOR_PALETTE = ['#f57900', '#cc0000', '#d400a8', '#75507b', '#3465a4', '#73d216', '#c17d11', '#edd400',
                     '#fcaf3e', '#ef2929', '#ff00c9', '#ad7fa8', '#729fcf', '#8ae234', '#e9b96e', '#fce94f',
                     '#ff8e00', '#ff0000', '#b0008c', '#9000ff', '#0078ff', '#00ff00', '#e6ff00', '#ffff00',
                     '#905000', '#9b0000', '#840067', '#510090', '#0000c9', '#009b00', '#9abe00', '#ffc900',]
    data = {
        'categories': [
            {'name': 'Conventions nationales & internationales'},
            {'name': 'OPC'},
            {'name': 'Back office titres'},
            {'name': 'Obligations'},
            {'name': 'Actions'},
            {'name': 'Comptes et moyens de paiement'},
            {'name': 'Crédits aux particuliers'},
            {'name': 'Comptabilité générale'},
            {'name': 'Déontologie'},
            {'name': 'Activité bancaire'},
        ],
        'values': [
            {'name': 'N1 / Niveau 1', 'color': COLOR_PALETTE[0]},
            {'name': 'N2 / Niveau 2', 'color': COLOR_PALETTE[1]},
            {'name': 'N3 / Niveau 3', 'color': COLOR_PALETTE[2]},
        ],
        'datas': [
            (10, 10, 10, 10, 10, 10, 10, 10, 10, 10),
            (30, 30, 30, 30, 30, 30, 30, 30, 30, 30),
            (5, 5, 5, 5, 5, 5, 5, 5, 5, 5),
        ],
        'datas_label': [
            ('10', '10', '10', '10', '10', '10', '10', '10', '10', '10'),
            ('30', '30', '30', '30', '30', '30', '30', '30', '30', '30'),
            ('5', '5', '5', '5', '5', '5', '5', '5', '5', '5'),
        ],
#        'title': 'Domain Barchart',
#        'xlabel': 'Domains',
#        'ylabel': 'Score',
    }
    bc = Barchart(data, orientation='vertical', xticks=3, yticks=3,
                    width=1240, height=1024, fontSize=24)
    bc.save(formats=['pdf'],outDir=None,fnRoot='tag_barchart')
