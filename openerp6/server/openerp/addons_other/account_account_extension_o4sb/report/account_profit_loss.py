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
from account.report.common_report_header import common_report_header
from tools.translate import _
from o4sb_fin_report_helper import o4sb_fin_report_helper

class Parser(report_sxw.rml_parse, common_report_header, o4sb_fin_report_helper):

    def __init__(self, cr, uid, name, context=None):
        super(Parser, self).__init__(cr, uid, name, context=context)
        self.res_pl = {}
        self.rounding = False
        self.currency = ''
        self.result_sum = {}
        self.lines = {}
        self.localcontext.update( {
            'time': time,
            'get_lines': self.get_lines,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
            'get_total': self._get_total,
            'get_data':self.get_data,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_pl_date': self._get_pl_date,
            'get_sortby': self._get_sortby,
            'get_company':self._get_company,
            'get_target_move': self._get_target_move,
            'get_display': self._get_display,
            'indent': self._indent,
            'get_cat': self._get_categories,
            'final_result': self.final_result,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(Parser, self).set_context(objects, data, new_ids, report_type=report_type)
    
    def _get_pl_date(self, data):
        cr, uid = self.cr, self.uid
        if data['form']['filter'] == 'filter_period':
            period_obj = pooler.get_pool(self.cr.dbname).get('account.period')
            periods =  data['form'].get('periods', False)
            start = period_obj.browse(cr, uid, periods[0]).date_start
            stop = period_obj.browse(cr, uid, periods[-1]).date_stop
        elif data['form']['filter'] == 'filter_date':
            start = data['form'].get('date_from', False)
            stop =  data['form'].get('date_to', False)
        elif data['form']['fiscalyear_id']:
            fiscalyear_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear').browse(cr, uid, data['form']['fiscalyear_id'])
            start = fiscalyear_obj.date_start
            stop = fiscalyear_obj.date_stop
        res = time.strftime('%d %B %Y', time.strptime(start, '%Y-%m-%d')) + ' to ' + time.strftime('%d %B %Y', time.strptime(stop, '%Y-%m-%d'))
        return res 
    
    def _get_categories(self):
        return [{'name': _('Income'), 'types': ['income'],'sum': 'income', 'break': False },
                {'name': _('Cost of Sales'), 'types': ['cogs'], 'sum': 'cogs', 'break': False },
                {'name': self.result_sum['gp'].get('type'), 'types': [],'sum': 'gp', 'break': False },
                {'name': _('Expenses'), 'types': ['expense'], 'sum': 'expense', 'break': False },
                {'name': self.result_sum['nop'].get('type'), 'types': [],'sum': 'nop', 'break': False },
                {'name': _('Other Income'), 'types': ['other_income'], 'sum': 'other_income', 'break': False}, 
                {'name': _('Other Expense'), 'types': ['other_expense'],'sum': 'other_expense', 'break': False},
                {'name': self.result_sum['np'].get('type'), 'types': [],'sum': 'np', 'break': False },]

    def final_result(self):
        return self.result_sum.get('np', False)

    def get_data(self, data):
        cr, uid = self.cr, self.uid
        db_pool = pooler.get_pool(self.cr.dbname)

        account_pool = db_pool.get('account.account')
        currency_pool = db_pool.get('res.currency')

        types = {
            'income': -1,
            'cogs': 1,
            'expense': 1,
            'other_income': -1,
            'other_expense': 1,
                }

        ctx = self.context.copy()
        ctx['fiscalyear'] = data['form'].get('fiscalyear_id', False)

        if data['form']['filter'] == 'filter_period':
            ctx['periods'] =  data['form'].get('periods', False)
        elif data['form']['filter'] == 'filter_date':
            ctx['date_from'] = data['form'].get('date_from', False)
            ctx['date_to'] =  data['form'].get('date_to', False)

        cal_list = {}
        account_id = data['form'].get('chart_account_id', False)
        account_ids = account_pool._get_children_and_consol(cr, uid, account_id, context=ctx)
        accounts = account_pool.browse(cr, uid, account_ids, context=ctx)
        
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
        
        self.result_sum.update({'dr': 0.0, 'gp': {}, 'cr': 0.0, 'np': {}, 'nop': {}})

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
                if (account.user_type.report_type) and (account.user_type.report_type == typ):
                    currency = account.currency_id and account.currency_id or account.company_id.currency_id
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
            
            if sign == 1:
                self.result_sum['dr'] += self.result_sum[typ]
            else:
                self.result_sum['cr'] += self.result_sum[typ]
            if view_accounts_total_lines:
                view_accounts_total_lines.reverse()
                accounts_temp.extend(view_accounts_total_lines)
            self.lines[typ] = accounts_temp
        self.result_sum['gp']['balance'] = self.result_sum.get('income', 0.0) - self.result_sum.get('cogs', 0.0)
        self.result_sum['gp']['type'] = self.result_sum['gp'].get('balance',0.0) < 0.0 and _('Gross Loss') or _('Gross Profit')
        self.result_sum['nop']['balance'] = self.result_sum['gp'].get('balance', 0.0) - self.result_sum.get('expense', 0.0)
        self.result_sum['nop']['type'] = self.result_sum['nop'].get('balance', 0.0) < 0.0 and _('Net Operating Loss') or _('Net Operating Profit')
        self.result_sum['np']['balance'] = self.result_sum['nop'].get('balance', 0.0) + self.result_sum.get('other_income', 0.0) - self.result_sum.get('other_expense', 0.0)
        self.result_sum['np']['type'] = self.result_sum['np'].get('balance', 0.0) < 0.0 and _('Net Loss') or _('Net Profit')

        return None





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
