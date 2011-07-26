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

{
    "name": "Training Human Resources",
    "version": "0.1",
    "author": "Zikzakmedia SL",
    "website": "http://www.zikzakmedia.com",
    "license" : "GPL-3",
    "category": "Training",
    "description": "Human Resources management for training module",
    "depends": [
        'training',
        'hr',
    ],
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "update_xml" : [
        'security/ir.model.access.csv',
        'training_hr_view.xml',
        'training_hr_sequence.xml',
#        'workflow/training_hr_subscription.xml',
#        'workflow/training_hr_subscription_line.xml',
    ],
    "installable": True,
}
