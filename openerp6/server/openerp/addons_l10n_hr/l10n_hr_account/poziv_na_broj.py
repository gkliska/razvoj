# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Author: Goran Kliska
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#    Contributions: 
#    Documentation: http://www.fina.hr/Default.aspx?sec=1266       
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

import logging

def mod11ini(value):
    '''
    Compute mod11ini
    '''    
    length = len(value) 
    sum = 0
    for i in xrange(0, length):
        sum += int(value[length - i - 1]) * (i + 2)
    res = sum % 11
    if res > 1:
        res =  11 - res
    else:
        res =0
    return str(res)

def iso7064(value):
    """
    Compute ISO 7064, Mod 11,10
    """
    t = 10
    for i in value:
        c = int(i)
        t = (2 * ((t + c) % 10 or 10)) % 11
    return str((11 - t) % 10)

def mod11p7(value):
     length = len(value) 
     ### if 1.st digit differs from three - ERROR
     #if not return_check_digit and int(value[0]) != 3:
     #    return False
     sum = 0
     for i in xrange(0, length):
         sum += int(value[length - i - 1]) * ((i % 6) + 2)
     res = sum % 11
     if res == 0:
         return '5' 
     elif res == 1:
         return '0' 
     else:
         return str( 11 - res )

def mod10zb(value):
    l = len(value) 
    res = 0
    for i in xrange(0, l):
        res += int(value[l - i - 1]) * (i % 2 + 1)
    return str( res % 10 )

def mod10(value):
    l = len(value) 
    res = 0
    for i in xrange(0, l):
        num = int(value[l - i - 1]) * (((i + 1) % 2) + 1)
        res += (num / 10 + num % 10)
    res = res % 10
    if res == 0:
        return '0'
    else:
        return str(10 - res)

def mod11(value):
    l = len(value) 
    res = 0
    for i in xrange(0, l):
        res += int(value[l - i - 1]) * (i % 6 + 2)
    res = res % 11
    if res > 1:
        return str(11-res)
    else:
        return '0'
"""
# Test
mod11p7('3456789012') # res = '2'
mod10zb('223344556') #res='8'
mod7064('234000') #res='9'
mod11ini('33444555666') #res=9
mod10('54370395') #res=7
mod11('54370395') #res=8
"""

def reference_number( model='', P1='', P2='', P3='', P4=''):

    if not model:
        model='' # or '99'?  
    if model == "01":
        res = '-'.join((P1, P2, P3 + mod11ini(P1 + P2 + P3)))
    elif model == "02":
        res = '-'.join((P1, P2 + mod11ini(P2), P3 + mod11ini(P3)))
    elif model == "03":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + mod11ini(P3)))
    elif model == "04":
        res = '-'.join((P1 + mod11ini(P1), P2, P3 + mod11ini(P3)))
    elif model == "05":
        res = '-'.join((P1 + mod11ini(P1), P2, P3))
    elif model == "06":
        res = '-'.join((P1, P2, P3 + mod11ini(P2 + P3)))
    elif model == "07":
        res = '-'.join((P1, P2 + mod11ini(P2), P3))
    elif model == "08":
        res = '-'.join((P1, P2 + mod11ini(P1+P2), P3 + mod11ini(P3)))
    elif model == "09":
        res = '-'.join((P1, P2 + mod11ini(P1 + P2), P3))
    elif model == "10":
        res = '-'.join((P1 + mod11ini(P1), P2, P3 + mod11ini(P2 + P3)))
    elif model == "11":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3))
    elif model == "13":
        res = '-'.join((P1 + mod11p7(P1), P2, P3))
    elif model == "14":
        res = '-'.join((P1 + mod10zb(P1), P2, P3))
    elif model == "15":
        res = '-'.join((P1 + mod10(P1), P2 + mod10(P2)))
    elif model == "16":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3))
    elif model == "17":
        res = '-'.join((P1 + iso7064(P1), P2, P3))
    elif model == "18":
        res = '-'.join((P1 + mod11p7(P1), P2, P3))
    elif model == "21":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3))
    elif model == "23":
        res = '-'.join((P1 + mod11ini(P1), P2, P3, P4))
    elif model == "24":
        res = '-'.join((P1 + mod11ini(P1), P2, P3, P4))
    elif model == "26":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + mod11ini(P3), P4))
    elif model == "27":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2)))
    elif model == "28":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + mod11ini(P3), P4))
    elif model == "29":
        res = '-'.join((P1 + self.mod11ini(P1), P2 + self.mod11ini(P2), P3 + self.mod11ini(P3)))
    elif model == "31":
        res = '-'.join((P1 + iso7064(P1), P2, P3, P4))
    elif model == "33":
        res = '-'.join((P1 + iso7064(P1), P2 + iso7064(P2), P3))
    elif model == "34":
        res = '-'.join((P1 + iso7064(P1), P2 + iso7064(P2), P3 + iso7064(P3)))
    elif model == "40":
        res = '-'.join((P1 + mod10(P1), P2, P3))
    elif model == "43":
        res = '-'.join((P1, P2 + mod11ini(P2), P3, P4))
    elif model == "55":
        res = '-'.join((P1 + mod11ini(P1), P2, P3))
    elif model == "62":
        res = '-'.join((P1 + mod11ini(P1), P2 + iso7064(P2), P3 + mod11ini(P3), P4))
    elif model == "63":
        res = '-'.join((P1 + mod11ini(P1), P2 + iso7064(P2), P3 + mod11ini(P3)))
    elif model == "64":
        res = '-'.join((P1 + mod11ini(P1), P2 + iso7064(P2), P3, P4))
    elif model == "65":
        res = '-'.join((P1 + mod11ini(P1), P2 + mod11ini(P2), P3 + iso7064(P3), P4))
    elif model == "66":
        res = '-'.join((P1, P2[:7] + mod11ini(P2[:7]) + P2[7:], P3))
    elif model == "83":
        res = '-'.join(((P1 + mod11ini(P1),  P2, P3)))
    elif model == "84":
        if len(P2) == 4:
            res = '-'.join((P1 + mod11ini(P1),  P2,  P3))
        else:
            res = '-'.join(((P1 + mod11ini(P1), P2)))
    else: # model in ('','00',"99")
        res= (P1 + '-' + P2 + '-' + P3 + '-' + P4 ) 
    
    res.strip('-')
    res = res.strip('-').replace('---', '-').replace('--', '-')
 
    return res

def validate_lenghts(model, value):













class account_ref_number():
    def mod11ini_check(self, ref_number, in_control_number = None, in_length_to_check = None, return_check_digit = False):
        calc_control_num = -1
        length_to_check = in_length_to_check or len(ref_number) - 1 
        sum = 0
        for i in xrange(0, length_to_check):
            sum += int(ref_number[length_to_check - i - 1]) * (i + 2)
        res = sum % 11
        if res == 0 or res == 1:
            calc_control_num = 0
        else:
            calc_control_num = 11 - res
        if return_check_digit:
            return str(calc_control_num)
        else:
            control_num = (in_control_number and int(in_control_number)) or int(ref_number[length_to_check]) 
            return (calc_control_num == control_num)

    def mod11p7_check(self, ref_number, in_control_number = None, in_length_to_check = None, return_check_digit = False):
        calc_control_num = -1
        length_to_check = in_length_to_check or len(ref_number) - 1 
        ### if 1.st digit differs from three - ERROR
        if not return_check_digit and int(ref_number[0]) != 3:
            return False
        sum = 0
        for i in xrange(0, length_to_check):
            sum += int(ref_number[length_to_check - i - 1]) * ((i % 6) + 2)
        res = sum % 11
        if res == 0:
            calc_control_num = 5
        elif res == 1:
            calc_control_num = 0
        else:
            calc_control_num = 11 - res
        if return_check_digit:
            return str(calc_control_num)
        else:
            control_num = (in_control_number and int(in_control_number)) or int(ref_number[length_to_check]) 
            return (calc_control_num == control_num)

    def mod10zb_check(self, ref_number, in_control_number = None, in_length_to_check = None, return_check_digit = False):
        calc_control_num = -1
        length_to_check = in_length_to_check or len(ref_number) - 1 
        sum = 0
        for i in xrange(0, length_to_check):
            sum += int(ref_number[length_to_check - i - 1]) * (i % 2 + 1)
        calc_control_num = sum % 10
        if return_check_digit:
            return str(calc_control_num)
        else:
            control_num = (in_control_number and int(in_control_number)) or int(ref_number[length_to_check]) 
            return (calc_control_num == control_num)

    def iso7064_1983_check(self, ref_number, in_control_number = None, in_length_to_check = None, return_check_digit = False):
        calc_control_num = -1
        length_to_check = in_length_to_check or len(ref_number) - 1 
        sum = 0
        res = 11
        for i in xrange(0, length_to_check):
            num = int(ref_number[i])
            if num == 0:
                num = 10
            res = ((res % 11) + num) % 10
            if res == 0:
                res = 10
            res = res * 2
        result = res % 11
        if result == 0:
            calc_control_num = 1
        elif result == 1:
            calc_control_num = 0
        else:
            calc_control_num = 11 - result
        if return_check_digit:
            return str(calc_control_num)
        else:
            control_num = (in_control_number and int(in_control_number)) or int(ref_number[length_to_check]) 
            return (calc_control_num == control_num)

    def mod10_check(self, ref_number, in_control_number = None, in_length_to_check = None, return_check_digit = False):
        calc_control_num = -1
        length_to_check = in_length_to_check or len(ref_number) - 1 
        sum = 0
        for i in xrange(0, length_to_check):
            num = int(ref_number[length_to_check - i - 1]) * (((i + 1) % 2) + 1)
            sum += (num / 10 + num % 10)
        res = sum % 10
        if res == 0:
            calc_control_num = 0
        else:
            calc_control_num = 10 - res
        if return_check_digit:
            return str(calc_control_num)
        else:
            control_num = (in_control_number and int(in_control_number)) or int(ref_number[length_to_check]) 
            return (calc_control_num == control_num)

    def mod11_check(self, ref_number, in_control_number = None, in_length_to_check = None, return_check_digit = False):
        calc_control_num = -1
        length_to_check = in_length_to_check or len(ref_number) - 1 
        sum = 0
        for i in xrange(0, length_to_check):
            sum += int(ref_number[length_to_check - i - 1]) * (i % 6 + 2)
        res = sum % 11
        if res == 0:
            return False
        elif res == 1:
            calc_control_num = 0
        else:
            calc_control_num = 11 - res
        if return_check_digit:
            return str(calc_control_num)
        else:
            control_num = (in_control_number and int(in_control_number)) or int(ref_number[length_to_check]) 
            return (calc_control_num == control_num)

    def control_ref_number(self, model, ref_number):
        logger = logging.getLogger('server')

        if len(ref_number) > 22 :
            logger.error('Input ref. number has more than 22 characters...')
            return False

        if len(model) != 2 :
            logger.error('Model must have 2 characters...')
            return False

        args = ref_number.split('-')
        if model == "01":
            return self.mod11ini_check("".join(args))
        elif model == "02":
            return (self.mod11ini_check(args[1]) and self.mod11ini_check(args[2])) 
        elif model == "03":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]) and self.mod11ini_check(args[2])) 
        elif model == "04":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[2])) 
        elif model == "05":
            return (self.mod11ini_check(args[0])) 
        elif model == "06":
            return (self.mod11ini_check("".join(args[1:]))) 
        elif model == "07":
            return (self.mod11ini_check(args[1])) 
        elif model == "08":
            return (self.mod11ini_check("".join(args[:2])) and self.mod11ini_check(args[2])) 
        elif model == "09":
            return (self.mod11ini_check("".join(args[:2]))) 
        elif model == "10":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check("".join(args[1:]))) 
        elif model == "11":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]))
        elif model == "13":
            return (self.mod11p7_check(args[0]))
        elif model == "14":
            return (self.mod10zb_check(args[0]))
        elif model == "15":
            return (self.mod10_check(args[0]) and self.mod10_check(args[1]))
        elif model == "16":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]))
        elif model == "17":
            return (self.iso7064_1983_check(args[0]))
        elif model == "18":
            return (self.mod11p7_check(args[0]))
        elif model == "21":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]))
        elif model == "23":
            return (self.mod11ini_check(args[0]))
        elif model == "24":
            return (self.mod11ini_check(args[0]))
        elif model == "26":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]) and self.mod11ini_check(args[2]))
        elif model == "27":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]))
        elif model == "28":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]) and self.mod11ini_check(args[2]))
        elif model == "29":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]) and self.mod11ini_check(args[2]))
        elif model == "31":
            return (self.iso7064_1983_check(args[0]))
        elif model == "33":
            return (self.iso7064_1983_check(args[0]) and self.iso7064_1983_check(args[1]))
        elif model == "34":
            return (self.iso7064_1983_check(args[0]) and self.iso7064_1983_check(args[1]) and self.iso7064_1983_check(args[2]))
        elif model == "40":
            ### If 3 consecutive list elements are the same, reference number is wrong
            list_1 = args[0]
            for i in range(0, len(args[0]) - 3):
                val = int(args[0][i]) & int(args[0][i + 1]) & int(args[0][i + 2])
                if val == int(args[0][i]) and val == int(args[0][i + 1]) and val == int(args[0][i + 2]):
                    return False  

            return (self.mod10_check(args[0], args[0][-2], len(args[0]) - 2) and self.mod11_check(args[0], args[0][-1], len(args[0]) - 2))
        elif model == "43":
            return self.mod11ini_check(args[1])
        elif model == "55":
            return self.mod11ini_check(args[0])
        elif model == "62":
            return (self.mod11ini_check(args[0]) and self.iso7064_1983_check(args[1]) and self.mod11ini_check(args[2]))
        elif model == "63":
            return (self.mod11ini_check(args[0]) and self.iso7064_1983_check(args[1]) and self.mod11ini_check(args[2]))
        elif model == "64":
            return (self.mod11ini_check(args[0]) and self.iso7064_1983_check(args[1]))
        elif model == "65":
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1]) and self.iso7064_1983_check(args[2]))
        elif model == "66":
            if args[1][0] != '0':
                return False 
            return (self.mod11ini_check(args[0]) and self.mod11ini_check(args[1], in_control_number = args[1][7], in_length_to_check = 7))
        elif model == "83":
            return (self.mod11ini_check(args[0]))
        elif model == "84":
            return (self.mod11ini_check(args[0]))
        elif model == "99":
            return True


    def generate_and_clean_ref_number(self, model, P1='', P2='', P3='', P4=''):
        res = generate_ref_number( model, P1, P2, P3, P4)
        res = res.replace('---', '-')
        res = res.replace('--' , '-')
        if res[0] ==  '-':
            res = res[1:]
        return res
    

        
        
    def generate_ref_number(self, model='', P1='', P2='', P3='', P4=''):
        if not model:
            model=''  

        if model == "":
            return (P1 + '-' + 
                    P2 + '-' + 
                    P3 + '-' + 
                    P4  ) 

        if model == "00":
            return (P1 + '-' + 
                    P2 + '-' + 
                    P3 + '-' + 
                    P4  ) 

        if model == "01":
            ref_number = P1 + P2 + P3
            return (P1 + '-' + 
                    P2 + '-' + 
                    P3 + self.mod11ini_check(ref_number, in_length_to_check=len(ref_number), return_check_digit = True)) 
        elif model == "02":
            return (P1 + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' + 
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True)) 
        elif model == "03":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' + 
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True)) 
        elif model == "04":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True)) 
        elif model == "05":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3) 
        elif model == "06":
            ref_number = P2 + P3
            return (P1 + '-' + 
                    P2 + '-' + 
                    P3 + self.mod11ini_check(ref_number, in_length_to_check=len(ref_number), return_check_digit = True)) 
        elif model == "07":
            return (P1 + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' + 
                    P3) 
        elif model == "08":
            ref_number = P1 + P2 
            return (P1 + '-' + 
                    P2 + self.mod11ini_check(ref_number, in_length_to_check=len(ref_number), return_check_digit = True) + '-' + 
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True)) 
        elif model == "09":
            ref_number = P1 + P2
            return (P1 + '-' + 
                    P2 + self.mod11ini_check(ref_number, in_length_to_check=len(ref_number), return_check_digit = True) + '-' + 
                    P3) 
        elif model == "10":
            ref_number = P2 + P3
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3 + self.mod11ini_check(ref_number, in_length_to_check=len(ref_number), return_check_digit = True)) 
        elif model == "11":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' + 
                    P3) 
        elif model == "13":
            return (P1 + self.mod11p7_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3) 
        elif model == "14":
            return (P1 + self.mod10zb_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3) 
        elif model == "15":
            return (P1 + self.mod10_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod10_check(P2, in_length_to_check=len(P2), return_check_digit = True)) 
        elif model == "16":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' + 
                    P3) 
        elif model == "17":
            return (P1 + self.iso7064_1983_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3) 
        elif model == "18":
            return (P1 + self.mod11p7_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3) 
        elif model == "21":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' + 
                    P3) 
        elif model == "23":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3 + '-' +
                    P4) 
        elif model == "24":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' + 
                    P3 + '-' +
                    P4) 
        elif model == "26":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True) + '-' +
                    P4) 
        elif model == "27":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True))
        elif model == "28":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True) + '-' +
                    P4) 
        elif model == "29":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True)) 
        elif model == "31":
            return (P1 + self.iso7064_1983_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' +
                    P3 + '-' +
                    P4) 
        elif model == "33":
            return (P1 + self.iso7064_1983_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.iso7064_1983_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3) 
        elif model == "34":
            return (P1 + self.iso7064_1983_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.iso7064_1983_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + self.iso7064_1983_check(P3, in_length_to_check=len(P3), return_check_digit = True)) 
        elif model == "40":
            return (P1 + self.mod10_check(P1, in_length_to_check=len(P1), return_check_digit = True) + self.mod11_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' +
                    P3) 
        elif model == "43":
            return (P1 + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + '-' +
                    P4) 
        elif model == "55":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' +
                    P3) 
        elif model == "62":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.iso7064_1983_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True) + '-' +
                    P4) 
        elif model == "63":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.iso7064_1983_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + self.mod11ini_check(P3, in_length_to_check=len(P3), return_check_digit = True)) 
        elif model == "64":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.iso7064_1983_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + '-' +
                    P4) 
        elif model == "65":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + self.mod11ini_check(P2, in_length_to_check=len(P2), return_check_digit = True) + '-' +
                    P3 + self.iso7064_1983_check(P3, in_length_to_check=len(P3), return_check_digit = True) + '-' +
                    P4) 
        elif model == "66":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2[:7] + self.mod11ini_check(P2, in_length_to_check=7, return_check_digit = True) + P2[7:] + '-' +
                    P3) 
        elif model == "83":
            return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                    P2 + '-' +
                    P3) 
        elif model == "84":
            if len(P2) == 4:
                return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                        P2 + '-' +
                        P3) 
            else:
                return (P1 + self.mod11ini_check(P1, in_length_to_check=len(P1), return_check_digit = True) + '-' + 
                        P2) 
        elif model == "99":
            retval = P1
            if len(P2) != 0:
                retval += '-' + P2
            if len(P3) != 0:
                retval += '-' + P3
            if len(P4) != 0:
                retval += '-' + P4
            return retval

    def test_functionality(self, model, P1 = '', P2 = '', P3 = '', P4 = ''):
        ref_num = self.generate_ref_number(model, P1, P2, P3, P4)
        chk = self.control_ref_number(model, ref_num) and 'True' or 'False'
        self.logger.info('Generating ref. number...Model: "' + model + '" , ref_number = "' + ref_num + '", checked_out=' + chk)
        
    def __init__(self, arg1 = ''):
        if arg1 == 'test':
            self.logger = logging.getLogger('server')
            P1 = '1234'
            P2 = '5678'
            P3 = '1357'
            P4 = '2581'
            self.logger.info('Test fields for reference number: P1='+P1+',P2='+P2+',P3='+P3+',P4='+P4)
            self.test_functionality('01', P1, P2, P3, P4)
            self.test_functionality('02', P1, P2, P3, P4)
            self.test_functionality('03', P1, P2, P3, P4)
            self.test_functionality('04', P1, P2, P3, P4)
            self.test_functionality('05', P1, P2, P3, P4)
            self.test_functionality('06', P1, P2, P3, P4)
            self.test_functionality('07', P1, P2, P3, P4)
            self.test_functionality('08', P1, P2, P3, P4)
            self.test_functionality('09', P1, P2, P3, P4)
            self.test_functionality('10', P1, P2, P3, P4)
            self.test_functionality('11', P1, P2, P3, P4)
            self.test_functionality('13', '31234', P2, P3, P4)
            self.test_functionality('14', P1, P2, P3, P4)
            self.test_functionality('15', P1, P2, P3, P4)
            self.test_functionality('16', P1, P2, P3, P4)
            self.test_functionality('17', P1, P2, P3, P4)
            self.test_functionality('18', '31234', P2, P3, P4)
            self.test_functionality('21', P1, P2, P3, P4)
            self.test_functionality('23', P1, P2, P3, P4)
            self.test_functionality('24', P1, P2, P3, P4)
            self.test_functionality('26', P1, P2, P3, P4)
            self.test_functionality('27', P1, P2, P3, P4)
            self.test_functionality('28', P1, P2, P3, P4)
            self.test_functionality('29', P1, P2, P3, P4)
            self.test_functionality('31', P1, P2, P3, P4)
            self.test_functionality('33', P1, P2, P3, P4)
            self.test_functionality('34', P1, P2, P3, P4)
            self.test_functionality('40', P1, P2, P3, P4)
            self.test_functionality('43', P1, P2, P3, P4)
            self.test_functionality('55', P1, P2, P3, P4)
            self.test_functionality('62', P1, P2, P3, P4)
            self.test_functionality('63', P1, P2, P3, P4)
            self.test_functionality('64', P1, P2, P3, P4)
            self.test_functionality('65', P1, P2, P3, P4)
            self.test_functionality('66', '615', '09583728987', '7868')
            self.test_functionality('83', P1, P2, P3, P4)
            self.test_functionality('84', P1, P2, P3, P4)

account_ref_number()
###account_ref_number('test')