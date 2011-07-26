# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

import netsvc

from osv import osv, fields

class hr_expense_line(osv.osv):
    _inherit = 'hr.expense.line'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Supplier', required=True),
    }

hr_expense_line()

class hr_expense_expense(osv.osv):
    _inherit = 'hr.expense.expense'

    def action_invoice_create(self, cr, uid, ids):
        res = False
        invoice_obj = self.pool.get('account.invoice')
        property_obj = self.pool.get('ir.property')
        sequence_obj = self.pool.get('ir.sequence')
        analytic_journal_obj = self.pool.get('account.analytic.journal')
        account_journal = self.pool.get('account.journal')
        for exp in self.browse(cr, uid, ids):
            lines = []
            for l in exp.line_ids:
                tax_id = []
                tax_tmp = []
                if l.product_id:
                    acc = l.product_id.product_tmpl_id.property_account_expense
                    if not acc:
                        acc = l.product_id.categ_id.property_account_expense_categ
                    tax_tmp = [x.id for x in l.product_id.supplier_taxes_id]

                    tmp_dict = {}
                    for i in l.partner_id.property_account_position.tax_ids:
                        tmp_dict[i.tax_src_id.id] = i.tax_dest_id.id

                    for y in tax_tmp:
                        if y in tmp_dict.keys():
                            tax_id.append(tmp_dict[y])
                        else:
                            tax_id.append(y)
                else:
                    acc = property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category')
                    if not acc:
                        raise osv.except_osv(_('Error !'), _('Please configure Default Expanse account for Product purchase, `property_account_expense_categ`'))

                lines.append((0, False, {
                    'name': l.name,
                    'account_id': acc.id,
                    'price_unit': l.unit_amount,
                    'quantity': l.unit_quantity,
                    'uos_id': l.uom_id.id,
                    'product_id': l.product_id and l.product_id.id or False,
                    'invoice_line_tax_id': tax_id and [(6, 0, tax_id)] or False,
                    'account_analytic_id': l.analytic_account.id,
                }))
            if not exp.employee_id.address_home_id:
                raise osv.except_osv(_('Error !'), _('The employee must have a home address'))
            acc = exp.employee_id.address_home_id.partner_id.property_account_payable.id
            payment_term_id = exp.employee_id.address_home_id.partner_id.property_payment_term.id
            inv = {
                'name': exp.name,
                'reference': sequence_obj.get(cr, uid, 'hr.expense.invoice'),
                'account_id': acc,
                'type': 'in_invoice',
                'partner_id': exp.employee_id.address_home_id.partner_id.id,
                'address_invoice_id': exp.employee_id.address_home_id.id,
                'address_contact_id': exp.employee_id.address_home_id.id,
                'origin': exp.name,
                'invoice_line': lines,
                'currency_id': exp.currency_id.id,
                'payment_term': payment_term_id,
                'fiscal_position': exp.employee_id.address_home_id.partner_id.property_account_position.id
            }
            if payment_term_id:
                to_update = invoice_obj.onchange_payment_term_date_invoice(cr, uid, [], payment_term_id, None)
                if to_update:
                    inv.update(to_update['value'])
            journal = False
            if exp.journal_id:
                inv['journal_id']=exp.journal_id.id
                journal = exp.journal_id
            else:
                journal_id = invoice_obj._get_journal(cr, uid, context={'type': 'in_invoice'})
                if journal_id:
                    inv['journal_id'] = journal_id
                    journal = account_journal.browse(cr, uid, journal_id)
            if journal and not journal.analytic_journal_id:
                analytic_journal_ids = analytic_journal_obj.search(cr, uid, [('type','=','purchase')])
                if analytic_journal_ids:
                    account_journal.write(cr, uid, [journal.id],{'analytic_journal_id':analytic_journal_ids[0]})
            inv_id = invoice_obj.create(cr, uid, inv, {'type': 'in_invoice'})
            invoice_obj.button_compute(cr, uid, [inv_id], {'type': 'in_invoice'}, set_total=True)
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.invoice', inv_id, 'invoice_open', cr)

            self.write(cr, uid, [exp.id], {'invoice_id': inv_id, 'state': 'invoiced'})
            res = inv_id
        return res

hr_expense_expense()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
