# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


####     MIRAR DEPENDENCIAS

from osv import osv
from osv import fields
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import time

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import netsvc

class sale_order(osv.osv):


                                
    def create_planning(self, cr, uid, ids, *args):                      
        
        def calculate_aux_date(aux_date, frecuency_type, vez=0):
            if frecuency_type == 'biweekly':                
                if vez==0:
                    aux_date = aux_date + timedelta(days=31)                                        
                    aux_date = date(aux_date.year, aux_date.month, 1)
                else:                                                        
                    aux_date = date(aux_date.year, aux_date.month, 15)
            elif frecuency_type == 'monthly':
                aux_date = aux_date + timedelta(days=31)
                aux_date = date(aux_date.year, aux_date.month, 1)
            elif frecuency_type == 'bimonthly':
                aux_date = aux_date + timedelta(days=62)
                aux_date = date(aux_date.year, aux_date.month, 1)
            elif frecuency_type == 'quarterly':
                aux_date = aux_date + timedelta(days=93)
                aux_date = date(aux_date.year, aux_date.month, 1)
            elif frecuency_type == 'four-monthly':
                aux_date = aux_date + timedelta(days=124)
                aux_date = date(aux_date.year, aux_date.month, 1)
            elif frecuency_type == 'semiannual':
                aux_date = aux_date + timedelta(days=183)
                aux_date = date(aux_date.year, aux_date.month, 1)
            elif frecuency_type == 'annual':
                aux_date = aux_date + timedelta(days=365)
                aux_date = date(aux_date.year, aux_date.month, 1)     
            return aux_date
        
        
        
        def get_order_id(order,aux_date):
            result = self.pool.get('sale.order').search(cr, uid, [('date_order','=',aux_date),('partner_id','=',order.partner_id.id),('name','like',order.name)])
            if result:
                result = result[0]
            else:
                result = self.pool.get('sale.order').create(cr, uid, {
                               'name': order.name + ' - ' + aux_date.strftime("%d/%m/%Y"),
                               'shop_id': order.shop_id.id,
                               'origin': order.origin,
                               'client_order_ref': order.client_order_ref,
                               'date_order': aux_date,
                               'user_id': order.user_id.id,
                               'partner_id': order.partner_id.id,
                               'partner_invoice_id': order.partner_invoice_id.id,
                               'partner_order_id': order.partner_order_id.id,
                               'partner_shipping_id': order.partner_shipping_id.id,
                               'incoterm': order.incoterm,
                               'picking_policy': order.picking_policy,
                               'order_policy': order.order_policy,
                               'pricelist_id': order.pricelist_id.id,
                               'project_id': order.project_id.id,
                               })   
            return result
        
        for order in self.browse(cr, uid, ids, context={}):

            aux_date_order = datetime.strptime(order.date_order[0:10], "%Y-%m-%d").date()
            if aux_date_order.day<29:
                aux_date_order = aux_date_order + timedelta(days=30)
            else:
                aux_date_order = aux_date_order + timedelta(days=15)
                
           
            cont = 0
            for line in order.order_line:
                aux_date = date(aux_date_order.year, aux_date_order.month, 1) 
                cont = 0
                aux_duration = order.plan_duration
                if line.frecuency == 'biweekly':
                    aux_sales = 2 * aux_duration
                                       
                    for i in range(aux_sales):
                        cont += 1                        
                        order_id = get_order_id(order,aux_date)                         
                        self.pool.get('sale.order.line').create(cr, uid, {
                            'order_id': order_id,
                            'name': line.name,
                            'delay': line.delay,
                            'product_id': line.product_id.id,
                            'price_unit': line.price_unit,
                            'product_uom_qty': 1,
                            'product_uom': line.product_uom.id,
                            })
                        aux_date = calculate_aux_date(aux_date, line.frecuency, cont % 2)                             
                        
                        

                
                
                elif line.frecuency == 'monthly':
                    aux_sales = aux_duration
                    for i in range(aux_sales):
                            cont += 1
                            order_id = get_order_id(order,aux_date)
                            self.pool.get('sale.order.line').create(cr, uid, {
                            'order_id': order_id,
                            'name': line.name,
                            'delay': line.delay,
                            'product_id': line.product_id.id,
                            'price_unit': line.price_unit,
                            'product_uom_qty': 1,
                            'product_uom': line.product_uom.id,
                            })                            
                            aux_date = calculate_aux_date(aux_date, line.frecuency)
                    
                        
                elif line.frecuency == 'bimonthly':                    
                    aux_sales = aux_duration / 2
                    for i in range(aux_sales):                            
                            order_id = get_order_id(order,aux_date)
                            self.pool.get('sale.order.line').create(cr, uid, {
                            'order_id': order_id,
                            'name': line.name,
                            'delay': line.delay,
                            'product_id': line.product_id.id,
                            'price_unit': line.price_unit,
                            'product_uom_qty': 1,
                            'product_uom': line.product_uom.id,
                            })                            
                            aux_date = calculate_aux_date(aux_date, line.frecuency)
                    
                            
                elif line.frecuency == 'quarterly':
                    aux_sales = aux_duration / 3                    
                    for i in range(aux_sales):                            
                            cont += 1
                            order_id = get_order_id(order,aux_date)
                            self.pool.get('sale.order.line').create(cr, uid, {
                            'order_id': order_id,
                            'name': line.name,
                            'delay': line.delay,
                            'product_id': line.product_id.id,
                            'price_unit': line.price_unit,
                            'product_uom_qty': 1,
                            'product_uom': line.product_uom.id,
                            })                            
                            aux_date = calculate_aux_date(aux_date, line.frecuency)
                    

                elif line.frecuency == 'four-monthly':
                    aux_sales = aux_duration / 4                    
                    for i in range(aux_sales):
                            cont += 1
                            order_id = get_order_id(order,aux_date)
                            self.pool.get('sale.order.line').create(cr, uid, {
                            'order_id': order_id,
                            'name': line.name,
                            'delay': line.delay,
                            'product_id': line.product_id.id,
                            'price_unit': line.price_unit,
                            'product_uom_qty': 1,
                            'product_uom': line.product_uom.id,
                            })                            
                            aux_date = calculate_aux_date(aux_date, line.frecuency)
                    

                elif line.frecuency == 'semiannual':
                    aux_sales = aux_duration / 6                    
                    for i in range(aux_sales):
                            cont += 1
                            order_id = get_order_id(order,aux_date)
                            self.pool.get('sale.order.line').create(cr, uid, {
                            'order_id': order_id,
                            'name': line.name,
                            'delay': line.delay,
                            'product_id': line.product_id.id,
                            'price_unit': line.price_unit,
                            'product_uom_qty': 1,
                            'product_uom': line.product_uom.id,
                            })                            
                            aux_date = calculate_aux_date(aux_date, line.frecuency)
                    
                            
                elif line.frecuency == 'annual':
                    aux_sales = aux_duration / 12
                    for i in range(aux_sales):
                            cont += 1
                            order_id = get_order_id(order,aux_date)
                            self.pool.get('sale.order.line').create(cr, uid, {
                            'order_id': order_id,
                            'name': line.name,
                            'delay': line.delay,
                            'product_id': line.product_id.id,
                            'price_unit': line.price_unit,
                            'product_uom_qty': 1,
                            'product_uom': line.product_uom.id,
                            })                            
                            aux_date = calculate_aux_date(aux_date, line.frecuency)
                    
            if order.order_line:
                self.write(cr, uid, ids, {'state': 'planned', 'name': order.name + " - planned"})
   
            return True
        
    _name = 'sale.order'
    _inherit = 'sale.order'
    _columns = {
             'state': fields.selection([
            ('planned', 'planning done'),
            ('draft', 'Quotation'),
            ('waiting_date', 'Waiting Schedule'),
            ('mannual', 'Mannual In Progress'),
            ('progress', 'In Progress'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
            ], 'Order State', readonly=True, help="Gives the state of the quotation or sale order. The exception state is automatically set when a cancel operation occurs in the invoice validation (Invoice Exception) or in the packing list process (Shipping Exception). The 'Waiting Schedule' state is set when the invoice is confirmed but waiting for the scheduler to run on the date 'Date Ordered'.", select=True),
        'date_order':fields.date('Date Ordered', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'plan_duration': fields.integer('Duration (Months)'),
    }


    _defaults = {
        'plan_duration': lambda *a: 12
    }
       
                           
sale_order()

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'
    _columns = {
                'frecuency': fields.selection((('punctual', 'Punctual'), ('biweekly', 'Planificación quincenal'), ('monthly', 'Planificación mensual'), ('bimonthly', 'Bimonthly planning'), ('quarterly', 'Quarterly planning'), ('four-monthly', 'Four-monthly planning'), ('semiannual', 'Semiannual planning'), ('annual', 'Annual planning')), 'Planning frecuency'),
    }
    _defaults = {
                 'frecuency' : lambda * a:'punctual'
                 }
    def frecuency_change(self, cr, uid, ids, frecuency_type, duration):
        quantity=1
        if not frecuency_type:
            return {}
        else:
            if frecuency_type == 'biweekly':
                quantity=duration * 2
            if frecuency_type == 'monthly':
                quantity=duration
            elif frecuency_type == 'bimonthly':
                quantity=duration / 2
            elif frecuency_type == 'quarterly':
                quantity=duration / 3
            elif frecuency_type == 'four-monthly':
                quantity=duration / 4
            elif frecuency_type == 'semiannual':
                quantity=duration / 6
            elif frecuency_type == 'annual':
                quantity=duration / 12
            return {'value':{'product_uom_qty':quantity}}
    
sale_order_line()