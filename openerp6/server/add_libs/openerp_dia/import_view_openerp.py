# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import pygtk
pygtk.require("2.0")
import gtk
import xmlrpclib
from lxml import etree
import sys, dia
import math

def warning(msg, type=gtk.MESSAGE_INFO):
    dialog = gtk.MessageDialog(None,
      gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
      type, gtk.BUTTONS_OK,
      msg)
    dialog.run()
    return dialog.destroy()


class window(object):
    def __init__(self):
        self.dia = gtk.Dialog(
            'Open ERP View',
            None,
            gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT
        )
        self.but_cancel = self.dia.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.but_ok = self.dia.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)

        table = gtk.Table(2,6)
        row = 0
        self.server = gtk.Entry()
        self.server.set_text('http://localhost:8069/xmlrpc')
        self.database = gtk.Entry()
        self.database.set_text('doc')
        self.login = gtk.Entry()
        self.login.set_text('admin')
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        col = 0
        for widget in [
            gtk.Label('Server URL: '), self.server,
            gtk.Label('Database: '), self.database,
            gtk.Label('Login: '), self.login,
            gtk.Label('Password: '), self.password,
        ]:
            table.attach(widget, col, col+1, row, row+1, yoptions=False, xoptions=gtk.FILL, ypadding=2)
            col += 1
            if col>1:
                col=0
                row+=1

        self.dia.vbox.pack_start(table, expand=True, fill=True)
        self.dia.show_all()

    def run(self):
        while True:
            res = self.dia.run()
            if res==gtk.RESPONSE_OK:
                if self.server.get_text().strip() == '':
                     warning('Invalid Server Name !')
                     continue
                _url = self.server.get_text() + '/common'
                sock = xmlrpclib.ServerProxy(_url)
                try:
                    db = self.database.get_text()
                    pa = self.password.get_text()
                    if pa in [None,''] or db.strip() in [None,'']:
                         warning('Authentication error !\nBad Database name or Password.')
                         continue
                    uid = None
                    try:
                        uid = sock.login(db, self.login.get_text(), pa)
                    except:
                        warning('Authentication error !\nInvalid User.')
                        continue                    
                    return uid, db, pa, self.server.get_text()
                except Exception, e:
                    warning('Unable to connect to the server')
                    continue
            self.destroy()
            break
        return False

    def destroy(self):
        self.dia.destroy()

class window2(object):
    def __init__(self, views, items):
        self.dia = gtk.Dialog(
            'Open ERP View',
            None,
            gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT
        )
        self.dia.set_property('default-width', 760)
        self.dia.set_property('default-height', 500)
        self.but_cancel = self.dia.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.but_ok = self.dia.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.views = views
        self.items = items
        self.treeview = gtk.TreeView()
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('View Name', cell, text=0)
        tvcolumn.set_sort_column_id(0)
        self.treeview.append_column(tvcolumn)
        cell1 = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('Object', cell1, text=1)
        tvcolumn.set_sort_column_id(1)
        self.treeview.append_column(tvcolumn)
        cell2 = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('View Type', cell2, text=2)
        tvcolumn.set_sort_column_id(2)
        self.treeview.append_column(tvcolumn)
        cell3 = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn('View ID', cell3, text=3)
        tvcolumn.set_sort_column_id(3)
        self.treeview.append_column(tvcolumn)
        views.sort()
        views.sort()
        self.liststore = gtk.ListStore(str,str,str,int)
        for v in views:
            self.liststore.append(v)
        self.treeview.set_model(self.liststore)    
            
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        sw.set_shadow_type(gtk.SHADOW_NONE)
        sw.add(self.treeview)
        model = gtk.ListStore(str,str)
        self.cb = gtk.ComboBoxEntry()
        table = gtk.Table(2,1)
        row = 0
        col = 0
        for widget in [
            gtk.Label('Language '), self.cb,
        ]:
            table.attach(widget, col, col+1, row, row+1, yoptions=2, xoptions=gtk.FILL, ypadding=2)
            col += 1
            if col>1:
                col=0
                row+=1        

        for i in items:
           model.append([i[0], i[1]])
           
        self.cb.set_model(model)
        self.cb.set_text_column(1)
        self.dia.vbox.pack_start(sw, expand=True, fill=True)
        self.dia.vbox.pack_start(gtk.HSeparator(),  expand=False, fill=False)
        self.dia.vbox.pack_start(table, expand=False, fill=False),
        self.dia.show_all()

    def run(self):
        while True:
            res = self.dia.run()
            model = self.cb.get_model()
            active = self.cb.get_active()
            if active < 0:
                return None
            res4 = model[active][0]

            if res==gtk.RESPONSE_OK:
                selection = self.treeview.get_selection()
                model,iter = selection.get_selected_rows()
                if iter:
                    iter = model.get_iter(iter[0])
                    res = model.get_value(iter,3)
                    res2 = model.get_value(iter,1)
                    res3 = model.get_value(iter,2)
                    self.destroy()
                    return res2, res, res3,  res4
            self.destroy()
            break
        return False

    def destroy(self):
        self.dia.destroy()
        
# self.sizes: a stack of containers (forms, groups, notebook, ...)
#   0- number of columns
#   1- total width of the upcomming element in group.notebook etc
#   2- x position (in pixels)
#   3- y position (in height pixels)
#   4- max Y (in pixels)        

class display(object):
    def __init__(self, view, default):
        self.view = view
        self.etree = etree.fromstring(view['arch'])
        self.select1 = self.select2 = []
        self.sizes = [[4 ,52 , 0 , 6, 8]]
        self.defaults = default
        self.shapes = {
            'form' : 'shape - head_title',
            'one2many_list': 'shape - one2many',
            'tree' : 'shape - tree_title',
            'label': 'Standard - Text',
        }
        self.attrs = {
            'form': {'group': True, 'label': False, 'colspan':4, 'height': 4},
            'tree': {'colspan':4},
            'search': {'group': True, 'label': False, 'colspan':16, 'height': 2},
            'group': {'group': True, 'display':False, 'label':False, 'height': 0},
            'notebook': {'group': True, 'display':False, 'label':False, 'height': 0, 'colspan':4},
            'page': {'group': True, 'label':False, 'height': 2, 'colspan':4},
        }
        self.fields = {
            'text': {'height': 4, 'style':{'text_alignment': 2}},
            'text_wiki': {'height': 4, 'style':{'text_alignment': 2}},
            'text_tag': {'height': 4, 'style':{'text_alignment': 2}},
            'one2many': {'height': 10, 'style':{'text_alignment': 0, 'text_font' : 'Helvetica-Bold'}}, # text_font attrib is raising error
            'many2many': {'height': 10, 'style':{'text_alignment': 0}},
            'one2many_form': {'height': 10, 'style':{'text_alignment': 0}},
            'one2many_list': {'height': 10, 'style':{'text_alignment': 0}},
        }

    def draw_element(self, x,y, sizex, sizey, shape, properties, default = None):
        shape = {
            'shape - page': 'shape - notebook_path'
        }.get(shape, shape)
        if type(default) == type(1) and shape == 'shape - boolean':
            shape = 'shape - boolean_on'
        if shape:
            oType = dia.get_object_type (shape)
            o, h1, h2 = oType.create(0,0)
            if ('elem_width'  and 'elem_height' ) in o.properties.keys():
                o.properties['elem_width'] = sizex
                o.properties['elem_height'] = sizey
            for k,v in properties.items():
                    o.properties[k] = v
            o.move(x,y)
            self.data.active_layer.add_object(o)
            
        if default and type(default) != type(1):
            oType = dia.get_object_type ('Standard - Text')
            o, h1, h2 = oType.create(x+0.25,y+1.25)
            o.properties['text'] = str(default)
            self.data.active_layer.add_object(o)
            
    def process_node(self, element, posx=0, posy=0):
        label = element.attrib.get('string','')
        default = None
        colspan = int(element.attrib.get('colspan',self.attrs.get(element.tag, {}).get('colspan', 1)))
        labelspan = 0
        attrs = {
            'text_alignment': 0,
            'text_colour': "#000000",
            'text_height': 1,
        }
        height = self.attrs.get(element.tag, {}).get('height', 2)
        if element.tag=='newline':
           return 0, self.sizes[-1][-1]
        shape = False
        if element.tag=='field':
            field_name = element.attrib.get('name')
            attr = self.view['fields'][field_name]
            attr.update(element.attrib)
            if attr.get('required',0):
                attrs['fill_colour'] = "#DDDDFF"
            if attr.get('readonly',0):
                attrs['fill_colour'] = "#EEEEEE"

            nolabel = int(attr.get('nolabel',0))
            if not nolabel:
                posx+=1
                labelspan = 1
                if attr.get('colspan', 0):
                    colspan = int(attr.get('colspan', 0)) - 1
            if not label:
                label = self.view['fields'][field_name]['string']
            if nolabel:
                label = ""
            if field_name in self.defaults and len(self.defaults):
                default = self.defaults[field_name]
                
            shape_type = self.view['fields'][field_name]['type']
            if shape_type == 'many2one':
                if self.view['fields'][field_name].has_key('widget'):
                    shape_type = self.view['fields'][field_name]['widget']
            shape = self.shapes.get(shape_type,'shape - '+shape_type)
            height = self.fields.get(shape_type, {}).get('height', 2)
            label = label and label + ' : '
            attrs['text_alignment'] =self.fields.get(shape_type, {}).get('style',{}).get('text_alignment',2)
        else:
            attrs['text_alignment'] = 0
            shape = self.shapes.get(element.tag,'shape - '+element.tag)

        attrs['text'] = label
        
        colsize = self.sizes[-1][1] / float(self.sizes[-1][0])
        if colspan == 0:
            colspan = 1
        size = colsize * colspan

        if posx+colspan > self.sizes[-1][0]:
            posx = labelspan
            posy = self.sizes[-1][-1]
        self.sizes[-1][-1] = max(self.sizes[-1][-1], posy + height)
            
        pos_x = posx * colsize  + self.sizes[-1][2]
        pos_y = posy
        if self.attrs.get(element.tag, {}).get('display', True):
             if element.tag == 'button':
                element_icon = element.attrib.get('icon',False)
                attrs['text_alignment'] = 1
                if element_icon.startswith("terp"):
                      element_icon = element_icon[5:]  
                self.draw_element(pos_x, pos_y, size, height, shape, attrs, default)
                if element_icon:
                    shape_icon = self.shapes.get(element_icon,'shape - '+ element_icon) 
                    self.draw_element(pos_x, pos_y+0.5, 1, 1, shape_icon, {})
             else:
                self.draw_element(pos_x, pos_y, size, height, shape, attrs, default)

        posx += colspan

        if element.tag in self.attrs:
            if self.attrs[element.tag].get('group', False):
                col = int(element.attrib.get('col',4))
                self.sizes.append([col, size, pos_x, pos_y, pos_y+height])
                posx2 = 0
                posy2 = posy + height
                for e in element.getchildren():
                    try:
                        posx2,posy2 = self.process_node(e, posx2, posy2)
                    except:
                        pass    
                self.sizes[-2][-1] = max(self.sizes[-2][-1],  self.sizes[-1][-1])
                self.sizes.pop()
            
        return posx,posy
            
    def process_search(self, element, posx=0, posy=0):
        label = element.attrib.get('string','')
        attrs = {
            'text_alignment': 0,
            'text_colour': "#000000",
        }
        height = self.attrs.get(element.tag, {}).get('height', 2)
        shape = self.shapes.get(element.tag,'shape - '+element.tag)
        colspan = int(element.attrib.get('colspan',self.attrs.get(element.tag, {}).get('colspan', 1)))
        pos_x = posx
        pos_y = posy
        labelspan=0
        default=None
        if element.tag == 'search':
            self.draw_element(pos_x, pos_y, self.sizes[-1][1], height, 'shape - '+element.tag, {},label)
            posx = pos_x
            posy = pos_y
            
        if element.tag=='newline':
            posx = 0
            posy += 2
        if element.tag == 'separator':
            posx = pos_x+1
            posy = pos_y

        if element.tag == 'filter':
            icon = element.attrib.get('icon',False)
            self.draw_element(pos_x-2, pos_y, self.sizes[-1][1], height, 'shape - '+element.tag, {},label)
            if icon: 
                if icon.startswith("terp"):
                      icon = icon[5:]     
                shape_icon = self.shapes.get(icon,'shape - '+icon) 
                self.draw_element(pos_x-0.5, pos_y, 0.8, 0.8, shape_icon, {})

            posx = pos_x+4
            posy = pos_y
        
        if element.tag == 'group':
            label = element.attrib.get('string','')
            if label == "Extended Filters...":
                self.draw_element(0, pos_y+0.5, self.sizes[-1][1] , 1.4, 'shape - search_group', {}, label)
                posx += 0
                posy += 2
            if label == "Group By...":
                self.draw_element(0, pos_y+0.5, self.sizes[-1][1] , 1.4, 'shape - search_group', {}, label)    
                posx += 0
                posy += 2
                
        if element.tag=='field':
            field_name = element.attrib.get('name')
            attr = self.view['fields'][field_name]
            attr.update(element.attrib)
            if attr.get('required',0):
                attrs['fill_colour'] = "#DDDDFF"
            if attr.get('readonly',0):
                attrs['fill_colour'] = "#EEEEEE"

            nolabel = int(attr.get('nolabel',0))
            if not nolabel:
                posx+=1
                labelspan = 1
                if attr.get('colspan', 0):
                    colspan = int(attr.get('colspan', 0)) - 1

            if not label:
                label = self.view['fields'][field_name]['string']
            if nolabel:
                label = ""
            if field_name in self.defaults and len(self.defaults):
                default = self.defaults[field_name]
                
            shape_type = self.view['fields'][field_name]['type']
            if shape_type == 'many2one':
                if self.view['fields'][field_name].has_key('widget'):
                    shape_type = self.view['fields'][field_name]['widget']
            shape = self.shapes.get(shape_type,'shape - '+shape_type)
            height = self.fields.get(shape_type, {}).get('height', 2)
            label = label and label + ' : '
            attrs['text_alignment'] = self.fields.get(shape_type, {}).get('style',{}).get('text_alignment',2)
            attrs['text'] = label
            colsize = self.sizes[-1][1] / float(self.sizes[-1][0])
            if colspan == 0:
                colspan = 2
            size = colsize * colspan - 3
            pos_x = posx * colsize  + self.sizes[-1][2] 
            pos_y = posy 
            if posx == 1:
                posx = 5
            if shape_type in ['one2many', 'many2many']:
                shape = self.shapes.get(shape_type,'shape - char')
                height = 2
                attrs.update({'text_alignment':2})
            if self.attrs.get(element.tag, {}).get('display', True):
                self.draw_element(posx, posy, size, height, shape, attrs, default)
            posx += (len(label)/2) + 3
            posy = pos_y

        if element.tag in self.attrs:
            col = int(element.attrib.get('col',6))
            self.sizes.append([col, self.sizes[-1][1], pos_x, pos_y, pos_y+height])
            posx2 = pos_x+2
            posy2 = posy + height
            for e in element.getchildren():
                try:
                    posx2,posy2 = self.process_search(e, posx2, posy2)
                except:
                    pass    
                posx=posx2
                posy=posy2 
            self.sizes[-2][-1] = max(self.sizes[-2][-1],  self.sizes[-1][-1])
        return posx, posy

   
    def process_tree(self, element, posx=0, posy=0):
        label = element.attrib.get('string','')
        attrs = {
            'text_alignment': 0,
            'text_colour': "#000000",
        }
        height = self.attrs.get(element.tag, {}).get('height', 2)
        shape = self.shapes.get(element.tag,'shape - '+element.tag)
        pos_x = posx
        pos_y = posy
        attrs['text'] = label
        if element.tag=='tree':
            attrs['text_colour'] =  "#000000"
            self.draw_element(0, pos_y+4, self.sizes[-1][1], 15, 'shape - o2m_m2m', {})
            self.draw_element(3, pos_y+4, self.sizes[-1][1], 15, None, attrs, label)
        elif element.tag=='field':
            field_name = element.attrib.get('name')
            label = self.view['fields'][field_name]['string']
            attrs['text_alignment'] = 0
            attrs['text_height'] = 0
            self.draw_element(pos_x, pos_y+4, self.sizes[-1][1] , height, None, attrs, label)
            posx = posx + len(label)/2
            
        if element.tag in self.attrs:
            col = int(element.attrib.get('col',4))
            self.sizes.append([col, self.sizes[-1][1], pos_x, pos_y, pos_y+height])
            posx2 = 0
            posy2 = posy + height
            for e in element.getchildren():
                try:
                    posx2,posy2 = self.process_tree(e, posx2, posy2)
                except:
                    pass    
            self.sizes[-2][-1] = max(self.sizes[-2][-1],  self.sizes[-1][-1])
                
        return posx,posy
    
    def draw(self, data, flags, type, x=0, y=0):
        self.data = data
        self.flags = flags
        self.draw_element(0, 0, 60, 5, 'shape - head_logo', {})
        if type == 'form':
            self.process_node(self.etree, x, y)
        if type == 'tree':
            self.process_tree(self.etree, x, y)
        if type == 'search':
            x, y = self.process_search(self.etree, 0,5)
            self.draw_element(0, y+2.2, 30, 2, 'shape - search_view_botton', {})
        if 'toolbar' in self.view:
            k = 6
            for data in ('print', 'action', 'relate'):
                if not self.view['toolbar'][data]:
                    continue
                self.draw_element(52, k, 11, 1.8 , 'shape - right_toolbar_header', {
                    'text': data.upper(),
                    'text_alignment': 0,
                    'text_colour': "#000000",
                })
                k += 1.8
                for relate in self.view['toolbar'][data] :
                     self.draw_element(52, k, 11, 1.8 , 'shape - right_toolbar_text', {
                        'text': relate['string'],
                        'text_alignment': 0
                     })
                     k += 1.6
            self.draw_element(52, k, 11, 35.8 , 'shape - right_toolbar_bottom', {
                'text_alignment': 0
                })
        self.data.active_layer.update_extents()
        return x,y

def view_get(sock,db, uid, password, model, type, domain):
    try:
        ids = sock.execute(db, uid, password, model, type, domain)
        views = sock.execute(db, uid, password, 'ir.ui.view', 'read', ids, ['name','type','model'])
        ids_lang = sock.execute(db, uid, password, 'res.lang', 'search', [],{})
        items = sock.execute(db, uid, password, 'res.lang', 'read', ids_lang, ['code','name'])
    except Exception, e:
        warning('Error!\nPlease Check the server configuration again.') 
    view_lst = map(lambda x: (x['name'],x['model'],x['type'],x['id']), views)
    item_lst = map(lambda x: (x['code'],x['name']), items)
    win = window2(view_lst, item_lst)
    result = win.run()
    s_views = None
    if result:
        model, view_id, view_type, lang = result   
        s_views = sock.execute(db, uid, password, model, 'fields_view_get', view_id, view_type, {'lang': lang})
    return s_views


def main(data=True, flags=True, draw=True):
    posx, posy = 0,5
    win = window()
    result = win.run()
    win.destroy()
    if result:
        uid, db, password, server= result
        _url = server + '/object'
        sock = xmlrpclib.ServerProxy(_url)
        views = view_get(sock,db, uid, password, 'ir.ui.view', 'search', [('inherit_id','=',False),('type','in',('form','tree','search'))])
        defaults ={}
        if views:
            fields = views['fields']
            for field in fields:
                default = sock.execute(db, uid, password, views.get('model', False), 'default_get',[field])
                if len(default) and default[field]:
                    if fields[field]['type'] == 'many2one':
                        val = sock.execute(db, uid, password, fields[field]['relation'], 'read', default[field], ['name'])['name']
                        default[field] = val
                    defaults.update(default)
            if views.get('type', False) == 'tree':
                search_views = view_get(sock, db, uid, password, 'ir.ui.view', 'search',  [('model','=', views.get('model',False)),('type','=','search')])
                if search_views:
                    d = display(search_views, defaults)
                    if draw:
                       posx, posy =  d.draw(data, flags,search_views.get('type', False), posx, posx)
            d = display(views, defaults)
            if draw:
                d.draw(data, flags,views.get('type', False), posx,posy)


if __name__=='__main__':
    main(draw =False)


def main2(data, flags):
    layer = data.active_layer
    oType = dia.get_object_type ("shape - char") 
    o, h1, h2 = oType.create (1.4,7.95)
    layer.add_object(o)

dia.register_callback ("Load Open ERP View", 
                       "<Display>/Tools/Load Open ERP View", 
                       main)
