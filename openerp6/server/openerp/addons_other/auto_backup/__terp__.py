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

{
    "name" : "Database Auto-Backup",
    "version" : "1.0",
    "author" : "Tiny",
    "website" : "http://www.openerp.com",
    "category" : "Generic Modules",
    "description": """The generic Open ERP Database Auto-Backup system enables the user to make configurations for the automatic backup of the database.
User simply requires to specify host & port under IP Configuration & database(on specified host running at specified port) and backup directory(in which all the backups of the specified database will be stored) under Database Configuration.

Automatic backup for all such configured databases under this can then be scheduled as follows:  
                      
1) Go to Administration / Configuration / Scheduler / Scheduled Actions
2) Schedule new action(create a new record)
3) Set 'Object' to 'db.backup' and 'Function' to 'schedule_backup' under page 'Technical Data'
4) Set other values as per your preference""",
    "depends" : [],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ["bkp_conf_view.xml","backup_data.xml"],
    "active": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: