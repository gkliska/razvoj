# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_tax
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#    Contributions: 
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

from osv import fields, osv, orm


class product_category(osv.osv):
    
    _inherit = "product.category"
    _columns = {
        'code': fields.char('Code', size=64, select=1),
        
        'purchase_tax_ids': fields.many2many('account.tax', 'category_purchase_tax_rel',
                                              'category_id','tax_id', 'Porezi nabave',
                                              domain=[('parent_id', '=', False),('type_tax_use','in',['purchase','all'])],
                                              help="It is much easier to handle taxes on product categories."),
        'sale_tax_ids': fields.many2many('account.tax', 'category_sale_tax_rel',
                                         'category_id', 'tax_id',  'Porezi prodaje',
                                         domain=[('parent_id', '=', False),('type_tax_use','in',['sale','all'])]
                                         ),
                
        'account_expense2_categ_id': fields.many2one('account.account', "Expense Account 2",
                                    help="Alternative account for product can be used to value part of tax base expenses for this product category"),
        'account_income2_categ_id': fields.many2one('account.account', "Income Account 2",
                                    help="Alternative account for product can be used to value part of nondeductable tax base sales for this product category"),

        }
product_category()

def std_price_digits(dig):
    return (16,dig)
class product_template(osv.osv):
    def get_prec_price():
        def change_digit_price(cr):
            res = pooler.get_pool(cr.dbname).get('decimal.precision').precision_get(cr, 1, 'Account')
            return (16, res+4)
        return change_digit_price
    
    _inherit = 'product.template'
    _columns = {
        'account_income2_id': fields.many2one('account.account', "Income Account 2",
                                                        help="This account will be used for invoices to value part of nondeductable tax base sales for the current product category"),
        'account_expense2_id': fields.many2one('account.account', "Expense Account 2",
                                                        help="This account will be used for invoices to value part of nondeductable tax base expenses for the current product category"),

        'account_map_ids': fields.one2many('product.account.map', 'product_id', 'Account Mapping'),
   
    }
    

    def get_product_accounts_ids(self, cr, uid, product_id, context=None):
        res={}
        #res = super( product_product ,self).get_product_accounts( cr, uid, product_id, context=None)
        product_obj = self.pool.get('product.template')
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)

        if product:
            # from account
            a = product.product_tmpl_id.property_account_income.id
            if not a:
                a = product.categ_id.property_account_income_categ.id
            res['account_income'] = a

            a = product.product_tmpl_id.property_account_expense.id
            if not a:
                a = product.categ_id.property_account_expense_categ.id
            res['account_expense'] = a
            
            #from account
            a = product.product_tmpl_id.account_income2_id.id
            if not a:
                a = product.categ_id.account_income2_categ_id.id
            res['account_income_base2_id'] = a

            a = product.product_tmpl_id.account_expense2_id.id
            if not a:
                a = product.categ_id.account_expense2_categ_id.id
            res['account_expense_base2_id'] = a

            # from module stock
            """
            stock_input_acc = product_obj.property_stock_account_input and product_obj.property_stock_account_input.id or False
            if not stock_input_acc:
                stock_input_acc = product_obj.categ_id.property_stock_account_input_categ and product_obj.categ_id.property_stock_account_input_categ.id or False
    
            stock_output_acc = product_obj.property_stock_account_output and product_obj.property_stock_account_output.id or False
            if not stock_output_acc:
                stock_output_acc = product_obj.categ_id.property_stock_account_output_categ and product_obj.categ_id.property_stock_account_output_categ.id or False
    
            journal_id = product_obj.categ_id.property_stock_journal and product_obj.categ_id.property_stock_journal.id or False
            account_variation = product_obj.categ_id.property_stock_variation and product_obj.categ_id.property_stock_variation.id or False
    
            return {
                'stock_account_input': stock_input_acc,
                'stock_account_output': stock_output_acc,
                'stock_journal': journal_id,
                'property_stock_variation': account_variation
            }
            """
        return res 

    def map_account(self, cr, uid, product_id, account_id, context=None):
        if not product_id:
            return account_id
        if type(product_id) == type(1): #int 
           product = self.pool.get('product.template').browse(cr, uid, product_id, context=context)
        else:
           product =  product_id  
        #if not product: return account_id
        for pos in product.account_map_ids:
            if pos.account_src_id.id == account_id:
                account_id = pos.account_dest_id.id
                break
        return account_id


product_template()    

class product_account_map(osv.osv):
    _name = 'product.account.map'
    _description = 'Product Account Mapping'
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('product.template', 'Product', required=True, ondelete='cascade'),
        'account_src_id': fields.many2one('account.account', 'Account Source', required=True),
        'account_dest_id': fields.many2one('account.account', 'Account Destination', domain=[('type','!=','view'),('type','!=','consolidation')], required=True)
    }


product_account_map()
