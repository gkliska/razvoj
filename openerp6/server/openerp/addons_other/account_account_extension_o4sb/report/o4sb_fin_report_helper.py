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
import time
import pooler
from tools.translate import _

class o4sb_fin_report_helper(object):
    
    def _get_total(self, type):
        try:
            return self._format_balance(self.result_sum.get(type, 0.0))
        except:
            return self._format_balance(self.result_sum[type].get('balance', 0.0))
    
    def _format_balance(self, value):
        if value == 0.0:
            return ''
        if self.rounding:
            return str('%s%d' % (self.currency, int(value)))
        else:
            #Todo make it respect decimal precision
            return str('%s%.2f' % (self.currency, value)) 
        
    def _indent(self, line, indent=3, type='l'):
        if type == 'l':
            x = max((line['level'] - 3), 0)*indent
        else:
            x = min((3 - line['level']), 0)*-1*indent
        return '.'*x #Todo make this whitespace, not working for right aligned reports.

    def _get_display(self, data):
        display = {'bal_all': 'All', 'bal_balance': 'With Balances', 'bal_solde': 'With Balances', 'bal_movement': 'With Movements'}
        return display.get(data['form'].get('display_account'), 'Unknown')
    
    def get_lines(self, type):
        return self.lines[type]
    
    
    
    