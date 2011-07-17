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


class training_school(osv.osv):
    _name = 'training.school'
    _description = 'Manage Training Multi Schools'

training_school()


class res_users(osv.osv):
    _name  =  "res.users"
    _inherit  =  "res.users"
    _columns  =  {
        'school_id': fields.many2one('training.school','School', help = 'The school related to the current user'),
        'school_ids': fields.many2many('training.school', 'school_user_rel', 'school_id', 'user_id', "Schools"),
    }

res_users()


class holiday_year(osv.osv):
    _name = 'training.holiday.year'
    _inherit = 'training.holiday.year'

    _columns = {
        'school_id': fields.many2one('training.school', 'School', help = 'The school related to this holiday period'),
    }

    _sql_constraints = [
        ('uniq_year', 'unique(year, school_id)', 'The year for the school must be unique!'),
    ]

holiday_year()


class training_session(osv.osv):
    _name = 'training.session'
    _inherit = 'training.session'

    _columns = {
        'school_id': fields.many2one('training.school', 'School', help = 'The school belongs to this session.'),
    }

training_session()

class training_subscription_line(osv.osv):
    _name = 'training.subscription.line'
    _inherit = 'training.subscription.line'

    _columns = {
        'school_id': fields.related('session_id','school_id', type='many2one', readonly=True, store=True, relation='training.school', string='School'),
    }

training_subscription_line()


class training_subscription(osv.osv):
    _name = 'training.subscription'
    _inherit = 'training.subscription'

    _columns = {
        'school_id': fields.related('subscription_line_ids','school_id', type='many2one', relation='training.school', readonly=True, store=True, string='School'),
    }

training_subscription()


class res_partner_contact(osv.osv):
    _name = "res.partner.contact"
    _inherit = "res.partner.contact"

    _columns = {
        'school_id': fields.related('group_id','school_id', type='many2one', readonly=True, store=True, relation='training.school', string='School'),
    }

res_partner_contact()


class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"

    def _get_contact_schools(self, cr, uid, ids, fields, arg, context=None):
        contact_obj = self.pool.get('res.partner.contact')
        school_ids = [x.id for x in self.pool.get('res.users').browse(cr, uid, uid, context).school_ids]
        res = {}
        for partner in self.browse(cr, uid, ids, context):
            contact_ids = []
            for addr in partner.address:
                for job in addr.job_ids:
                    contact_ids.append(job.contact_id.id)
            contacts_ids = contact_obj.search(cr, uid, [('id','in',contact_ids),('school_id','in',school_ids)], context=context)
            contacts = contact_obj.browse(cr, uid, contacts_ids, context)
            schools = []
            for c in contacts:
                if c.school_id and c.school_id.id not in schools:
                    schools.append(c.school_id.id)
            res[partner.id] = schools
        return res

    def _search_school(self, cr, uid, obj, name, args, context={}):
        contact_obj = self.pool.get('res.partner.contact')
        result = []
        cond = []
        for (namex,op,value) in args:
            if namex==name:
                if value in [False, True]:
                    cond.append(('group_id',op,value))
                    if op == '=' and value == False:
                        # Special case: We want to found partner not related to any address or address job
                        result = self.search(cr, uid, ['|',('address','=',False),('address.job_ids','=',False)])
                else:
                    cond.append(('group_id.session_id.school_id',op,value))
        contact_ids = contact_obj.search(cr, uid, cond)
        for contact in contact_obj.browse(cr, uid, contact_ids, context):
            for job in contact.job_ids:
                partner_id = job.address_id and job.address_id.partner_id and job.address_id.partner_id.id or False
                if partner_id and partner_id not in result:
                    result.append(partner_id)       
        return [('id','in', result)]
            
    _columns = {
        'school_ids': fields.function(_get_contact_schools, method = True, type='many2many', store=False, relation='training.school', string='School',  fnct_search=_search_school),
    }

res_partner()


class training_offer(osv.osv):
    _name = 'training.offer'
    _inherit = 'training.offer'

    _columns = {
        'school_ids': fields.many2many('training.school', 'training_offer_school_rel', 'school_id', 'offer_id', 'Schools'),
    }
    
training_offer()


class training_group(osv.osv):
    _name = 'training.group'
    _inherit = 'training.group'

    _columns = {
        'school_id': fields.related('session_id','school_id', type='many2one', select=True, readonly=True, store=True, relation='training.school', string='School'),
    }

training_group()

class training_seance(osv.osv):
    _name = 'training.seance'
    _inherit = 'training.seance'

    _columns = {
        'school_id': fields.related('group_id','session_id','school_id', type='many2one', readonly=True, store=True, relation='training.school', string='School'),
    }

training_seance()


class training_participation(osv.osv):
    _name = 'training.participation'
    _inherit = 'training.participation'
    
    _columns = {
        'school_id': fields.related('seance_id','school_id', type='many2one', readonly=True, store=True, relation='training.school', string='School'),
    }

training_participation()



class training_school(osv.osv):
    _name = 'training.school'

    _columns = {
        'name': fields.char('Name', size = 30, required = True, select = 1),
        'partner_id': fields.many2one('res.partner', 'Partner', required = True, select = 1, help = 'Partner that is related to the current school.'),
        'user_ids': fields.many2many('res.users', 'school_user_rel', 'user_id', 'school_id', 'Users', help = 'Users of this school.'),
        'holiday_ids': fields.one2many('training.holiday.year', 'school_id', string = 'Calendars', help = 'Calendars of this school.'),
        'session_ids': fields.one2many('training.session', 'school_id', string = 'Sessions', help = 'Sessions of this school.'),
        'group_ids': fields.one2many('training.group', 'school_id', string = 'Groups', help = 'Groups of this school.'),
    }

training_school()
