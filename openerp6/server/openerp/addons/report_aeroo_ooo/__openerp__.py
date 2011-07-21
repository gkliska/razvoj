# -*- encoding: utf-8 -*-

#########################################################################
#                                                                       #
# Copyright (C) 2009  Domsense s.r.l.                                   #
# @authors: Simone Orsi													#				       
# Copyright (C) 2009  KN dati, Ltd                                      #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

{ 
    'name': 'Aeroo Reports - OpenOffice Helper Addon',
    'version': '1.0',
    'category': 'Generic Modules/Aeroo Reporting',
    'description': """ Make possible used OpenOffice features for reports.
                    Requires "openoffice.org", "openoffice-python" to be installed.
                    """,
    'author': 'Alistek Ltd',
    'website': 'http://www.alistek.com',
    'depends': ['base','report_aeroo'],
    "init_xml" : [],
    'update_xml': ["report_view.xml", "data/report_aeroo_data.xml"],
    'installable': True,
    'active': False,
}
