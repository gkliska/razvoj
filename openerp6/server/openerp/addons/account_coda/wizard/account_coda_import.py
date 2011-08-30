# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (c) 2011 Noviat nv/sa (www.noviat.be). All rights reserved.
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

import time
import base64
from osv import fields,osv
from tools.translate import _
import netsvc
import re
logger=netsvc.Logger()

class account_coda_import(osv.osv_memory):
    _name = 'account.coda.import'
    _description = 'Import CODA File'
    _columns = {
        'def_payable': fields.many2one('account.account', 'Default Payable Account', domain=[('type', '=', 'payable')], required=True,
            help= 'Set here the payable account that will be used, by default, if the partner is not found.'),
        'def_receivable': fields.many2one('account.account', 'Default Receivable Account', domain=[('type', '=', 'receivable')], required=True,
            help= 'Set here the receivable account that will be used, by default, if the partner is not found.',),
        'transfer_account': fields.many2one('account.account', 'Default Internal Transfer Account', domain=[('code', 'like', '58%'), ('type', '!=', 'view')], required=True,
            help= 'Set here the default account that will be used for internal transfer between own bank accounts (e.g. transfer between current and deposit bank accounts).'),
        'awaiting_account': fields.many2one('account.account', 'Default Account for Unrecognized Movement', domain=[('type', '!=', 'view')], required=True,
            help= 'Set here the default account that will be used if the partner cannot be unambiguously identified.'),
        'coda_data': fields.binary('CODA File', required=True),
        'coda_fname': fields.char('CODA Filename', size=128, required=True),
        'note':fields.text('Log'),
    }
    _defaults = {
        'coda_fname': lambda *a: '',
    }
        
    def coda_parsing(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data=self.browse(cr,uid,ids)[0]
        try:
            codafile = data.coda_data
            codafilename = data.coda_fname
            def_pay_acc = data.def_payable.id
            def_rec_acc = data.def_receivable.id
            transfer_acc = data.transfer_account.id
            awaiting_acc = data.awaiting_account.id
            
        except:
            raise osv.except_osv(_('Error!'), _('Wizard in incorrect state. Please hit the Cancel button!'))
            return {}
    
        journal_obj = self.pool.get('account.journal')
        period_obj = self.pool.get('account.period')
        partner_bank_obj = self.pool.get('res.partner.bank')
        trans_type_obj = self.pool.get('account.coda.trans.type')
        trans_code_obj = self.pool.get('account.coda.trans.code')
        trans_category_obj = self.pool.get('account.coda.trans.category')
        comm_type_obj = self.pool.get('account.coda.comm.type')
        coda_obj = self.pool.get('account.coda')
        coda_st_obj = self.pool.get('coda.bank.statement')
        coda_st_line_obj = self.pool.get('coda.bank.statement.line')
        inv_obj = self.pool.get('account.invoice')
        mod_obj = self.pool.get('ir.model.data')
        
        err_log = ''
        coda_bank_statements = []
        recordlist = base64.decodestring(codafile).split('\n')
        for line in recordlist:
            
            if not line:
                pass
            elif line[0] == '0':
                # start of a new statement within the CODA file
                coda_statement = {}
                coda_parsing_note = ''
                coda_statement_lines = {}
                st_line_seq = 0
                glob_lvl_stack = [0]
                # header data
                coda_statement['version'] = line[127]
                coda_version = line[127]
                if coda_version not in ['1','2']:
                    raise osv.except_osv(_('Data Error!'),
                        _('CODA V%s statements are not supported, please contact your bank!') % coda_version)
                coda_statement['coda_statement_lines'] = {}
                coda_statement['date'] = str2date(line[5:11])
                period_id = period_obj.search(cr , uid, [('date_start' ,'<=', coda_statement['date']), ('date_stop','>=',coda_statement['date'])])
                if not period_id:
                    raise osv.except_osv(_('Data Error!'), 
                        _("The CODA creation date doesn't fall within a defined Accounting Period!" \
                          "\nPlease create the Accounting Period for date %s.") % coda_statement['date'])
                coda_statement['period_id'] = period_id[0]
                coda_statement['state'] = 'draft'
                
            elif line[0] == '1':
                if coda_version == '1':
                    coda_statement['acc_number'] = line[5:17]
                elif line[1] == '0':                                # Belgian bank account BBAN structure
                    coda_statement['acc_number'] = line[5:17]
                    if line[18:21] <> 'EUR':
                        raise osv.except_osv(_('Data Error!'),
                            _('only bank accounts in EUR are supported !'))                
                elif line[1] == '1':    # foreign bank account BBAN structure
                    raise osv.except_osv(_('Data Error!'),
                        _('Foreign bank accounts with BBAN structure are not supported !'))
                elif line[1] == '2':    # Belgian bank account IBAN structure
                    coda_statement['acc_number']=line[5:21] 
                    if line[39:42] <> 'EUR':
                        raise osv.except_osv(_('Data Error!'),
                            _('only bank accounts in EUR are supported !'))
                elif line[1] == '3':    # foreign bank account IBAN structure
                    raise osv.except_osv(_('Data Error!'),
                         _('Foreign bank accounts with IBAN structure are not supported !'))
                else:
                    raise osv.except_osv(('Data Error!'),
                         _('Unsupported bank account structure !'))                          
                journal_obj_ids = journal_obj.search(cr , uid, [('coda_bank_acc' ,'=', coda_statement['acc_number'])]) 
                if journal_obj_ids:
                    journal = journal_obj.browse(cr, uid, journal_obj_ids[0], context)
                    coda_statement['journal_id'] = journal.id
                else:
                    raise osv.except_osv(_('Data Error!'),
                        _("No matching Financial Journal found !") +
                        _("\nPlease check if the 'Bank Account Number' field of your Bank Journal matches with '%s' !") % coda_statement['acc_number'])
                bal_start = list2float(line[43:58])             # old balance data
                if line[42] == '1':    # 1= Debit
                    bal_start = - bal_start
                coda_statement['balance_start'] = bal_start            
                coda_statement['acc_holder'] = line[64:90]
                coda_statement['paper_seq_number'] = line[2:5]
                coda_statement['coda_seq_number'] = line[125:128]
                if journal.coda_st_naming:
                    coda_statement['name'] = journal.coda_st_naming % {
                       'code': journal.code,                                                    
                       'year': time.strftime('%Y'),
                       'y': time.strftime('%y'),
                       'coda': line[125:128],
                       'paper': line[2:5],
                    }
                else:
                    coda_statement['name'] = '/'
                    
            elif line[0] == '2':
                # movement data record 2
                if line[1] == '1':
                    # movement data record 2.1
                    st_line = {}
                    st_line_seq = st_line_seq + 1
                    st_line['sequence'] = st_line_seq
                    st_line['type'] = 'general'                
                    st_line['struct_comm_type'] = ''
                    st_line['struct_comm_type_desc'] = ''
                    st_line['struct_comm_101'] = ''
                    st_line['communication'] = ''
                    st_line['partner_id'] = 0
                    st_line['account_id'] = 0
                    st_line['counterparty_name'] = ''
                    st_line['counterparty_number'] = ''
                    st_line['globalisation_level'] = False
                    st_line['globalisation_amount'] = False
                    st_line['amount'] = False
                          
                    st_line['ref'] = line[2:10]
                    # positions 11-31 not processed (informational bank ref nbr) 
                    st_line_amt = list2float(line[32:47])
                    if line[31] == '1':    # 1=debit
                        st_line_amt = - st_line_amt
                    # processing of amount depending on globalisation code    
                    glob_lvl = int(line[124])
                    if glob_lvl > 0: 
                        if glob_lvl_stack[-1] == glob_lvl: 
                            st_line['amount'] = st_line_amt
                            glob_lvl_stack.pop()
                        else:
                            glob_lvl_stack.append(glob_lvl)
                            st_line['type'] = 'globalisation'
                            st_line['globalisation_level'] = glob_lvl
                            st_line['globalisation_amount'] = st_line_amt
                            st_line['account_id'] = None
                    else:
                        st_line['amount'] = st_line_amt
                    # positions 48-53 : Value date or 000000 if not known (DDMMYY)
                    st_line['val_date'] = str2date(line[47:53])
                    # positions 54-61 : transaction code
                    st_line['trans_type'] = line[53]
                    trans_type_ids = trans_type_obj.search(cr , uid, [('type' ,'=', st_line['trans_type'])])
                    if not trans_type_ids:
                        raise osv.except_osv(_('Data Error!'), 
                            _('The File contains an invalid CODA Transaction Type : %s!') % (st_line['trans_type']))
                    st_line['trans_type_desc'] = trans_type_obj.browse(cr, uid, trans_type_ids[0], context).description          
                    st_line['trans_family'] = line[54:56]
                    trans_family_ids = trans_code_obj.search(cr , uid, 
                        [('type', '=', 'family'),('code', '=', st_line['trans_family'])])
                    if not trans_family_ids:
                        raise osv.except_osv(_('Data Error!'), 
                            _('The File contains an invalid CODA Transaction Family : %s!') % (st_line['trans_family']))
                    st_line['trans_family_desc'] = trans_code_obj.browse(cr, uid, trans_family_ids[0], context).description
                    st_line['trans_code'] = line[56:58]
                    trans_code_ids = trans_code_obj.search(cr , uid, 
                        [('parent_id', '=', trans_family_ids[0]),('type', '=', 'code'),('code', '=', st_line['trans_code'])])
                    if trans_code_ids:
                        st_line['trans_code_desc'] = trans_code_obj.browse(cr, uid, trans_code_ids[0], context).description
                    else:
                        st_line['trans_code_desc'] = _('Transaction Code unknown, please consult your bank.')
                    st_line['trans_category'] = line[58:61]
                    trans_category_ids = trans_category_obj.search(cr , uid, [('category' ,'=', st_line['trans_category'])])
                    if trans_category_ids:
                        st_line['trans_category_desc'] = trans_category_obj.browse(cr, uid, trans_category_ids[0], context).description
                    else:
                        st_line['trans_category_desc'] = _('Transaction Category unknown, please consult your bank.')              
                    # positions 61-115 : communication                
                    if line[61] == '1':
                        st_line['struct_comm_type'] = line[62:65]
                        comm_code_ids = comm_type_obj.search(cr , uid, [('code' ,'=', st_line['struct_comm_type'])])
                        if not comm_code_ids:
                            raise osv.except_osv(_('Data Error!'), 
                                _('The File contains an invalid Structured Communication Type : %s!') % (st_line['struct_comm_type']))
                        st_line['struct_comm_type_desc'] = comm_type_obj.browse(cr, uid, comm_code_ids[0], context).description
                        st_line['communication'] = st_line['name'] = line[65:115]
                        if st_line['struct_comm_type'] == '101':
                            bbacomm = line[65:77]   
                            st_line['struct_comm_101'] = st_line['name'] = '+++' + bbacomm[0:3] + '/' + bbacomm[3:7] + '/' + bbacomm[7:] + '+++'     
                    else:
                        st_line['communication'] = st_line['name'] = line[62:115]
                    st_line['entry_date'] = str2date(line[115:121])
                    # positions 122-124 not processed 
                    coda_statement_lines[st_line['ref']] = st_line
                    coda_statement['coda_statement_lines'] = coda_statement_lines
                elif line[1] == '2':
                    # movement data record 2.2
                    st_line_name = line[2:10]
                    coda_statement['coda_statement_lines'][st_line_name]['communication'] += line[10:63]
                elif line[1] == '3':
                    # movement data record 2.3
                    st_line_name = line[2:10]
                    st_line = coda_statement_lines[st_line_name]
                    if coda_version == '1':
                        counterparty_number = line[10:22]
                        counterparty_name = line[47:125].strip()
                    else:
                        counterparty_number = line[10:47].strip()
                        counterparty_name = line[47:82].strip()
                        st_line['communication'] += line[82:125]
                    st_line['counterparty_number'] = counterparty_number
                    st_line['counterparty_name'] = counterparty_name

                    # partner matching
                    if st_line['type'] == 'general':                    
                        match = False
                        bank_ids = False
                        #
                        # remark : bba structured communication lookup needs further work after porting the prereq V5 bbacomm code to V6
                        #
                        reference = st_line['struct_comm_101']
                        if reference:
                            inv_ids = inv_obj.search(cr , uid, [('reference' ,'=', reference), ('state', '=', 'open')])
                            if inv_ids:
                                partner = inv_obj.browse(cr, uid, inv_ids[0]).partner_id
                                st_line['partner_id'] = partner.id
                                st_line['invoice_id'] = inv_ids[0]
                                match = True
                        #
                        if not match and counterparty_number:
                            journal_ids = journal_obj.search(cr , uid, [('coda_bank_acc' ,'=', counterparty_number)])
                            if journal_ids:                               
                                st_line['account_id'] = transfer_acc
                                match = True
                            else:
                                bank_ids = partner_bank_obj.search(cr,uid,[('acc_number','=', counterparty_number)])
                        if not match and bank_ids:
                            if len(bank_ids) > 1:
                                coda_parsing_note += _("\n    Bank Statement '%s' line '%s':" \
                                    "\n        No partner record assigned: There are multiple partners with the same Bank Account Number '%s'!" \
                                    "\n        Please correct the configuration and perform the import again or otherwise change the corresponding entry manually in the generated Bank Statement.") \
                                    % (coda_statement['name'], st_line_name, counterparty_number)
                            else:    
                                bank = partner_bank_obj.browse(cr, uid, bank_ids[0], context)
                                st_line['partner_id'] = bank.partner_id.id
                                match = True 
                        elif not match:
                            if counterparty_number:
                                coda_parsing_note += _("\n    Bank Statement '%s' line '%s':" \
                                    "\n        The bank account '%s' is not defined for the partner '%s'!" \
                                    "\n        Please correct the configuration and perform the import again or otherwise change the corresponding entry manually in the generated Bank Statement.") \
                                    % (coda_statement['name'], st_line_name, 
                                    counterparty_number, counterparty_name)
                            else:
                                coda_parsing_note += _("\n    Bank Statement '%s' line '%s':" \
                                    "\n        No matching partner record found!" \
                                    "\n        Please adjust the corresponding entry manually in the generated Bank Statement.") \
                                    % (coda_statement['name'], st_line_name) 
                            st_line['account_id'] = awaiting_acc
                    # end of partner record lookup
                    coda_statement_lines[st_line_name] = st_line
                    coda_statement['coda_statement_lines'] = coda_statement_lines
                else:
                    # movement data record 2.x (x <> 1,2,3)
                    raise osv.except_osv(_('Data Error!'),
                         _('Movement data records of type 2.%s are not supported !') % (line[1]))
                
            elif line[0] == '3':
                # information data record 3
                if line[1] == '1':
                    # information data record 3.1
                    info_line = {}
                    info_line['entry_date'] = st_line['entry_date']
                    info_line['type'] = 'information'
                    st_line_seq = st_line_seq + 1
                    info_line['sequence'] = st_line_seq
                    info_line['struct_comm_type'] = ''
                    info_line['struct_comm_type_desc'] = ''
                    info_line['communication'] = ''
                    info_line['ref'] = line[2:10]
                    # positions 11-31 not processed (informational bank ref nbr) 
                    # positions 32-38 : transaction code
                    info_line['trans_type'] = line[31]
                    trans_type_ids = trans_type_obj.search(cr , uid, [('type' ,'=', info_line['trans_type'])])
                    if not trans_type_ids:
                        raise osv.except_osv(_('Data Error!'), 
                            _('The File contains an invalid CODA Transaction Type : %s!') % (info_line['trans_type']))
                    info_line['trans_type_desc'] = trans_type_obj.browse(cr, uid, trans_type_ids[0], context).description          
                    info_line['trans_family'] = line[32:34]
                    trans_family_ids = trans_code_obj.search(cr , uid, 
                        [('type', '=', 'family'),('code', '=', info_line['trans_family'])])
                    if not trans_family_ids:
                        raise osv.except_osv(_('Data Error!'), 
                            _('The File contains an invalid CODA Transaction Family : %s!') % (info_line['trans_family']))
                    info_line['trans_family_desc'] = trans_code_obj.browse(cr, uid, trans_family_ids[0], context).description
                    info_line['trans_code'] = line[34:36]
                    trans_code_ids = trans_code_obj.search(cr , uid, 
                        [('parent_id', '=', trans_family_ids[0]),('type', '=', 'code'),('code', '=', info_line['trans_code'])])
                    if trans_code_ids:
                        info_line['trans_code_desc'] = trans_code_obj.browse(cr, uid, trans_code_ids[0], context).description
                    else:
                        info_line['trans_code_desc'] = _('Transaction Code unknown, please consult your bank.')
                    info_line['trans_category'] = line[36:39]
                    trans_category_ids = trans_category_obj.search(cr , uid, [('category' ,'=', info_line['trans_category'])])
                    if trans_category_ids:
                        info_line['trans_category_desc'] = trans_category_obj.browse(cr, uid, trans_category_ids[0], context).description
                    else:
                        info_line['trans_category_desc'] = _('Transaction Category unknown, please consult your bank.')              
                    # positions 40-113 : communication                
                    if line[39] == '1':
                        info_line['struct_comm_type'] = line[40:43]
                        comm_code_ids = comm_type_obj.search(cr , uid, [('code' ,'=', info_line['struct_comm_type'])])
                        if not comm_code_ids:
                            raise osv.except_osv(_('Data Error!'), 
                                _('The File contains an invalid Structured Communication Type : %s!') % (info_line['struct_comm_type']))
                        info_line['struct_comm_type_desc'] = comm_type_obj.browse(cr, uid, comm_code_ids[0], context).description
                        info_line['communication'] = info_line['name'] = line[43:113]
                    else:
                        info_line['communication'] = info_line['name'] = line[40:113]
                    # positions 114-128 not processed
                    coda_statement_lines[info_line['ref']] = info_line
                    coda_statement['coda_statement_lines'] = coda_statement_lines
                elif line[1] == '2':
                    # information data record 3.2
                    info_line_name = line[2:10]
                    coda_statement['coda_statement_lines'][info_line_name]['communication'] += line[10:115]
                elif line[1] == '3':
                    # information data record 3.3
                    info_line_name = line[2:10]
                    coda_statement['coda_statement_lines'][info_line_name]['communication'] += line[10:100]
                   
            elif line[0] == '4':
                # free communication data record 4
                comm_line = {}
                comm_line['type'] = 'communication'
                st_line_seq = st_line_seq + 1
                comm_line['sequence'] = st_line_seq
                comm_line['ref'] = line[2:10]
                comm_line['communication'] = comm_line['name'] = line[32:112]
                coda_statement_lines[comm_line['ref']] = comm_line
                coda_statement['coda_statement_lines'] = coda_statement_lines
    
            elif line[0] == '8':
                # new balance record
                bal_end = list2float(line[42:57])
                if line[41] == '1':    # 1=Debit
                    bal_end = - bal_end
                coda_statement['balance_end_real'] = bal_end
    
            elif line[0] == '9':
                # footer record
                if coda_parsing_note:                
                    coda_statement['coda_parsing_note'] = '\nPartner record matching results:' + coda_parsing_note
                else:
                    coda_statement['coda_parsing_note'] = ''
                coda_bank_statements.append(coda_statement)
        #end for
        
        nb_err = 0
        err_log = _('CODA Import failed !')
        coda_id = 0
        coda_note = ''
        line_note = ''
        
        coda_id = coda_obj.search(cr, uid,[
            ('name', '=', codafilename),
            ('coda_creation_date', '=', coda_statement['date']),
            ])
        if coda_id:
            raise osv.except_osv(_('CODA Import failed !'),
                _("CODA file with Filename '%s' and Creation Date '%s' has already been imported !")
                % (codafilename, coda_statement['date']))    
        
        try:
            coda_id = coda_obj.create(cr, uid,{
                'name' : codafilename,
                'coda_data': codafile,
                'coda_creation_date' : coda_statement['date'],
                'date': time.strftime('%Y-%m-%d'),
                'user_id': uid,
                })
            context.update({'coda_id': coda_id})
    
        except osv.except_osv, e:
            cr.rollback()
            nb_err += 1
            err_log = err_log +'\n\nApplication Error : ' + str(e)
        except Exception, e:
            cr.rollback()
            nb_err += 1
            err_log = err_log +'\n\nSystem Error : ' +str(e)       
        except :
            cr.rollback()
            nb_err += 1
            err_log = err_log +'\n\nUnknown Error'        

        coda_st_ids = []
        bk_st_ids = []      
        for statement in coda_bank_statements:
            try:
                
                coda_st_id = coda_st_obj.create(cr, uid, {
                    'name': statement.get('name', '/'),
                    'journal_id': statement['journal_id'],
                    'coda_id': coda_id,
                    'date': statement['date'],
                    'period_id': statement['period_id'],
                    'balance_start': statement['balance_start'],
                    'balance_end_real': statement['balance_end_real'],
                    'state':'draft',
                })
    
                lines = statement['coda_statement_lines']
                for value in lines:
                    line = lines[value]
                    
                    if line['type'] == 'information':
                        line_note = _('Transaction Type' ': %s - %s'                \
                            '\nTransaction Family: %s - %s'                         \
                            '\nTransaction Code: %s - %s'                           \
                            '\nTransaction Category: %s - %s'                       \
                            '\nStructured Communication Type: %s - %s'              \
                            '\nCommunication: %s')                                  \
                            %(line['trans_type'], line['trans_type_desc'],
                              line['trans_family'], line['trans_family_desc'],
                              line['trans_code'], line['trans_code_desc'],
                              line['trans_category'], line['trans_category_desc'],
                              line['struct_comm_type'], line['struct_comm_type_desc'],
                              line['communication'])
    
                        id = coda_st_line_obj.create(cr, uid, {
                                   'sequence': line['sequence'],
                                   'ref': line['ref'],                                           
                                   'name': line['name'],
                                   'type' : 'information',               
                                   'date': line['entry_date'],                
                                   'statement_id': coda_st_id,
                                   'note': line_note,
                                   })
                            
                    elif line['type'] == 'communication':
                        line_note = _('Free Communication:\n %s')                  \
                            %(line['communication'])
    
                        id = coda_st_line_obj.create(cr, uid, {
                                   'sequence': line['sequence'],
                                   'ref': line['ref'],                                                 
                                   'name': line['name'],
                                   'type' : 'communication',
                                   'date': statement['date'],
                                   'statement_id': coda_st_id,
                                   'note': line_note,
                                   })
    
                    else:
                        line_note = _('Partner name: %s \nPartner Account Number: %s' \
                            '\nTransaction Type: %s - %s'                             \
                            '\nTransaction Family: %s - %s'                           \
                            '\nTransaction Code: %s - %s'                             \
                            '\nTransaction Category: %s - %s'                         \
                            '\nStructured Communication Type: %s - %s'                \
                            '\nCommunication: %s'                                     \
                            '\nValuta Date: %s'                                       \
                            '\nEntry Date: %s \n')                                    \
                            %(line['counterparty_name'], line['counterparty_number'],
                              line['trans_type'], line['trans_type_desc'],
                              line['trans_family'], line['trans_family_desc'],
                              line['trans_code'], line['trans_code_desc'],
                              line['trans_category'], line['trans_category_desc'],
                              line['struct_comm_type'], line['struct_comm_type_desc'],
                              line['communication'],
                              line['val_date'],
                              line['entry_date'])
    
                        if line['type'] == 'globalisation':
                            id = coda_st_line_obj.create(cr, uid, {
                                   'sequence': line['sequence'],
                                   'ref': line['ref'],                                                  
                                   'name': line['name'],
                                   'type' : 'globalisation',
                                   'date': line['entry_date'],
                                   'globalisation_level': line['globalisation_level'],  
                                   'globalisation_amount': line['globalisation_amount'],                                                      
                                   'partner_id': line['partner_id'] or 0,
                                   'account_id': line['account_id'],
                                   'statement_id': coda_st_id,
                                   'note': line_note,
                                   })
                        else:
                            if line['account_id'] != transfer_acc:                               
                                if line['partner_id']:
                                    partner = self.pool.get('res.partner').browse(cr, uid, line['partner_id'])
                                    if line['amount'] < 0 :
                                        line['account_id'] = partner.property_account_payable.id or def_pay_acc
                                        line['type'] = 'supplier'
                                    else:
                                        line['account_id'] = partner.property_account_receivable.id or def_rec_acc
                                        line['type'] = 'customer'
                                else:
                                    line['account_id'] = awaiting_acc
                            id = coda_st_line_obj.create(cr, uid, {
                                   'sequence': line['sequence'],
                                   'ref': line['ref'],                                                   
                                   'name': line['name'],
                                   'type' : line['type'],
                                   'date': line['entry_date'],
                                   'amount': line['amount'],
                                   'partner_id': line['partner_id'] or 0,
                                   'account_id': line['account_id'],
                                   'statement_id': coda_st_id,
                                   'note': line_note,
                                   'invoice_id': line.get('invoice_id',False),
                                   })

                res = coda_st_obj.action_generate(cr, uid, [coda_st_id], context=context) # generate bank statement
                bk_st_ids.append(res[0])
                cr.commit()

                bk_st_journal = journal_obj.browse(cr, uid, statement['journal_id'], context).name
                coda_note = coda_note +                                                 \
                    _('\n\nBank Journal: %s'                                            \
                    '\nCODA Sequence Number: %s'                                        \
                    '\nPaper Statement Sequence Number: %s'                             \
                    '\nAccount Number: %s'                                              \
                    '\nAccount Holder Name: %s'                                         \
                    '\nDate: %s, Starting Balance:  %.2f, Ending Balance: %.2f'         \
                    '%s')                                                               \
                    %(bk_st_journal,
                      statement['coda_seq_number'],
                      statement['paper_seq_number'],
                      statement['acc_number'],
                      statement['acc_holder'],
                      statement['date'], float(statement['balance_start']), float(statement['balance_end_real']),
                      statement['coda_parsing_note'])
    
                coda_st_ids.append(coda_st_id)
    
            except osv.except_osv, e:
                cr.rollback()
                nb_err += 1
                err_log = err_log + _('\n\nApplication Error : ') + str(e)
            except Exception, e:
                cr.rollback()
                nb_err += 1
                err_log = err_log + _('\n\nSystem Error : ') +str(e)          
            except :
                cr.rollback()
                nb_err += 1
                err_log = err_log + _('\n\nUnknown Error')
    
        coda_note_header = _('CODA File is Imported  :')
        coda_note_footer = _('\n\nNumber of statements : ') + str(len(coda_st_ids))
        err_log = err_log + _('\nNumber of errors : ') + str(nb_err) + '\n'
        if not nb_err:
            note = coda_note_header + coda_note + coda_note_footer
            coda_obj.write(cr, uid,[coda_id],{'note': note })
        else:
            note = err_log
        self.write(cr, uid, ids, {'note': note}, context=context)
        context.update({ 'bk_st_ids': bk_st_ids})
        model_data_ids = mod_obj.search(cr, uid, [('model', '=', 'ir.ui.view'), ('name', '=', 'account_coda_import_result_view')], context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']

            
        return {
            'name': _('Import CODA File result'),
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.coda.import',
            'view_id': False,
            'target': 'new',
            'views': [(resource_id, 'form')],
            'context': context,
            'type': 'ir.actions.act_window',
        }

    def action_open_coda_statements(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return {
            'domain': "[('coda_id','=',%d)]" %(context.get('coda_id', False)),
            'name': _('CODA Bank Statements'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'coda.bank.statement',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    def action_open_bank_statements(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return {
            'domain':"[('id','in',%s)]" %(context.get('bk_st_ids', False)),
            'name': _('Bank Statements'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.bank.statement',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
account_coda_import()

def str2date(date_str):
            return time.strftime('%Y-%m-%d', time.strptime(date_str,'%d%m%y'))

def str2float(str):
    try:
        return float(str)
    except:
        return 0.0

def list2str(lst):
            return str(lst).strip('[]').replace(',', '').replace('\'', '')

def list2float(lst):
            try:
                return str2float((lambda s : s[:-3] + '.' + s[-3:])(lst))
            except:
                return 0.0


