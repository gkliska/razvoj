# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2010 Gábor Dukai <gdukai@gmail.com>
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
    "name" : "Configurable system backup tool",
    "version" : "1.0",
    "author" : "Gábor Dukai",
    "website" : "http://exploringopenerp.blogspot.com",
    "license" : "GPL-3",
    "description": """
    This is a system backup tool that can be run from the OpenERP
    user interface. It is meant for system administrators.
    It doesn't do the backup itself but provides a convenient
    framework to run python backup scripts. There are several
    example scripts provided that can be run outside OpenERP
    so they can be easily tested.
    Backup scripts are called Tasks and they don't do device
    mounting and unmounting but that's provided by the scripts
    in the object Target.
    The result of a backup operation is called a Job. There are
    tar and rsync kind of jobs supported.

    Compatibility: tested with OpenERP v5.0
    """,
    "depends" : [
                 ],
    "init_xml" : [],
    "update_xml" : [
        "security/backup_security.xml",
        "security/ir.model.access.csv",
        "backup_view.xml",
                   ],
    "installable" : True,
    "active" : False,
}
