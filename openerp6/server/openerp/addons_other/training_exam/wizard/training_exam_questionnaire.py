# -*- encoding: utf-8 -*-
############################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    Copyright (C) 2008-2009 AJM Technologies S.A. (<http://www.ajm.lu). All Rights Reserved
#    Copyright (C) 2010-2011 Thamini S.à.R.L (<http://www.thamini.com>). All Rights Reserved
#    Copyright (C) 2011 Zikzakmedia S.L. (<http://www.zikzakmedia.com>). All Rights Reserved
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

from osv import osv
from osv import fields
import random

class exam_questionnaire_wizard(osv.osv_memory):
    _name = 'training.exam.questionnaire.wizard'
    _description = 'Questionnaire Wizard'

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'course_id' : fields.many2one('training.course', 'Course', required=True, domain="[('state_course', '=', 'validated')]"),
        'number_of_question' : fields.integer('Number of Questions'),
        'kind' : fields.selection(
            [
                ('automatic', 'Automatic'),
                ('manual', 'At Least one open-ended question')
            ],
            'Type'),
    }

    _defaults = {
        'kind' : lambda *a: 'automatic',
        'number_of_question' : lambda *a: 20,
    }

    def action_cancel(self, cr, uid, ids, context=None):
        return {'type':'ir.actions.act_window_close'}

    def action_generate_questionnaire(self, cr, uid, ids, context=None):
        if not ids:
            return {}
        if context is None:
            context = {}
        question_proxy = self.pool.get('training.exam.question')
        exam_question_proxy = self.pool.get('training.exam.questionnaire.question')
        this = self.browse(cr, uid, ids, context=context)[0]
        all_question_ids = question_proxy.search(cr, uid, [], context=context)
        mandatory_question_ids = []
        question_ids = []
        for question in question_proxy.browse(cr, uid, all_question_ids, context=context):
            if this.course_id in question.course_ids:
                if question.is_mandatory:
                    mandatory_question_ids.append(question.id)
                else:
                    question_ids.append(question.id)

        mqids = []
        qids = []

        number_of_mandatory_questions = random.randint(0, 3)
        number_of_questions = min(max(20, this.number_of_question) - number_of_mandatory_questions,len(question_ids))

        while number_of_mandatory_questions:
            try:
                idx = random.randint(0, len(mandatory_question_ids))
                mqids.append(mandatory_question_ids[idx])
                del mandatory_question_ids[idx]
            except:
                pass
            number_of_mandatory_questions -= 1

        while number_of_questions:
            try:
                idx = random.randint(0, len(question_ids))
                qids.append(question_ids[idx])
                del question_ids[idx]
                number_of_questions -= 1
            except:
                pass
        question = []
        for quest in exam_question_proxy.read(cr, uid,  mqids + qids, context=context):
            if quest.get('question_id',False):
                quest.update({'question_id': quest.get('question_id')[0]})
            question.append(quest)
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'training.exam.questionnaire',
            'view_id':self.pool.get('ir.ui.view').search(cr,uid,[('name','=','training.exam.questionnaire.form')]),
            'type': 'ir.actions.act_window',
            'target':'current',
            'context' : {
                'default_name' : this.name,
                'default_main_course_id' : this.course_id.id,
                'default_question_ids' : question,
                'default_kind' : this.kind,
            }
        }

exam_questionnaire_wizard()
