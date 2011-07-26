# -*- encoding: utf-8 -*-
############################################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (C) 2008-2009 AJM Technologies S.A. (<http://www.ajm.lu>). All Rights Reserved
#    Copyright (C) 2010 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
#    $Id$
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
############################################################################################

from osv import osv, fields
from tools.translate import _

import time
import mx.DateTime

class holiday_year_wizard(osv.osv_memory):
    _name = 'training.holiday.year.wizard'

    _columns = {
        'year' : fields.integer('Year', required=True),
    }

    _defaults = {
        'year' : lambda *a: int(time.strftime('%Y')),
    }

    def _check_date(self, cr, uid, ids, context=None):
        return self.browse(cr, uid, ids[0], context=context).year >= int(time.strftime('%Y'))

    def action_cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def action_apply(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids[0], context=context)

        first_day = mx.DateTime.strptime('%04s-01-01' % (this.year,), '%Y-%m-%d')
        last_day = mx.DateTime.strptime('%04s-12-31' % (this.year,), '%Y-%m-%d')

        tmp_day = first_day

        proxy = self.pool.get('training.holiday.year')
        year_id = proxy.create(cr, uid, {'year' : this.year}, context=context)

        proxy = self.pool.get('training.holiday.period')

        counter = 1
        while tmp_day <= last_day:

            if tmp_day.day_of_week == mx.DateTime.Saturday:
                saturday = tmp_day.strftime('%Y-%m-%d')
                tmp_day = tmp_day + mx.DateTime.RelativeDate(days=1)
                sunday = tmp_day.strftime('%Y-%m-%d')

                proxy.create(cr, uid, {
                    'year_id' : year_id,
                    'date_start' : saturday,
                    'date_stop' : sunday,
                    'name' : _('Weekend %02d') % (counter,)
                }, context=context),

                counter = counter + 1
            tmp_day = tmp_day + mx.DateTime.RelativeDate(days=1)

        return {
            'view_type': 'form',
            "view_mode": 'form',
            'res_model': 'training.holiday.year',
            'view_id':self.pool.get('ir.ui.view').search(cr,uid,[('name','=','training.holiday.year.form')]),
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id' : year_id,
        }

    _constraints = [
        (_check_date, "Can you check the year", ['year']),
    ]

holiday_year_wizard()

