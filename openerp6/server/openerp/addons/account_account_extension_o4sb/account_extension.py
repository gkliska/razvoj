# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution - module extension
#    Copyright (C) 2010- O4SB (<http://openforsmallbusiness.co.nz>).
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

from osv import fields,osv
from tools.translate import _


class account_account_type(osv.osv):
    _inherit = 'account.account.type'
    
    _columns = {
        'report_type':fields.selection([
        ('none','/'),
        ('income','Profit & Loss (Operating Income Accounts)'),
        ('cogs', 'Profit & Loss (Cost of Goods Sold Accounts)'),
        ('expense','Profit & Loss (Operating Expense Accounts)'),
        ('other_income', 'Profit & Loss (Other Income Accounts)'),
        ('other_expense', 'Profit & Loss (Other Expense Accounts)'),
        ('asset','Balance Sheet (Current Asset Accounts)'),
        ('fixed_asset', 'Balance Sheet (Non Current Asset Accounts'),
        ('liability','Balance Sheet (Current Liability Accounts)'),
        ('fixed_liability', 'Balance Sheet (Non Current Liability Accounts)'),
        ('equity', 'Balance Sheet (Equity Accounts)'),
        ],'P&L / BS Category', select=True, readonly=False, help="According value related accounts will be display on respective reports (Balance Sheet Profit & Loss Account)", required=True),
    }

account_account_type()

class res_company(osv.osv):
    _inherit = 'res.company' 

    _columns = {
        'short_name': fields.char('Company Short Name', size = 8, help = 'This name is used to append to Journal names in automatic installers')
    }

res_company()

class wizard_multi_charts_accounts(osv.osv_memory):
    _inherit = 'wizard.multi.charts.accounts'
    
    _columns = {
        'code_digits': fields.integer('# of Digits', required=False, help="No. of Digits to use for account code"),
        'sep_multi_seq': fields.boolean('Separated Company Sequences', help='Check this if you wish to create new sequences for this company.  If unchecked, it will reuse existing/create default sequences.  If checked the sequences will be prepended with the company id which can later be changed'),
        'prefix': fields.char('Acct Code Prefix', size=4, help='This prefix will be appended to all accounts to enable them to be easily differentiated in a multicompany environment'),
        'suffix': fields.char('Acct Code Suffix', size=4, help='This suffix will be appended to all accounts to enable them to be easily differentiated in a multicompany environment')
    }
    
    _defaults = {
        'code_digits': 0,
        }
    
    def onchange_chart_template_id(self, cr, uid, ids, chart_template_id=False, context=None):
        res = super(wizard_multi_charts_accounts, self).onchange_chart_template_id(cr, uid, ids, chart_template_id=chart_template_id, context=context)
        if chart_template_id:
            obj_acc_template = self.pool.get('account.account.template')
            chart_template_bank = self.pool.get('account.chart.template').browse(cr, uid, chart_template_id, context).bank_account_view_id.id
            bank_account_ids = obj_acc_template.search(cr, uid, [('parent_id', '=', chart_template_bank), ('type', '=', 'liquidity')])
            if not bank_account_ids:
                return res
            accounts = obj_acc_template.browse(cr, uid, bank_account_ids, context)
            bank_account_details = []
            for account in accounts:
                if account.name.lower().find('cash') != -1 or account.name.lower().find(_('cash')) != -1:
                    type = 'cash'
                else:
                    type = 'bank'                 
                bank_details = {'acc_name': account.name, 'acc_code': account.code, 'account_type': type}
                if account.currency_id:
                    bank_details.update({'currency_id': currency_id})
                bank_account_details.append(bank_details)       
            res['value'].update({'bank_accounts_id': bank_account_details})
        return res
    
    def execute(self, cr, uid, ids, context=None):
        obj_multi = self.browse(cr, uid, ids[0])
        obj_acc = self.pool.get('account.account')
        obj_acc_tax = self.pool.get('account.tax')
        obj_journal = self.pool.get('account.journal')
        obj_sequence = self.pool.get('ir.sequence')
        obj_acc_template = self.pool.get('account.account.template')
        obj_fiscal_position_template = self.pool.get('account.fiscal.position.template')
        obj_fiscal_position = self.pool.get('account.fiscal.position')
        obj_data = self.pool.get('ir.model.data')
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        obj_tax_code = self.pool.get('account.tax.code')
        # Creating Account
        obj_acc_root = obj_multi.chart_template_id.account_root_id
        tax_code_root_id = obj_multi.chart_template_id.tax_code_root_id.id
        company_id = obj_multi.company_id.id
        if obj_multi.sep_multi_seq:            
            company_id2 = str(company_id)
            company_short = obj_multi.company_id.short_name or company_id2
        else:
            company_id2 = ''
            company_short =''

        #new code
        acc_template_ref = {}
        tax_template_ref = {}
        tax_code_template_ref = {}
        todo_dict = {}
        ref_acc_bank = obj_multi.chart_template_id.bank_account_view_id

        #create all the tax code
        children_tax_code_template = self.pool.get('account.tax.code.template').search(cr, uid, [('parent_id','child_of',[tax_code_root_id])], order='id')
        children_tax_code_template.sort()
        for tax_code_template in self.pool.get('account.tax.code.template').browse(cr, uid, children_tax_code_template, context=context):
            vals={
                'name': (tax_code_root_id == tax_code_template.id) and obj_multi.company_id.name or tax_code_template.name,
                'code': tax_code_template.code,
                'info': tax_code_template.info,
                'parent_id': tax_code_template.parent_id and ((tax_code_template.parent_id.id in tax_code_template_ref) and tax_code_template_ref[tax_code_template.parent_id.id]) or False,
                'company_id': company_id,
                'sign': tax_code_template.sign,
            }
            new_tax_code = obj_tax_code.create(cr, uid, vals)
            #recording the new tax code to do the mapping
            tax_code_template_ref[tax_code_template.id] = new_tax_code

        #create all the tax
        tax_template_to_tax = {}
        for tax in obj_multi.chart_template_id.tax_template_ids:
            #create it
            vals_tax = {
                'name':tax.name,
                'sequence': tax.sequence,
                'amount':tax.amount,
                'type':tax.type,
                'applicable_type': tax.applicable_type,
                'domain':tax.domain,
                'parent_id': tax.parent_id and ((tax.parent_id.id in tax_template_ref) and tax_template_ref[tax.parent_id.id]) or False,
                'child_depend': tax.child_depend,
                'python_compute': tax.python_compute,
                'python_compute_inv': tax.python_compute_inv,
                'python_applicable': tax.python_applicable,
                'base_code_id': tax.base_code_id and ((tax.base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.base_code_id.id]) or False,
                'tax_code_id': tax.tax_code_id and ((tax.tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.tax_code_id.id]) or False,
                'base_sign': tax.base_sign,
                'tax_sign': tax.tax_sign,
                'ref_base_code_id': tax.ref_base_code_id and ((tax.ref_base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_base_code_id.id]) or False,
                'ref_tax_code_id': tax.ref_tax_code_id and ((tax.ref_tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_tax_code_id.id]) or False,
                'ref_base_sign': tax.ref_base_sign,
                'ref_tax_sign': tax.ref_tax_sign,
                'include_base_amount': tax.include_base_amount,
                'description':tax.description,
                'company_id': company_id,
                'type_tax_use': tax.type_tax_use,
                'price_include': tax.price_include
            }
            new_tax = obj_acc_tax.create(cr, uid, vals_tax)
            tax_template_to_tax[tax.id] = new_tax
            #as the accounts have not been created yet, we have to wait before filling these fields
            todo_dict[new_tax] = {
                'account_collected_id': tax.account_collected_id and tax.account_collected_id.id or False,
                'account_paid_id': tax.account_paid_id and tax.account_paid_id.id or False,
            }
            tax_template_ref[tax.id] = new_tax

        #deactivate the parent_store functionality on account_account for rapidity purpose
        ctx = context and context.copy() or {}
        ctx['defer_parent_store_computation'] = True

        children_acc_template = obj_acc_template.search(cr, uid, [('parent_id','child_of',[obj_acc_root.id]),('nocreate','!=',True)])
        children_acc_template.sort()
        for account_template in obj_acc_template.browse(cr, uid, children_acc_template,context=context):
            tax_ids = []
            for tax in account_template.tax_ids:
                tax_ids.append(tax_template_ref[tax.id])
            #create the account_account

            dig = obj_multi.code_digits or 0
            suf = obj_multi.suffix or ''
            pre = obj_multi.prefix or ''
            code_acc = pre + account_template.code + suf or ''
            code_main = account_template.code and len(code_acc) or 0
            if code_main>0 and code_main<=dig and account_template.type != 'view':
                code_acc=str(code_acc) + (str('0'*(dig-code_main)))
            vals={
                'name': (obj_acc_root.id == account_template.id) and obj_multi.company_id.name or account_template.name,
                'currency_id': account_template.currency_id and account_template.currency_id.id or False,
                'code': code_acc,
                'type': account_template.type,
                'user_type': account_template.user_type and account_template.user_type.id or False,
                'reconcile': account_template.reconcile,
                'shortcut': account_template.shortcut,
                'note': account_template.note,
                'parent_id': account_template.parent_id and ((account_template.parent_id.id in acc_template_ref) and acc_template_ref[account_template.parent_id.id]) or False,
                'tax_ids': [(6,0,tax_ids)],
                'company_id': company_id,
            }
            new_account = obj_acc.create(cr, uid, vals, context=ctx)
            acc_template_ref[account_template.id] = new_account
        #reactivate the parent_store functionality on account_account
        self.pool.get('account.account')._parent_store_compute(cr)

        for key,value in todo_dict.items():
            if value['account_collected_id'] or value['account_paid_id']:
                obj_acc_tax.write(cr, uid, [key], {
                    'account_collected_id': acc_template_ref.get(value['account_collected_id'], False),
                    'account_paid_id': acc_template_ref.get(value['account_paid_id'], False),
                })

        # Creating Journals Sales and Purchase
        vals_journal={}
        data_id = obj_data.search(cr, uid, [('model','=','account.journal.view'), ('name','=','account_sp_journal_view')])
        data = obj_data.browse(cr, uid, data_id[0], context=context)
        view_id = data.res_id

        seq_id = obj_sequence.search(cr, uid, [('name','=','Account Journal')])[0]
        if obj_multi.sep_multi_seq:
            seq = obj_sequence.browse(cr, uid, seq_id)
            seq_id = obj_sequence.copy(cr, uid, seq_id)
            obj_sequence.write(cr, uid, seq_id, {'company_id': company_id, 'prefix': (seq.prefix or '') + company_id2, 'name': company_short + (seq.name or '')})

        if obj_multi.seq_journal:
            seq_id_sale = obj_sequence.search(cr, uid, [('name','=','Sale Journal')])[0]
            seq_id_purchase = obj_sequence.search(cr, uid, [('name','=','Purchase Journal')])[0]
            seq_id_sale_refund = obj_sequence.search(cr, uid, [('name','=','Sales Refund Journal')])
            if seq_id_sale_refund:
                seq_id_sale_refund = seq_id_sale_refund[0]
            seq_id_purchase_refund = obj_sequence.search(cr, uid, [('name','=','Purchase Refund Journal')])
            if seq_id_purchase_refund:
                seq_id_purchase_refund = seq_id_purchase_refund[0]
            #Todo make this a loop - probably requies making the previous section a loop
            if obj_multi.sep_multi_seq:
                seq = obj_sequence.browse(cr, uid, seq_id_sale)
                seq_id_sale = obj_sequence.copy(cr, uid, seq.id)
                obj_sequence.write(cr, uid, seq_id_sale, {'company_id': company_id, 'prefix': (seq.prefix or '') + company_id2, 'name': company_short + (seq.name or ''),})
                seq = obj_sequence.browse(cr, uid, seq_id_purchase)
                seq_id_purchase = obj_sequence.copy(cr, uid, seq.id)
                obj_sequence.write(cr, uid, seq_id_purchase, {'company_id': company_id, 'prefix': (seq.prefix or '') + company_id2, 'name': company_short + (seq.name or ''),})
                if seq_id_sale_refund:
                    seq = obj_sequence.browse(cr, uid, seq_id_sale_refund)
                    seq_id_sale_refund = obj_sequence.copy(cr, uid, seq.id)
                    obj_sequence.write(cr, uid, seq_id_sale_refund, {'company_id': company_id, 'prefix': (seq.prefix or '') + company_id2, 'name': company_short + (seq.name or ''),})
                if seq_id_purchase_refund:
                    seq = obj_sequence.browse(cr, uid, seq_id_purchase_refund)
                    seq_id_purchase_refund = obj_sequence.copy(cr, uid, seq.id)
                    obj_sequence.write(cr, uid, seq_id_purchase_refund, {'company_id': company_id, 'prefix': (seq.prefix or '') + company_id2, 'name': company_short + (seq.name or ''),})
            
        else:
            seq_id_sale = seq_id
            seq_id_purchase = seq_id
            seq_id_sale_refund = seq_id
            seq_id_purchase_refund = seq_id

        vals_journal['view_id'] = view_id
        

        #Sales Journal
        analytical_sale_ids = analytic_journal_obj.search(cr,uid,[('type','=','sale'),('company_id', '=', company_id)])
        analytical_journal_sale = analytical_sale_ids and analytical_sale_ids[0] or False

        vals_journal['name'] = _('%s Sales Journal') % company_short
        vals_journal['type'] = 'sale'
        vals_journal['code'] = _('SAJ%s') % company_id2
        vals_journal['sequence_id'] = seq_id_sale
        vals_journal['company_id'] =  company_id
        vals_journal['analytic_journal_id'] = analytical_journal_sale

        if obj_multi.chart_template_id.property_account_receivable:
            vals_journal['default_credit_account_id'] = acc_template_ref[obj_multi.chart_template_id.property_account_income_categ.id]
            vals_journal['default_debit_account_id'] = acc_template_ref[obj_multi.chart_template_id.property_account_income_categ.id]

        obj_journal.create(cr,uid,vals_journal)

        # Purchase Journal
        analytical_purchase_ids = analytic_journal_obj.search(cr,uid,[('type','=','purchase'), ('company_id', '=', company_id)])
        analytical_journal_purchase = analytical_purchase_ids and analytical_purchase_ids[0] or False

        vals_journal['name'] =  _('%s Purchase Journal') % company_short
        vals_journal['type'] = 'purchase'
        vals_journal['code'] = _('EXJ%s') % company_id2
        vals_journal['sequence_id'] = seq_id_purchase
        vals_journal['view_id'] = view_id
        vals_journal['company_id'] =  company_id
        vals_journal['analytic_journal_id'] = analytical_journal_purchase

        if obj_multi.chart_template_id.property_account_payable:
            vals_journal['default_credit_account_id'] = acc_template_ref[obj_multi.chart_template_id.property_account_expense_categ.id]
            vals_journal['default_debit_account_id'] = acc_template_ref[obj_multi.chart_template_id.property_account_expense_categ.id]

        obj_journal.create(cr,uid,vals_journal)

        # Creating Journals Sales Refund and Purchase Refund
        vals_journal = {}
        data_id = obj_data.search(cr, uid, [('model', '=', 'account.journal.view'), ('name', '=', 'account_sp_refund_journal_view')], context=context)
        data = obj_data.browse(cr, uid, data_id[0], context=context)
        view_id = data.res_id

        #Sales Refund Journal
        vals_journal = {
            'view_id': view_id,
            'name': _('%s Sales Refund Journal') % company_short,
            'type': 'sale_refund',
            'refund_journal': True,
            'code': _('SCNJ%s') % company_id2,
            'sequence_id': seq_id_sale_refund,
            'analytic_journal_id': analytical_journal_sale,
            'company_id': company_id
        }

        if obj_multi.chart_template_id.property_account_receivable:
            vals_journal['default_credit_account_id'] = acc_template_ref[obj_multi.chart_template_id.property_account_income_categ.id]
            vals_journal['default_debit_account_id'] = acc_template_ref[obj_multi.chart_template_id.property_account_income_categ.id]

        obj_journal.create(cr, uid, vals_journal, context=context)

        # Purchase Refund Journal
        vals_journal = {
            'view_id': view_id,
            'name': _('%s Purchase Refund Journal') % company_short,
            'type': 'purchase_refund',
            'refund_journal': True,
            'code': _('ECNJ%s') % company_id2,
            'sequence_id': seq_id_purchase_refund,
            'analytic_journal_id': analytical_journal_purchase,
            'company_id': company_id
        }

        if obj_multi.chart_template_id.property_account_payable:
            vals_journal['default_credit_account_id'] = acc_template_ref[obj_multi.chart_template_id.property_account_expense_categ.id]
            vals_journal['default_debit_account_id'] = acc_template_ref[obj_multi.chart_template_id.property_account_expense_categ.id]

        obj_journal.create(cr, uid, vals_journal, context=context)

        # Bank Journals
        data_id = obj_data.search(cr, uid, [('model','=','account.journal.view'), ('name','=','account_journal_bank_view')])
        data = obj_data.browse(cr, uid, data_id[0], context=context)
        view_id_cash = data.res_id

        data_id = obj_data.search(cr, uid, [('model','=','account.journal.view'), ('name','=','account_journal_bank_view_multi')])
        data = obj_data.browse(cr, uid, data_id[0], context=context)
        view_id_cur = data.res_id


        current_num = 1
        current_num_bank = 1
        current_num_cash = 1
        for line in obj_multi.bank_accounts_id:
            #create the account_account for this bank journal if required
            tmp = line.acc_name
            acc_cash_id = False
            if line.acc_code:
                template_id = obj_acc_template.search(cr, uid, [('code', '=', line.acc_code), ('type', '=', 'liquidity')])[0]
                acc_cash_id = acc_template_ref.get(template_id, False)
                vals = {'name': line.acc_name}
            if not acc_cash_id:
                if ref_acc_bank.code:
                    new_code = pre + str(ref_acc_bank.code) + suf + str('%d' % current_num)
                    new_main = len(new_code)
                    if new_main>0 and new_main<=dig:
                        new_code = str(new_code) + (str('0'*(dig-new_main)))
                vals = {
                    'name': tmp,
                    'currency_id': line.currency_id and line.currency_id.id or False,
                    'code': new_code,
                    'type': 'liquidity',
                    'user_type': account_template.user_type and account_template.user_type.id or False,
                    'reconcile': True,
                    'parent_id': acc_template_ref[ref_acc_bank.id] or False,
                    'company_id': company_id,
                }
                acc_cash_id  = obj_acc.create(cr,uid,vals)

            if obj_multi.seq_journal:
                if obj_multi.sep_multi_seq:
                    vals_seq={
                        'name': _('%s Bank Journal %s') % (company_short, vals['name']),
                        'code': 'account.journal',
                        'prefix': str(company_id)
                    }
                    if line.account_type == 'cash':
                        vals_seq.update({'name': _('%s Cash Journal %s') % (company_short, vals['name']) })
                else:
                    vals_seq={
                        'name': _('Bank Journal %s') % vals['name'],
                        'code': 'account.journal',
                    }
                    if line.account_type == 'cash':
                        vals_seq.update({'name': _('Cash Journal %s') % vals['name']})
                seq_id = obj_sequence.create(cr,uid,vals_seq)

            #create the bank journal
            analytical_bank_ids = analytic_journal_obj.search(cr,uid,[('type','=','situation'), ('company_id', '=', company_id)])
            analytical_journal_bank = analytical_bank_ids and analytical_bank_ids[0] or False

            vals_journal['name']= vals['name']
            if line.account_type == 'cash':
                vals_journal['code'] = _('CASH%d') % current_num_cash
                current_num_cash += 1
            else:
                vals_journal['code']= _('BNK%d') % current_num_bank
                current_num_bank +=1
            vals_journal['sequence_id'] = seq_id
            vals_journal['type'] = line.account_type == 'cash' and 'cash' or 'bank'
            vals_journal['company_id'] =  company_id
            vals_journal['analytic_journal_id'] = analytical_journal_bank

            if line.currency_id:
                vals_journal['view_id'] = view_id_cur
                vals_journal['currency'] = line.currency_id.id
            else:
                vals_journal['view_id'] = view_id_cash
            vals_journal['default_credit_account_id'] = acc_cash_id
            vals_journal['default_debit_account_id'] = acc_cash_id
            obj_journal.create(cr, uid, vals_journal)
            current_num += 1

        #create the properties
        property_obj = self.pool.get('ir.property')
        fields_obj = self.pool.get('ir.model.fields')

        todo_list = [
            ('property_account_receivable','res.partner','account.account'),
            ('property_account_payable','res.partner','account.account'),
            ('property_account_expense_categ','product.category','account.account'),
            ('property_account_income_categ','product.category','account.account'),
            ('property_account_expense','product.template','account.account'),
            ('property_account_income','product.template','account.account'),
            ('property_reserve_and_surplus_account','res.company','account.account')
        ]
        for record in todo_list:
            r = []
            r = property_obj.search(cr, uid, [('name','=', record[0] ),('company_id','=',company_id)])
            account = getattr(obj_multi.chart_template_id, record[0])
            field = fields_obj.search(cr, uid, [('name','=',record[0]),('model','=',record[1]),('relation','=',record[2])])
            vals = {
                'name': record[0],
                'company_id': company_id,
                'fields_id': field[0],
                'value': account and 'account.account,'+str(acc_template_ref[account.id]) or False,
            }

            if r:
                #the property exist: modify it
                property_obj.write(cr, uid, r, vals)
            else:
                #create the property
                property_obj.create(cr, uid, vals)

        fp_ids = obj_fiscal_position_template.search(cr, uid, [('chart_template_id', '=', obj_multi.chart_template_id.id)])

        if fp_ids:

            obj_tax_fp = self.pool.get('account.fiscal.position.tax')
            obj_ac_fp = self.pool.get('account.fiscal.position.account')

            for position in obj_fiscal_position_template.browse(cr, uid, fp_ids, context=context):

                vals_fp = {
                    'company_id': company_id,
                    'name': position.name,
                }
                new_fp = obj_fiscal_position.create(cr, uid, vals_fp)

                for tax in position.tax_ids:
                    vals_tax = {
                        'tax_src_id': tax_template_ref[tax.tax_src_id.id],
                        'tax_dest_id': tax.tax_dest_id and tax_template_ref[tax.tax_dest_id.id] or False,
                        'position_id': new_fp,
                    }
                    obj_tax_fp.create(cr, uid, vals_tax)

                for acc in position.account_ids:
                    vals_acc = {
                        'account_src_id': acc_template_ref[acc.account_src_id.id],
                        'account_dest_id': acc_template_ref[acc.account_dest_id.id],
                        'position_id': new_fp,
                    }
                    obj_ac_fp.create(cr, uid, vals_acc)

        ir_values = self.pool.get('ir.values')
        if obj_multi.sale_tax:
            ir_values.set(cr, uid, key='default', key2=False, name="taxes_id", company=obj_multi.company_id.id,
                            models =[('product.product',False)], value=[tax_template_to_tax[obj_multi.sale_tax.id]])
        if obj_multi.purchase_tax:
            ir_values.set(cr, uid, key='default', key2=False, name="supplier_taxes_id", company=obj_multi.company_id.id,
                            models =[('product.product',False)], value=[tax_template_to_tax[obj_multi.purchase_tax.id]])

wizard_multi_charts_accounts()

class account_bank_accounts_wizard(osv.osv_memory):
    _inherit = 'account.bank.accounts.wizard'

    _columns = {
        'acc_code': fields.char('Account Code', size=64),
        }

account_bank_accounts_wizard()





