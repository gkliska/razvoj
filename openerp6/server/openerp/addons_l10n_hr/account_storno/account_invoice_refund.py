
#Copy-paste of refund method and account_invoice_refund.py 

from osv import fields, osv, orm


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def refund(self, cr, uid, ids, date=None, period_id=None, description=None, journal_id=None):
        invoices = self.read(cr, uid, ids, ['name', 'type', 'number', 'reference', 'comment', 'date_due', 'partner_id', 'address_contact_id', 'address_invoice_id', 'partner_contact', 'partner_insite', 'partner_ref', 'payment_term', 'account_id', 'currency_id', 'invoice_line', 'tax_line', 'journal_id'])
        obj_invoice_line = self.pool.get('account.invoice.line')
        obj_invoice_tax = self.pool.get('account.invoice.tax')
        obj_journal = self.pool.get('account.journal')
        new_ids = []
        for invoice in invoices:
            del invoice['id']

            type_dict = {
                'out_invoice': 'out_refund', # Customer Invoice
                'in_invoice': 'in_refund',   # Supplier Invoice
                'out_refund': 'out_invoice', # Customer Refund
                'in_refund': 'in_invoice',   # Supplier Refund
            }

            invoice_lines = obj_invoice_line.read(cr, uid, invoice['invoice_line'])
            invoice_lines = self._refund_cleanup_lines(cr, uid, invoice_lines)

            tax_lines = obj_invoice_tax.read(cr, uid, invoice['tax_line'])
            tax_lines = filter(lambda l: l['manual'], tax_lines)
            tax_lines = self._refund_cleanup_lines(cr, uid, tax_lines)
            if journal_id:
                refund_journal_ids = [journal_id]
            elif invoice['type'] == 'in_invoice':
                refund_journal_ids = obj_journal.search(cr, uid, [('type','=','purchase_refund')])
            else:
                refund_journal_ids = obj_journal.search(cr, uid, [('type','=','sale_refund')])

            #STORNO-begin#  # makes same document qty *(-1)
            invoice_journal= obj_journal.browse(cr, uid, invoice['journal_id'][0])
            if invoice_journal.storno_contra == 'storno':
                type_dict = {  
                    'out_invoice': 'out_invoice', # Customer Invoice
                    'in_invoice': 'in_invoice',   # Supplier Invoice
                    'out_refund': 'out_refund', # Customer Refund
                    'in_refund': 'in_refund',   # Supplier Refund
                }
            for invoice_line in invoice_lines:
                invoice_line[2]['quantity'] =invoice_line[2].get('quantity',0.0) *(-1)
            for tax_line in tax_lines:
                tax_line[2]['base']       = tax_line[2].get('base'       ,0.0) * (-1)
                tax_line[2]['amount']     = tax_line[2].get('amount'     ,0.0) * (-1)
                tax_line[2]['base_amount']= tax_line[2].get('base_amount',0.0) * (-1)
                tax_line[2]['tax_amount'] = tax_line[2].get('tax_amount' ,0.0) * (-1)

            refund_journal_ids = [ invoice['journal_id'][0] ]

            #STORNO-end#  


            if not date:
                date = time.strftime('%Y-%m-%d')
            invoice.update({
                'type': type_dict[invoice['type']],
                'date_invoice': date,
                'state': 'draft',
                'number': False,
                'invoice_line': invoice_lines,
                'tax_line': tax_lines,
                'journal_id': refund_journal_ids
            })
            if period_id:
                invoice.update({
                    'period_id': period_id,
                })
            if description:
                invoice.update({
                    'name': description,
                })
            # take the id part of the tuple returned for many2one fields
            for field in ('address_contact_id', 'address_invoice_id', 'partner_id',
                    'account_id', 'currency_id', 'payment_term', 'journal_id'):
                invoice[field] = invoice[field] and invoice[field][0]
            # create the new invoice
            new_ids.append(self.create(cr, uid, invoice))

        return new_ids


account_invoice()

    
class account_invoice_refund(osv.osv_memory):
    _inherit = "account.invoice.refund"

    """Refunds invoice
    _description = "Invoice Refund"
    _columns = {
       'date': fields.date('Operation date', help='This date will be used as the invoice date for Refund Invoice and Period will be chosen accordingly!'),
       'period': fields.many2one('account.period', 'Force period'),
       'journal_id': fields.many2one('account.journal', 'Refund Journal', help='You can select here the journal to use for the refund invoice that will be created. If you leave that field empty, it will use the same journal as the current invoice.'),
       'description': fields.char('Description', size=128, required=True),
       'filter_refund': fields.selection([('modify', 'Modify'), ('refund', 'Refund'), ('cancel', 'Cancel')], "Refund Type", required=True, help='Refund invoice base on this type. You can not Modify and Cancel if the invoice is already reconciled'),
    }
"""

    _columns = {
       'date'       : fields.date('Operation date', help='This date will be used as the invoice date for Refund Invoice and Period will be chosen accordingly!'),
       'period'     : fields.many2one('account.period', 'Force period'),
       'journal_id' : fields.many2one('account.journal', 'Refund Journal',
                                       help='You can select here the journal to use for the refund invoice that will be created. If you leave that field empty, it will use the same journal as the current invoice.'),
       'description': fields.char('Description', size=128, required=True),
       'filter_refund': fields.selection([('modify', 'Modify'),
                                          ('refund', 'Refund'),
                                          ('cancel', 'Cancel')],
                                          "Refund Type", required=True,
                                           help='Refund invoice base on this type. You can not Modify and Cancel if the invoice is already reconciled'),
    }
    def _get_journal(self, cr, uid, context=None):
        obj_journal = self.pool.get('account.journal')
        """
        if context is None:
            context = {}
        journal = obj_journal.search(cr, uid, [('type', '=', 'sale_refund')])
        if context.get('type', False):
            if context['type'] in ('in_invoice', 'in_refund'):
                journal = obj_journal.search(cr, uid, [('type', '=', 'purchase_refund')])
        """    
        #storno TODO read it from journal new field "storno_journal"   
        journal = obj_journal.search(cr, uid, [('type', '=', 'sale')])
        if context.get('type', False):
            journal = obj_journal.search(cr, uid, [('type', '=', context['type'])])
                
        return journal and journal[0] or False

    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'journal_id': _get_journal,
        'filter_refund': 'modify',
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        journal_obj = self.pool.get('account.journal')
        res = super(account_invoice_refund,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = context.get('journal_type', 'sale_refund')
        if type in ('sale', 'sale_refund'):
            type = 'sale_refund'
        else:
            type = 'purchase_refund'

        #storno    
        type = context.get('journal_type', 'sale')

        for field in res['fields']:
            if field == 'journal_id':
                journal_select = journal_obj._name_search(cr, uid, '', [('type', '=', type)], context=context, limit=None, name_get_uid=1)
                res['fields'][field]['selection'] = journal_select
        return res

    def compute_refund(self, cr, uid, ids, mode='refund', context=None):
        """
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: the account invoice refund’s ID or list of IDs

        """
        inv_obj = self.pool.get('account.invoice')
        reconcile_obj = self.pool.get('account.move.reconcile')
        account_m_line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        wf_service = netsvc.LocalService('workflow')
        inv_tax_obj = self.pool.get('account.invoice.tax')
        inv_line_obj = self.pool.get('account.invoice.line')
        res_users_obj = self.pool.get('res.users')
        if context is None:
            context = {}

        for form in  self.read(cr, uid, ids, context=context):
            created_inv = []
            date = False
            period = False
            description = False
            company = res_users_obj.browse(cr, uid, uid, context=context).company_id
            journal_id = form.get('journal_id', False)
            for inv in inv_obj.browse(cr, uid, context.get('active_ids'), context=context):
                if inv.state in ['draft', 'proforma2', 'cancel']:
                    raise osv.except_osv(_('Error !'), _('Can not %s draft/proforma/cancel invoice.') % (mode))
                if inv.reconciled and mode in ('cancel', 'modify'):
                    raise osv.except_osv(_('Error !'), _('Can not %s invoice which is already reconciled, invoice should be unreconciled first. You can only Refund this invoice') % (mode))
                if form['period']:
                    period = form['period']
                else:
                    period = inv.period_id and inv.period_id.id or False

                if not journal_id:
                    journal_id = inv.journal_id.id

                if form['date']:
                    date = form['date']
                    if not form['period']:
                            cr.execute("select name from ir_model_fields \
                                            where model = 'account.period' \
                                            and name = 'company_id'")
                            result_query = cr.fetchone()
                            if result_query:
                                cr.execute("""select p.id from account_fiscalyear y, account_period p where y.id=p.fiscalyear_id \
                                    and date(%s) between p.date_start AND p.date_stop and y.company_id = %s limit 1""", (date, company.id,))
                            else:
                                cr.execute("""SELECT id
                                        from account_period where date(%s)
                                        between date_start AND  date_stop  \
                                        limit 1 """, (date,))
                            res = cr.fetchone()
                            if res:
                                period = res[0]
                else:
                    date = inv.date_invoice
                if form['description']:
                    description = form['description']
                else:
                    description = inv.name

                if not period:
                    raise osv.except_osv(_('Data Insufficient !'), \
                                            _('No Period found on Invoice!'))

                refund_id = inv_obj.refund(cr, uid, [inv.id], date, period, description, journal_id)
                refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                inv_obj.write(cr, uid, [refund.id], {'date_due': date,
                                                'check_total': inv.check_total})
                inv_obj.button_compute(cr, uid, refund_id)

                created_inv.append(refund_id[0])
                if mode in ('cancel', 'modify'):
                    movelines = inv.move_id.line_id
                    to_reconcile_ids = {}
                    for line in movelines:
                        if line.account_id.id == inv.account_id.id:
                            to_reconcile_ids[line.account_id.id] = [line.id]
                        if type(line.reconcile_id) != osv.orm.browse_null:
                            reconcile_obj.unlink(cr, uid, line.reconcile_id.id)
                    wf_service.trg_validate(uid, 'account.invoice', \
                                        refund.id, 'invoice_open', cr)
                    refund = inv_obj.browse(cr, uid, refund_id[0], context=context)
                    for tmpline in  refund.move_id.line_id:
                        if tmpline.account_id.id == inv.account_id.id:
                            to_reconcile_ids[tmpline.account_id.id].append(tmpline.id)
                    for account in to_reconcile_ids:
                        account_m_line_obj.reconcile(cr, uid, to_reconcile_ids[account],
                                        writeoff_period_id=period,
                                        writeoff_journal_id = inv.journal_id.id,
                                        writeoff_acc_id=inv.account_id.id
                                        )
                    if mode == 'modify':
                        invoice = inv_obj.read(cr, uid, [inv.id],
                        #STORNO invoice = inv_obj.read(cr, uid, refund_id[0],
                                    ['name', 'type', 'number', 'reference',
                                    'comment', 'date_due', 'partner_id',
                                    'address_contact_id', 'address_invoice_id',
                                    'partner_insite', 'partner_contact',
                                    'partner_ref', 'payment_term', 'account_id',
                                    'currency_id', 'invoice_line', 'tax_line',
                                    'journal_id', 'period_id'], context=context)
                        invoice = invoice[0]
                        del invoice['id']
                        invoice_lines = inv_line_obj.read(cr, uid, invoice['invoice_line'], context=context)
                        invoice_lines = inv_obj._refund_cleanup_lines(cr, uid, invoice_lines)
                        tax_lines = inv_tax_obj.read(cr, uid, invoice['tax_line'], context=context)
                        tax_lines = inv_obj._refund_cleanup_lines(cr, uid, tax_lines)
                        
                        invoice.update({
                            'type': inv.type,
                            'date_invoice': date,
                            'state': 'draft',
                            'number': False,
                            'invoice_line': invoice_lines,
                            'tax_line': tax_lines,
                            'period_id': period,
                            'name': description
                        })
                        for field in ('address_contact_id', 'address_invoice_id', 'partner_id',
                                'account_id', 'currency_id', 'payment_term', 'journal_id'):
                                invoice[field] = invoice[field] and invoice[field][0]
                        inv_id = inv_obj.create(cr, uid, invoice, {})
                        if inv.payment_term.id:
                            data = inv_obj.onchange_payment_term_date_invoice(cr, uid, [inv_id], inv.payment_term.id, date)
                            if 'value' in data and data['value']:
                                inv_obj.write(cr, uid, [inv_id], data['value'])
                        created_inv.append(inv_id)
            if inv.type in ('out_invoice', 'out_refund'):
                xml_id = 'action_invoice_tree3'
            else:
                xml_id = 'action_invoice_tree4'
            result = mod_obj.get_object_reference(cr, uid, 'account', xml_id)
            id = result and result[1] or False
            result = act_obj.read(cr, uid, id, context=context)
            invoice_domain = eval(result['domain'])
            invoice_domain.append(('id', 'in', created_inv))
            result['domain'] = invoice_domain
            return result

    def invoice_refund(self, cr, uid, ids, context=None):
        data_refund = self.read(cr, uid, ids, [],context=context)[0]['filter_refund']
        return self.compute_refund(cr, uid, ids, data_refund, context=context)


account_invoice_refund()
