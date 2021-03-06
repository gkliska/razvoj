# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jesús Martín <jmartin@zikzakmedia.com>
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


class training_course(osv.osv):
    _inherit = 'training.course'
    _name = 'training.course'
    
    _columns = {
        'course_wiki_pages_ids': fields.many2many('wiki.wiki', 'training_course_wiki_rel', 'training_course_id', 'wiki_wiki_id', string = 'Wiki Docs'),
    }

training_course()


class wiki_wiki(osv.osv):
    _inherit = 'wiki.wiki'
    _name = 'wiki.wiki'
    
    _columns = {
        'sequence': fields.integer('Sequence')
    }

wiki_wiki()
