# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (c) 2011 Noviat nv/sa (www.noviat.be). All rights reserved.
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

import time
from osv import osv, fields
import netsvc
from tools.translate import _
logger=netsvc.Logger()

def _format_iban(string):
    '''
    This function removes all characters from given 'string' that isn't a alpha numeric and converts it to upper case.
    '''
    res = ""
    for char in string:
        if char.isalnum():
            res += char.upper()
    return res

class account_journal(osv.osv):
    _inherit = 'account.journal'
    
    _columns = {
        'coda_bank_acc': fields.char('Bank Account Number', size=34, 
                help="Bank Account Number, used for bank journals."
                     "\nThe CODA import function will find the bank journal based on this number."),
                     
        'coda_st_naming': fields.char('Bank Statement Naming Policy', size=64,
            help="Define the rules to create the name of the Bank Statements generated by the CODA processing." \
                 "\nE.g. %(code)s%(y)s/%(paper)s"     
                 "\n\nVariables:" \
                 "\nBank Journal Code: %(code)s" \
                 "\nCurrent Year with Century: %(year)s" \
                 "\nCurrent Year without Century: %(y)s" \
                 "\nCODA sequence number: %(coda)s" \
                 "\nPaper Statement sequence number: %(paper)s"),
    }
    _defaults = {
        'coda_st_naming': lambda *a: '%(code)s/%(coda)s',
    }
    _sql_constraints = [('acc_uniq','unique(coda_bank_acc)', 'This Bank Account Number has already been assigned to another Journal.')]    
    
    def create(self, cr, uid, vals, context=None):
        #overwrite to format the iban number correctly
        if 'coda_bank_acc' in vals and vals['coda_bank_acc']:
            vals['coda_bank_acc'] = _format_iban(vals['coda_bank_acc'])
        return super(account_journal, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        #overwrite to format the iban number correctly
        if 'coda_bank_acc' in vals and vals['coda_bank_acc']:
            vals['coda_bank_acc'] = _format_iban(vals['coda_bank_acc'])
        return super(account_journal, self).write(cr, uid, ids, vals, context)    
    
account_journal()


class account_coda(osv.osv):
    _name = 'account.coda'
    _description = 'Object to store CODA Data Files'
    _order = 'coda_creation_date desc'
    _columns = {
        'name': fields.char('CODA Filename',size=128, readonly=True),
        'coda_data': fields.binary('CODA File', readonly=True),
        'statement_ids': fields.one2many('coda.bank.statement','coda_id','Generated CODA Bank Statements', readonly=True),
        'note': fields.text('Import Log', readonly=True),
        'coda_creation_date': fields.date('CODA Creation Date', readonly=True, select=True),
        'date': fields.date('Import Date', readonly=True, select=True),
        'user_id': fields.many2one('res.users','User', readonly=True, select=True),
        'company_id': fields.many2one('res.company', 'Company', readonly=True)
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'user_id': lambda self,cr,uid,context: uid,
        'company_id': lambda s,cr,uid,c: s.pool.get('res.company')._company_default_get(cr, uid, 'account.coda', context=c),
    }        
    _sql_constraints = [
        ('coda_uniq', 'unique (name, coda_creation_date)', 'This CODA has already been imported !')
    ]  

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        coda_st_obj = self.pool.get('coda.bank.statement')
        for coda in self.browse(cr, uid, ids, context=context):
            for coda_statement in coda.statement_ids:
                if coda_statement.state == 'done':
                    coda_st_obj.action_cancel(cr, uid, [coda_statement.id], context=context) 
        return super(account_coda, self).unlink(cr, uid, ids, context=context)
  
account_coda()

class account_coda_trans_type(osv.osv):  
    _name = 'account.coda.trans.type'
    _description = 'CODA transaction type'
    _rec_name = 'type' 
    _columns = {
        'type': fields.char('Transaction Type', size=1, required=True),
        'parent_id': fields.many2one('account.coda.trans.type', 'Parent'),
        'description': fields.text('Description', translate=True),
    }
account_coda_trans_type()

class account_coda_trans_code(osv.osv):  
    _name = 'account.coda.trans.code'
    _description = 'CODA transaction code'
    _rec_name = 'code' 
    _columns = {
        'code': fields.char('Code', size=2, required=True, select=1),
        'type': fields.selection([
                ('code', 'Transaction Code'),
                ('family', 'Transaction Family')], 
                'Type', required=True, select=1), 
        'parent_id': fields.many2one('account.coda.trans.code', 'Family', select=1),
        'description': fields.char('Description', size=128, translate=True, select=2),
        'comment': fields.text('Comment', translate=True),
    }
account_coda_trans_code()

class account_coda_trans_category(osv.osv):  
    _name = 'account.coda.trans.category'
    _description = 'CODA transaction category'
    _rec_name = 'category' 
    _columns = {
        'category': fields.char('Transaction Category', size=3, required=True),
        'description': fields.char('Description', size=256, translate=True),
    }
account_coda_trans_category()

class account_coda_comm_type(osv.osv):  
    _name = 'account.coda.comm.type'
    _description = 'CODA structured communication type'
    _rec_name = 'code' 
    _columns = {
        'code': fields.char('Structured Communication Type', size=3, required=True, select=1),
        'description': fields.char('Description', size=128, translate=True),
    }
    _sql_constraints = [
        ('code_uniq', 'unique (code)','The Structured Communication Code must be unique !')
        ]
account_coda_comm_type()

class coda_bank_statement(osv.osv):
    _name = 'coda.bank.statement' 
    _description = 'CODA Bank Statement'    
    
    def _default_journal_id(self, cr, uid, context={}):
        if context.get('journal_id', False):
            return context['journal_id']
        return False

    def _end_balance(self, cursor, user, ids, name, attr, context=None):
        res = {}
        statements = self.browse(cursor, user, ids, context=context)
        for statement in statements:
            res[statement.id] = statement.balance_start
            for line in statement.line_ids:
                    res[statement.id] += line.amount
        for r in res:
            res[r] = round(res[r], 2)
        return res

    def _get_period(self, cr, uid, context={}):
        periods = self.pool.get('account.period').find(cr, uid)
        if periods:
            return periods[0]
        else:
            return False

    def _currency(self, cursor, user, ids, name, args, context=None):
        res = {}
        res_currency_obj = self.pool.get('res.currency')
        res_users_obj = self.pool.get('res.users')
        default_currency = res_users_obj.browse(cursor, user,
                user, context=context).company_id.currency_id
        for statement in self.browse(cursor, user, ids, context=context):
            currency = statement.journal_id.currency
            if not currency:
                currency = default_currency
            res[statement.id] = currency.id
        currency_names = {}
        for currency_id, currency_name in res_currency_obj.name_get(cursor,
                user, [x for x in res.values()], context=context):
            currency_names[currency_id] = currency_name
        for statement_id in res.keys():
            currency_id = res[statement_id]
            res[statement_id] = (currency_id, currency_names[currency_id])
        return res

    _order = 'date desc'
    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=True),
        'date': fields.date('Date', required=True, readonly=True),
        'coda_id': fields.many2one('account.coda', 'CODA Data File', ondelete='cascade'),        
        'statement_id': fields.many2one('account.bank.statement', 'Associated Bank Statement'),        
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True,
            domain=[('type', '=', 'cash')]),
        'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True),
        'balance_start': fields.float('Starting Balance', digits=(16,2), readonly=True),
        'balance_end_real': fields.float('Ending Balance', digits=(16,2), readonly=True),
        'balance_end': fields.function(_end_balance, method=True, string='Balance'),        
        'line_ids': fields.one2many('coda.bank.statement.line',
            'statement_id', 'CODA Bank Statement lines', readonly=True),
        'state': fields.selection([('draft', 'Draft'),('done', 'Done')],
            'State', required=True, readonly=True),
        'currency': fields.function(_currency, method=True, string='Currency',
            type='many2one', relation='res.currency'),
        'company_id': fields.related('journal_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
    }
    _defaults = {
        'state': lambda *a: 'draft',
        'journal_id': _default_journal_id,
        'period_id': _get_period,
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None: 
            context = {}
        res = super(coda_bank_statement, self).search(cr, uid, args=args, offset=offset, limit=limit, order=order,
                context=context, count=count)
        if context.get('bank_statement', False) and not res:
            raise osv.except_osv('Warning', _('No CODA Bank Statement found for this Bank Statement!'))
        return res

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        coda_obj = self.pool.get('account.coda')
        for coda_statement in self.browse(cr, uid, ids, context=context):
            if coda_statement.state == 'done':
                if coda_statement.statement_id.state == 'confirm': 
                    raise osv.except_osv(_('Invalid action !'),
                        _("Cannot delete CODA Bank Statement '%s' of Journal '%s'." \
                          "\nThe associated Bank Statement has already been confirmed !" \
                          "\nPlease undo this action first!") \
                          % (coda_statement.name, coda_statement.journal_id.name))
                else:
                    coda_obj.unlink(cr, uid, [coda_statement.coda_id.id], context=context)
        return super(coda_bank_statement, self).unlink(cr, uid, ids, context=context)

    def action_generate(self, cr, uid, ids, context={}):
        bank_st_obj = self.pool.get('account.bank.statement')
        bk_st_ids = []
        for statement in self.browse(cr, uid, ids, context):
            try:               
                bk_st_id = bank_st_obj.create(cr, uid, {
                    'name': statement.name,
                    'journal_id': statement.journal_id.id,
                    'coda_statement_id': ids[0],
                    'date': statement.date,
                    'period_id': statement.period_id.id,
                    'balance_start': statement.balance_start,
                    'balance_end_real': statement.balance_end_real,
                    'state': 'draft',
                })
                self.write(cr, uid, ids, {'statement_id':bk_st_id}, context=context)
                bk_st_ids.append(bk_st_id)
                line_ids = statement.line_ids
                for rec in line_ids:
                    line = self.pool.get('coda.bank.statement.line').browse(cr, uid, rec.id, context=context)                  
                    if line.type in ['information', 'communication', 'globalisation']:
                        pass
                    else:
                        # To Do : add code to reconcile on bba structured communication
                        st_line_id = self.pool.get('account.bank.statement.line').create(cr, uid, {
                                   'name': line.name,
                                   'type' : line.type,
                                   'date': line.date,
                                   'amount': line.amount,
                                   'partner_id': line.partner_id and line.partner_id.id,
                                   'account_id': line.account_id and line.account_id.id,
                                   'statement_id': bk_st_id,
                                   'note': line.note,
                                   'ref': line.ref,
                                   })
                        if line.invoice_id:

                            for l in line.invoice_id.move_id.line_id:
                                if l.account_id.type in ('receivable','payable'):
                                    self.pool.get('account.bank.statement.line').create_voucher(cr, uid, [st_line_id], l.id, statement.journal_id.id, context=context)
                                    break
                bank_st_obj.button_dummy(cr, uid, [bk_st_id], context=context)       # calculate balance
                cr.commit()

            except osv.except_osv, e:
                cr.rollback()
                err_log = '\n\nApplication Error : ' + str(e)
                raise osv.except_osv(_('Error !'),err_log)
    
            except Exception, e:
                cr.rollback()
                err_log = '\n\nSystem Error : ' +str(e)
                raise osv.except_osv(_('Error !'),err_log)

            except :
                cr.rollback()
                err_log = '\n\nUnknown Error'
                raise osv.except_osv(_('Error !'),err_log)

        self.write(cr, uid, ids, {'state':'done'}, context=context)
        return bk_st_ids

    def action_cancel(self, cr, uid, ids, context={}):
        bank_st_obj = self.pool.get('account.bank.statement')
        for coda_statement in self.browse(cr, uid, ids, context=context):
            if coda_statement.state == 'done':
                if coda_statement.statement_id.state == 'confirm':
                    # do not overwrite the bank statement error message when unlink originated from account.bank.statement
                    if not context.get('bank_st_unlink', False):
                        raise osv.except_osv(_('Invalid action !'),
                            _("Cannot delete CODA Bank Statement '%s' of Journal '%s'." \
                              "\nThe associated Bank Statement has already been confirmed !" \
                              "\nPlease undo this action first!") \
                              % (coda_statement.name, coda_statement.journal_id.name))
            # avoid unlink loop when unlink originated from account.bank.statement
            if not context.get('bank_st_unlink', False):
                bank_st_obj.unlink(cr, uid, [coda_statement.statement_id.id])
        #self.write(cr, uid, ids, {'state': 'draft'}, context=context)
        return True
 
coda_bank_statement()

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'
    _columns = {
        'coda_statement_id': fields.many2one('coda.bank.statement', 'Associated CODA Bank Statement'),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        context.update({'bank_st_unlink': True})
        coda_obj = self.pool.get('account.coda')
        for statement in self.browse(cr, uid, ids, context=context):
            if statement.coda_statement_id:
                coda_obj.unlink(cr, uid, [statement.coda_statement_id.coda_id.id], context=context)
        return super(account_bank_statement, self).unlink(cr, uid, ids, context=context)
         
account_bank_statement()

class coda_bank_statement_line(osv.osv):
    _name = 'coda.bank.statement.line'     
    _order = 'sequence'   
    _description = 'CODA Bank Statement Line'
    _columns = {
        'name': fields.char('Communication', size=64, required=True),
        'sequence': fields.integer('Sequence'),
        'date': fields.date('Date', required=True),
        'account_id': fields.many2one('account.account','Account'),     # remove required=True
        'type': fields.selection([
            ('supplier','Supplier'),
            ('customer','Customer'),
            ('general','General'),
            ('globalisation','Globalisation'),            
            ('information','Information'),    
            ('communication','Free Communication'),          
            ], 'Type', required=True),
        'globalisation_level': fields.integer('Globalisation Level', 
                help="The value which is mentioned (1 to 9), specifies the hierarchy level"
                     " of the globalisation of which this record is the first."
                     "\nThe same code will be repeated at the end of the globalisation."),
        'globalisation_amount': fields.float('Globalisation Amount'),                                                           
        'amount': fields.float('Amount'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'statement_id': fields.many2one('coda.bank.statement', 'CODA Bank Statement',
            select=True, required=True, ondelete='cascade'),
        'ref': fields.char('Reference', size=32),
        'note': fields.text('Notes'),
        'company_id': fields.related('statement_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),        
    }
coda_bank_statement_line()      
