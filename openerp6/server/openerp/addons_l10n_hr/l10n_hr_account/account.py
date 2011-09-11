# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#    Contributions: 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv, orm

class account_move(osv.osv):
    _inherit = "account.move"

    def check_vat_number(self, cr, uid, partner_id, context=None):
        if not partner_id:
            raise osv.except_osv(_('Partner missing!'),_("Partner is required for this type of posting!"))
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id, context={})
        if (not partner.vat) or (not partner_obj.check_vat(cr, uid, partner_id, context=None) ):
            raise osv.except_osv(_('Invalid VAT number!'),_("Partner (%s) does not have VAT number!") % partner.name)
        return True

    def validate(self, cr, uid, ids, context=None):
        res=super(account_move,self).validate(cr, uid, ids, context=context)
        for move in self.browse(cr, uid, ids, context):
            if move.journal_id.type in ('purchase','sale','purchase_refund','sale_refund'):            
                self.check_vat_number(cr, uid, move.partner_id, context) 
        return res


