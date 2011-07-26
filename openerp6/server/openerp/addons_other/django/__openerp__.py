# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Raimon Esteve <resteve@zikzakmedia.com>
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
    "name" : "Django",
    "author" : "Zikzakmedia SL",
    "website" : "http://www.zikzakmedia.com",
    "description" : """
OpenERP integration to Django.
- Create OpenObject Model to Django Model. Select model and copy-paste Django Model (wizard)
- OpenERP to Django Mapping Fields. Export OpenERP data to Django Models
- Update SQL Django. Update Django models when already been created previously in Django (wizard)
This module was built generically but in focus of the ZZSaaS service of Zikzakmedia and Zoook e-sale for OpenERP
    """,
    "version" : "0.1",
    "depends" : ["base"],
    "init_xml" : [],
    "update_xml" : [
        "security/ir.model.access.csv",
        "django_view.xml",
        "partner_view.xml",
        "django_wizard.xml",
        "wizard/wizard_create_model.xml",
        "wizard/wizard_sql_update.xml",
    ],
    "category" : "Generic Modules",
    "active": False,
    "installable": True
}
