# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

import pooler
from report import report_sxw
import account_profit_loss
from account.report.common_report_header import common_report_header
from tools.translate import _
from o4sb_fin_report_helper import o4sb_fin_report_helper

class Parser(report_sxw.rml_parse, common_report_header, o4sb_fin_report_helper):
    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.obj_pl = account_profit_loss.Parser(cr, uid, name, context=context)
        self.obj_py = account_profit_loss.Parser(cr, uid, name, context=context)
        self.rounding = False
        self.currency = ''
        self.result_sum = {}
        self.lines = {}
        self.localcontext.update({
            'time': time,
            'get_lines': self.get_lines,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
            'get_total': self._get_total,
            'get_data':self.get_data,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_balance_date': self._get_balance_date,
            'get_sortby': self._get_sortby,
            'get_company':self._get_company,
            'get_target_move': self._get_target_move,
            'get_display': self._get_display,
            'indent': self._indent,
            'get_cat': self._get_categories,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(Parser, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_categories(self):
        return [{'name': _('Assets'), 'types': ['asset', 'fixed_asset'],'sum': 'dr', 'break': False},
                {'name': _('Equity and Liabilities'), 'types': [],'sum': 'cr', 'break': True},
                {'name': _('Liabilities'), 'types': ['liability' , 'fixed_liability'], 'sum': 'lb', 'break': False}, 
                {'name': _('Equity'), 'types': ['equity'],'sum': 'equity', 'break': False}]
    
    def _get_balance_date(self, data):
        period = pooler.get_pool(self.cr.dbname).get('account.period').browse(self.cr, self.uid, data['form']['period'])
        res = time.strftime('%d %B %Y', time.strptime(period.date_stop, '%Y-%m-%d'))
        return res 

    def get_data(self,data):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)
        
        account_pool = db_pool.get('account.account')
        currency_pool = db_pool.get('res.currency')
        period_pool = db_pool.get('account.period')
        self.currency = self._get_currency(data)
        fiscalyear_obj = db_pool.get('account.fiscalyear')

        #Getting Profit or Loss Balance from profit and Loss report
        pl_data = data.copy()
        res = {}
        #We need to change our form data so we get back the profit and loss from all open fiscal periods up to the date of the report.  To fudge it to look correct,
        #first we get the periods belonging to the current fiscal year and then to all previous years that have not been closed yet.
        #We use 2 pl_data objects because I don't trust profit and loss get_data function to reset data.
        date_stop = period_pool.browse(cr, uid, data['form']['period']).date_stop
        pl_data['form']['periods'] = period_pool.search(cr, uid, [('date_start', '<', date_stop)])       
        self.obj_pl.get_data(pl_data)
        res['bl'] = self.obj_pl.final_result()
        
        fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state', '=', 'draft')])
        fiscalyears = fiscalyear_obj.browse(cr, uid, fiscalyear_ids)
        pl_data['form']['fiscalyear_id'] = [f.id for f in fiscalyears if (f.date_stop < date_stop) ]
        if pl_data['form'].get('fiscalyear_id', False):
            self.obj_py.get_data(pl_data)
            res['py'] = self.obj_py.final_result()        
        
        types = {
            'fixed_asset': 1,
            'asset': 1,
            'liability': -1,
            'fixed_liability': -1,
            'equity': -1,
            }

        ctx = self.context.copy()
        #We set this to False because a balance sheet is a point in time report and should consider all fiscalyears.
        ctx['fiscalyear'] = False
        ctx['state'] = data['form'].get('target_move', 'all')
        date_stop = period_pool.browse(cr, uid, data['form']['period']).date_stop
        ctx['periods'] = period_pool.search(cr, uid, [('date_start', '<', date_stop)])
        pl_dict = []
        account_dict = {}
        account_id = data['form'].get('chart_account_id', False)
        account_ids = account_pool._get_children_and_consol(cr, uid, account_id, context=ctx)
        accounts = account_pool.browse(cr, uid, account_ids, context=ctx)

        for k, v in res.items():
            if not v:
                v['type'] = _('Net Profit')
                v['balance'] = 0.0

            if v['type'] != _('Net Profit'):
                v['balance'] = v['balance'] * -1
        
        if res.get('py', False):
            pl_dict.append({
                'code': res['py'].get('type', ''),
                'name': _('Unposted Earnings from prior fiscal years'),
                'level': False,
                'balance': res['py'].get('balance', 0.0),
                'type': res['py'].get('type', ''),
                'fmt_balance': self._format_balance(res['py'].get('balance', 0.0)),
            })
                        
        pl_dict.append({
            'code': res['bl'].get('type', ''),
            'name': _('Current Year Earnings'),
            'level': False,
            'balance': res['bl'].get('balance', 0.0),
            'type': res['bl'].get('type', ''),
            'fmt_balance': self._format_balance(res['bl'].get('balance', 0.0)),
        })

        def append_accounts():
            #Basically we are saying that if this account is equal to or higher in the hierarchy than the last entry, we need to add the total
            while view_accounts_total_lines and (account.level <= view_accounts_total_lines[-1]['level']):
                accounts_temp.append(view_accounts_total_lines.pop())
            if account.type == 'view':                
                view_accounts_total_lines.append({
                    'id': account.id,
                    'code': '',
                    'name': _('Total')+' '+account.name,
                    'level': account.level,
                    'balance': account.balance * sign,
                    'type': 'view_total',
                    'fmt_balance': self._format_balance(account.balance * sign),
                })
                account_dict.update({'balance': 0.00, 'fmt_balance': ''})
            accounts_temp.append(account_dict)
            
            
        for typ, sign in types.items():
            self.result_sum[typ] = 0.0
            accounts_temp = []
            view_accounts_total_lines = []
            for account in accounts:
                if (account.user_type.report_type) and (account.user_type.report_type == typ):
                    account_dict = {
                        'id': account.id,
                        'code': account.code,
                        'name': account.name,
                        'level': account.level,
                        'balance':account.balance * sign,
                        'type': account.type,
                        'fmt_balance': self._format_balance(account.balance * sign),
                    }
                    currency = account.currency_id and account.currency_id or account.company_id.currency_id
                    if account.id == data['form']['reserve_account_id']:
                        self.result_sum[typ] += account.balance * sign
                        append_accounts()
                        for profit in pl_dict:
                            profit['level'] = account.level + 1
                            accounts_temp.append(profit)
                            self.result_sum[typ] += profit['balance']
                    else:                    
                        if account.type <> 'view' and (account.debit <> account.credit):
                            self.result_sum[typ] += account.balance * sign
                        if account.level > data['form']['level'] and account.id != data['form']['reserve_account_id']:
                            continue
                        if data['form']['display_account'] == 'bal_movement':
                            if (not currency_pool.is_zero(self.cr, self.uid, currency, account.credit)) or (not currency_pool.is_zero(self.cr, self.uid, currency, account.debit)) or (not currency_pool.is_zero(self.cr, self.uid, currency, account.balance)):
                                append_accounts()
                        elif data['form']['display_account'] == 'bal_balance':
                            if not currency_pool.is_zero(self.cr, self.uid, currency, account.balance):
                                append_accounts()
                        else:
                            append_accounts()

            if view_accounts_total_lines:
                view_accounts_total_lines.reverse()
                accounts_temp.extend(view_accounts_total_lines) 
            self.lines[typ] = accounts_temp
                
        self.result_sum['dr'] = self.result_sum.get('asset', 0.0)+self.result_sum.get('fixed_asset', 0.0)
        self.result_sum['lb'] = self.result_sum.get('liability', 0.0)+self.result_sum.get('fixed_liability', 0.0)
        self.result_sum['cr'] = self.result_sum.get('lb', 0.0)+self.result_sum.get('equity', 0.0)
        if data['form']['rounding']:
            self.rounding = True    
        return None
    



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: