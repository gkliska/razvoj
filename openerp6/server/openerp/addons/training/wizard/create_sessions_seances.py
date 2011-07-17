# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
##############################################################################

from osv import osv, fields
from tools.translate import _

from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time

def strToDate(dt):
    return datetime(int(dt[0:4]),int(dt[5:7]),int(dt[8:10]),int(dt[11:13] or '00'),int(dt[14:16] or '00'),int(dt[17:19] or '00'))

class training_create_session_seances(osv.osv_memory):
    _name = 'training.create.session.seances'
    _rec_name = 'offer_id'

    _columns = {
        'offer_id': fields.many2one('training.offer', 'Offer', required=True),
        'address_id': fields.many2one('res.partner.address', 'Place'),
        'line_ids': fields.one2many('training.create.session.seances.line', 'create_sessions_id', 'Lines'),
        'date_from': fields.date('Date', required=True, help="The start date of the planned session."),
        'date_to' : fields.date('End Date', help="The end date of the planned session."),
        'format_id': fields.many2one('training.offer.format', 'Format', required=True, help="Delivery format of the planned session."),
        'state': fields.selection([
            ('first','First'),
            ('second','Second')
        ], 'State', readonly=True, required=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context= {}
        values = {
            'state': 'first',
            'date_from': time.strftime('%Y-%m-%d'),
        }
        offer_obj = self.pool.get('training.offer')
        if context['active_model'] == 'training.offer':
            values['offer_id'] = offer_obj.browse(cr, uid, context['active_id'], context = context).id
        return values

    def next_step(self, cr, uid, ids, context=None):
        ''' Fills the create session wizard with the course lines of the offer '''
        if context is None:
            context = {}
        values = {}
        session_line_obj = self.pool.get('training.create.session.seances.line')
        for create_session in self.browse(cr, uid, ids, context = context):
            values['create_sessions_id'] = create_session.id
            for course in create_session.offer_id.course_ids:
                values['course_id'] = course.course_id.id
                values['duration'] = course.course_id.splitted_by
                values['time'] = 12
                session_line_obj.create(cr, uid, values, context = context)
        return self.write(cr, uid, ids, {'state': 'second'}, context = context)

    def create_session (self, cr, uid, ids, context=None):
        """ Create one session and the seances depending of the duration and the splitted time of the courses. """
        if context is None:
            context = {}
        values = {}
        vals = {}
        write_values = {}
        weekdays = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday',
        }
        weekdays_obj = self.pool.get('training.create.session.seances.line')
        session_obj = self.pool.get('training.session')
        seance_obj = self.pool.get('training.seance')
        holiday_obj = self.pool.get('training.holiday.period')
        for create_session in self.browse(cr, uid, ids, context = context):
            hour = '00:00:00'
            if len(create_session.line_ids) < 2:
                time = create_session.line_ids[0].time
                hour = "%02d:%02d" % (time, round((time - int(time)) * 60))
            session_date = strToDate(create_session.date_from + ' ' + hour)
            values['date'] = session_date
            if create_session.date_to:
                date_to = strToDate(create_session.date_to)
                values['date_end'] = date_to
            else:
                date_to = False
            values['name'] = create_session.offer_id.name
            values['offer_id'] = create_session.offer_id.id
            values['format_id'] =create_session.format_id.id
            session_id = session_obj.create(cr, uid, values, context = context)
            seance_ids = []
            for create_seance in create_session.line_ids:
                start_hour = "%02d:%02d" % (create_seance.time, round((create_seance.time - int(create_seance.time)) * 60))
                seance_date = strToDate(create_session.date_from + ' ' + start_hour)
                duration = create_seance.course_id.duration
                splitted_by = create_seance.duration
                if splitted_by == 0:
                    raise osv.except_osv(_('Error'), _('The duration of the seance must be longer than 0!'))
                repeated = 0
                weekday = seance_date.weekday()
                seance_weekdays = weekdays_obj.read(cr, uid, [create_seance.id], [
                        'sunday','monday','tuesday','wednesday','thursday','friday','saturday'
                    ], context=context)[0]
                if not reduce(lambda x, y: x or y, [e for e in seance_weekdays.values()]):
                    raise osv.except_osv(_('Error'), _('You must select one day of the week at least!'))
                limit = 0
                while duration > 0 and limit < 365:
                    holiday_ids = holiday_obj.search(cr, uid, [('date_start','<=',seance_date),('date_stop','>=',seance_date)], context = context)
                    if seance_weekdays[weekdays[seance_date.weekday()]] and len(holiday_ids) == 0:
                        limit = 0
                        vals['name'] = create_seance.course_id.name
                        vals['date'] = seance_date
                        vals['kind'] = 'standard'
                        vals['duration'] = splitted_by
                        vals['course_id'] = create_seance.course_id.id
                        seance_ids.append(seance_obj.create(cr, uid, vals, context = context))
                        duration -= splitted_by
                    seance_date = seance_date + relativedelta(days=1)
                    limit += 1
                if limit >= 365:
                    raise osv.except_osv(_('Error'), _('Did not match any non-holiday days to create the seances in the next year!'))
            write_values['seance_ids'] = [(6, 0, seance_ids)]
            session_obj.write(cr, uid, [session_id], write_values, context = context)
        return session_id

    def create_new (self, cr, uid, ids, context=None):
        self.create_session (cr, uid, ids, context = context)
        return True
        
    def create_close (self, cr, uid, ids, context=None):
        self.create_session (cr, uid, ids, context = context)
        return {'type': 'ir.actions.act_window_close'}

    def onchange_offer(self, cr, uid, ids, offer_id=False, context=None):
        if context is None:
            context = {}
        values = {}
        offer_obj = self.pool.get('training.offer')
        values['format_id'] = offer_obj.browse(cr, uid, offer_id, context = context).format_id.id
        return {'value' : values}

training_create_session_seances()

class training_create_session_seances_line(osv.osv_memory):
    _name = 'training.create.session.seances.line'
    _rec_name = 'create_sessions_id'
    
    _columns = {
        'create_sessions_id':fields.many2one('training.create.session.seances', 'Session'),
        'course_id':fields.many2one('training.course', 'Course', required=True),
        'sunday': fields.boolean('Sunday', help="Check it if you want to create a session on Sunday."),
        'monday': fields.boolean('Monday', help="Check it if you want to create a session on Monday."),
        'tuesday': fields.boolean('Tuesday', help="Check it if you want to create a session on Tuesday."),
        'wednesday': fields.boolean('Wednesday', help="Check it if you want to create a session on Wednesday."),
        'thursday': fields.boolean('Thursday', help="Check it if you want to create a session on Thursday."),
        'friday': fields.boolean('Friday', help="Check it if you want to create a session on Friday."),
        'saturday': fields.boolean('Saturday', help="Check it if you want to create a session on Saturday."),
        'time': fields.time('Time From'),
        'duration': fields.float('Duration')
    }

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'monday': lambda *a: True,
        'tuesday': lambda *a: True,
        'wednesday': lambda *a: True,
        'thursday': lambda *a: True,
        'friday': lambda *a: True,
    }

    def _check_weekdays(self, cr, uid, ids, context=None):
        weekday_obj = self.browse(cr, uid, ids[0], context=context)
        if not weekday_obj.sunday and not weekday_obj.monday and not weekday_obj.tuesday and not weekday_obj.wednesday and not weekday_obj.thursday and not weekday_obj.friday and not weekday_obj.saturday:
            return False
        return True

    _constraints = [
        (_check_weekdays, 'You must check one day at least!', ['sunday','monday','tuesday','wednesday','thursday','friday','saturday',]),
    ]

training_create_session_seances_line()
