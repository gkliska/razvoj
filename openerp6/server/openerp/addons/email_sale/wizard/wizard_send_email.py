# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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

import wizard
import pooler
import tools

from tools.translate import _
from osv import fields,osv
import time
import netsvc
from tools.misc import UpdateableStr, UpdateableDict

email_send_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Send sale order/s by Email">
    <field name="to"/>
    <newline/>
    <field name="subject"/>
    <newline/>
    <separator string="Message:" colspan="4"/>
    <field name="text" nolabel="1" colspan="4"/>
</form>'''

email_send_fields = {
    'to': {'string':"To", 'type':'char', 'size':512, 'required':True},
    'subject': {'string':'Subject', 'type':'char', 'size': 512, 'required':True},
    'text': {'string':'Message', 'type':'text_tag', 'required':True}
}

email_done_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Send sale order/s by Email">
    <field name="email_sent"/>
</form>'''

email_done_fields = {
    'email_sent': {'string':'Quantity of Emails sent', 'type':'integer', 'readonly': True},
}


def _get_defaults(self, cr, uid, data, context):
    p = pooler.get_pool(cr.dbname)
    user = p.get('res.users').browse(cr, uid, uid, context)
    orders = p.get(data['model']).browse(cr, uid, data['ids'], context)

    # Calculate 'subject'
    # Ensure subject is tranlated into partner's language.
    current_lang = context.get('lang')
    context['lang'] = orders[0].partner_id.lang or current_lang
    subject = user.company_id.name+_('. Sale Num.')
    context['lang'] = current_lang

    # Calculate 'text'
    text = '\n--\n' + user.signature

    # Calculate 'to'
    adr_ids = []
    partner_id = orders[0].partner_id.id
    for o in orders:
        if partner_id != o.partner_id.id:
            raise osv.except_osv(_('Warning'), _('You have selected documents for different partners.'))
        if o.name:
            subject = subject + ' ' + o.name
        if o.client_order_ref:
            text = o.client_order_ref + '\n' + text
        if o.partner_order_id.id not in adr_ids:
            adr_ids.append(o.partner_order_id.id)
        if o.partner_invoice_id.id not in adr_ids:
            adr_ids.append(o.partner_invoice_id.id)
        if o.partner_shipping_id.id not in adr_ids:
            adr_ids.append(o.partner_shipping_id.id)
    addresses = p.get('res.partner.address').browse(cr, uid, adr_ids, context)
    to = []
    for adr in addresses:
        if adr.email:
            name = adr.name or adr.partner_id.name
            # The adr.email field can contain several email addresses separated by ,
            to.extend(['%s <%s>' % (name, email) for email in adr.email.split(',')])
    to = ','.join(to)

    return {'to': to, 'subject': subject, 'text': text}


def create_report(cr, uid, res_ids, report_name=False, file_name=False):
    if not report_name or not res_ids:
        return (False, Exception('Report name and Resources ids are required !!!'))
    try:
        ret_file_name = '/tmp/'+file_name+'.pdf'
        service = netsvc.LocalService("report."+report_name)
        (result, format) = service.create(cr, uid, res_ids, {'model': 'sale.order'}, {})
        fp = open(ret_file_name, 'wb+');
	try:
		fp.write(result);
	finally:
		fp.close();
    except Exception,e:
        print 'Exception in create report:',e
        return (False, str(e))
    return (True, ret_file_name)


def _send_mails(self, cr, uid, data, context):
    import re
    p = pooler.get_pool(cr.dbname)

    user = p.get('res.users').browse(cr, uid, uid, context)
    file_name = user.company_id.name.replace(' ','_')+'_'+_('Sale_Order')
    sale_smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','sale'),('state','=','confirm'),('active','=',True)], context=False)
    if not sale_smtpserver_id:
        default_smtpserver_id = p.get('email.smtpclient').search(cr, uid, [('type','=','default'),('state','=','confirm'),('active','=',True)], context=False)
    smtpserver_id = sale_smtpserver_id or default_smtpserver_id
    if smtpserver_id:
        smtpserver_id = smtpserver_id[0]
    else:
        raise osv.except_osv(_('Error'), _('No SMTP Server has been defined!'))

    # Create report to send as file attachments
    report = create_report(cr, uid, data['ids'], data['model'], file_name)
    attachments = report[0] and [report[1]] or []

    nbr = 0
    for email in data['form']['to'].split(','):
        #print email, data['form']['subject'], data['ids'], data['model'], file_name, data['form']['text']
        state = p.get('email.smtpclient').send_email(cr, uid, smtpserver_id, email, data['form']['subject'], data['form']['text'], attachments)
        if not state:
            raise osv.except_osv(_('Error sending email'), _('Please check the Server Configuration!'))
        nbr += 1

    # Add a partner event
    docs = p.get(data['model']).browse(cr, uid, data['ids'], context)
    partner_id = docs[0].partner_id.id
    c_id = p.get('res.partner.canal').search(cr ,uid, [('name','ilike','EMAIL'),('active','=',True)])
    c_id = c_id and c_id[0] or False
    p.get('res.partner.event').create(cr, uid,
            {'name': _('Email sent through sale order wizard'),
             'partner_id': partner_id,
             'description': _('To: ').encode('utf-8') + data['form']['to'] +
                            _('\n\nSubject: ').encode('utf-8') + data['form']['subject'] +
                            _('\n\nText:\n').encode('utf-8') + data['form']['text'],
             'document': data['model']+','+str(docs[0].id),
             'canal_id': c_id,
             'user_id': uid, })
    return {'email_sent': nbr}


class send_email(wizard.interface):
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch': email_send_form, 'fields': email_send_fields, 'state':[('end','Cancel'), ('send','Send Email')]}
        },
        'send': {
            'actions': [_send_mails],
            'result': {'type': 'form', 'arch': email_done_form, 'fields': email_done_fields, 'state': [('end', 'End')] }
        }
    }
send_email('sale.order.email_send_2')
