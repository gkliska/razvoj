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

from datetime import datetime
from dateutil.relativedelta import relativedelta

from osv import osv, fields
from tools.translate import _

class account_extension_common_report(osv.osv_memory):
    # Just fixing some functions to return sensible values
    _inherit = "account.common.account.report"
    _name = "account.extension.common.report"
    
    def onchange_chart_id(self, cr, uid, ids, chart_id, context=None):
        if not chart_id:
            return {}
        account = self.pool.get('account.account').browse(cr, uid, chart_id , context=context)
        if not account.company_id.property_reserve_and_surplus_account:
            return {'value': {'reserve_account_id': False, 'company_id': account.company_id.id}}
        return {'value': {'reserve_account_id': account.company_id.property_reserve_and_surplus_account.id, 'company_id': account.company_id.id}}
    
    def _get_company_id(self, cr, uid, context=None):
        chart_id = self._get_account(cr, uid, context=context)
        res = self.onchange_chart_id(cr, uid, [], chart_id, context=context)
        if not res:
            return False
        return res['value']['company_id']  

    def _get_period(self, cr, uid, context=None):
        last_month = (datetime.now()-relativedelta(months=1)).strftime('%Y-%m-%d')
        company_id = self._get_company_id(cr, uid, context)      
        period = self.pool.get('account.period').search(cr, uid, [('date_start', '<', last_month), ('date_stop', '>', last_month), ('company_id', '=', company_id)] ,)
        return period and period[0] or False

    def _get_account(self, cr, uid, context=None):
        company_id = self.pool.get('res.users').browse(cr,uid, uid).company_id.id
        accounts = self.pool.get('account.account').search(cr, uid, [('parent_id', '=', False), ('company_id', '=', company_id)], limit=1)
        return accounts and accounts[0] or False
    
    def _get_all_journal(self, cr, uid, context=None):
        company_id = self._get_company_id(cr, uid, context)
        return self.pool.get('account.journal').search(cr, uid ,[('company_id', '=', company_id)])
    
    columns = {
        'chart_account_id': fields.many2one('account.account', 'Chart of account', help='Select Charts of Accounts', required=True, domain = [('parent_id','=',False)]),
        }
    
    defaults = {
        'chart_account_id': _get_account
        }


account_extension_common_report()    

class account_bs_alt_report(osv.osv_memory):
    """
    This wizard will provide the account balance sheet report by periods, between any two dates.
    """
    _name = 'account.bs.alternative.report'
    _inherit = "account.extension.common.report"
    _description = 'Account Balance Sheet Report'

    def _get_def_reserve_account(self, cr, uid, context=None):
        chart_id = self._get_account(cr, uid, context=context)
        res = self.onchange_chart_id(cr, uid, [], chart_id, context=context)
        if not res:
            return False
        return res['value']['reserve_account_id']        

    _columns = {
        'display_type': fields.boolean("Landscape Mode"),
        'rounding': fields.boolean('Rounding', help='Round values to nearest dollar'),
        'level': fields.integer('Account Level', help="Levels between 3 and 6 are most useful, generally 6 will print all accounts, 3 will print just summary accounts in most setups."),
        'display_account': fields.selection([('bal_all','All'), ('bal_movement','With movements'),
                                            ('bal_balance','With balance is not equal to 0'),
                                            ],'Display accounts', required=True),
        'reserve_account_id': fields.many2one('account.account', 'Reserve & Profit/Loss Account',
                                      required=True,
                                      help='This Account is used for transferring Profit/Loss ' \
                                           '(Profit: Amount will be added, Loss: Amount will be deducted), ' \
                                           'which is calculated from Profit & Loss Report',
                                      domain = [('type','=','payable')]),
        'period': fields.many2one('account.period', 'Period', required=True),
        'filter': fields.selection([('filter_no', 'No Filters'), ('filter_date', 'Date'), ('filter_period', 'Periods')], "Filter by", required=False),
        'journal_ids': fields.many2many('account.journal', 'account_common_journal_rel', 'account_id', 'journal_id', 'Journals', required=False),
        'company_id': fields.many2one('res.company', 'Company')
    }
    
    def _get_period(self, cr, uid, context=None):
        return super(account_bs_alt_report, self)._get_period(cr, uid, context)
    
    def _get_company_id(self, cr, uid, context=None):
        return super(account_bs_alt_report, self)._get_company_id(cr, uid, context)

    _defaults={
        'display_type': True,
        'journal_ids': [],
        'reserve_account_id': _get_def_reserve_account,
        'level': 6,
        'period': _get_period,
        'company_id': _get_company_id
    }




    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids, ['display_type','reserve_account_id', 'period', 'rounding', 'level'])[0])
        if not data['form']['reserve_account_id']:
            raise osv.except_osv(_('Warning'),_('Please define the Reserve and Profit/Loss account for current user company !'))
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        if data['form']['display_type']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.balancesheet.alternative',
                'datas': data,
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.balancesheet.alternative',
                'datas': data,
            }

account_bs_alt_report()

class account_pl_alt_report(osv.osv_memory):
    """
    This wizard will provide the account profit and loss report by periods, between any two dates.
    """
    _inherit = "account.extension.common.report"
    _name = "account.pl.report.alternative"
    _description = "Account Profit And Loss Report"
    _columns = {
        'display_type': fields.boolean("Landscape Mode"),
        'rounding': fields.boolean('Rounding', help='Round values to nearest dollar'),
        'level': fields.integer('Account Level', help="Levels between 3 and 6 are most useful, generally 6 will print all accounts, 3 will print just summary accounts in most setups."),

    }

    def _get_all_journal(self, cr, uid, context=None):
        return super(account_pl_alt_report, self)._get_all_journal(cr, uid, context)

    _defaults = {
        'display_type': True,
        'journal_ids': _get_all_journal,
        'level': 6
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['display_type', 'rounding', 'level'])[0])
        #Will use in future, but only 1 report for now
        if data['form']['display_type']:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.pl.alternative',
                'datas': data,
            }
        else:
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.pl.alternative',
                'datas': data,
            }

account_pl_alt_report()