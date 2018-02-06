# -*- coding: utf-8 -*-

import time
from openerp import netsvc

import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.addons.hr_nomina import payroll_tools
from openerp import models, fields, api
import logging
from docutils.nodes import line_block
from openerp.exceptions import ValidationError
import base64, time

def change_special_caracters(text):
    characters = {
        u'Á': u'A', u'á': u'a',
        u'É': u'E', u'é': u'e',
        u'Í': u'I', u'í': u'i',
        u'Ó': u'O', u'ó': u'o',
        u'Ú': u'U', u'ú': u'u',
        u'Ü': u'U', u'ü': u'u',
        u'Ñ': u'N', u'ñ': 'n',
    }
    for ori, new in characters.iteritems():
        text = text.replace(ori, new)
    return text


class voucher_cash_wizard(osv.osv_memory):
    """account.voucher cash"""
    _name = "voucher.cash.wizard"
    _description = "Genera Cash Management de vouchers seleccionados"

    voucher_ids=fields.Many2many('account.voucher', required=True, default=lambda self: self._context.get('active_ids', []))
    date=fields.Date('Fecha', default=time.strftime('%Y-%m-%d'),required=True)
    bank_account_id=fields.Many2one('res.partner.bank', 'Cuenta', required=True ,domain=[('partner_id', '=', 1)])
   
    
    @api.multi
    def generar_cash_pichincha(self):
        file, filename = self.pichincha()
        return self.env['base.file.report'].show(file, filename)
    
    @api.multi
    def generar_cash_produbanco(self):
        file, filename = self.produbanco()
        return self.env['base.file.report'].show(file, filename)
    
    
    def pichincha(self, CODIF='Windows-1252', NEWLINE='\r\n'):
        string = ''
        DATE = datetime.strptime(self.date, '%Y-%m-%d').strftime('%y%m%d')

        for sequence, transfer in enumerate(self.voucher_ids, 1):
            
            TIPO_CUENTA = {'AHO': 'AHO', 'COR': 'CTE'}
            TIPO_IDENT = {'c': 'C', 'r': 'R', 'p': 'P'}
            
            if transfer.partner_id.bank_ids:
                string += 'PA\t%s\t%s\t%s'%(self.bank_account_id.acc_number.replace('-', ''), sequence, '')
                string += '%s%s'%(transfer.partner_id.ident_num.upper().ljust(13, ' ')[:13],' ')
                string += 'USD%s%s%s'%(' ',str(int(round(transfer.amount, 2) * 100)).rjust(14, '0'),' ')
                string += 'CTA%s%s%s'%(' ',transfer.partner_id.bank_ids.bank_bic.replace('-', '').rjust(4, '0'),' ')
                string += '%s%s%s'%(' ',TIPO_CUENTA[transfer.partner_id.bank_ids.acc_type],' ')      
                string += '%s%s%s%s%s%s%s%s'%(transfer.partner_id.bank_ids.acc_number.replace('-', '').rjust(11, '0'),' ',TIPO_IDENT[transfer.partner_id.ident_type],' ',transfer.partner_id.ident_num.upper().ljust(13, ' ')[:13],' ',transfer.partner_id.name.upper().ljust(40, ' ')[:40],' ')
                ##string += '\t%s\t|%s'%('\t',transfer.partner_id.email or '')
                string += NEWLINE
            else:
                continue
        
        
        file = base64.encodestring(string.encode(CODIF))
        filename = time.strftime('CASH'+self.bank_account_id.bank_bic+'%Y%m%d.txt')
        return file, filename
    

    def produbanco(self, CODIF='Windows-1252', NEWLINE='\r\n'):
        string = ''

        DATE = datetime.strptime(self.date, '%Y-%m-%d').strftime('%y%m%d')

        for sequence, transfer in enumerate(self.voucher_ids, 1):
            TIPO_CUENTA = {'AHO': 'AHO', 'COR': 'CTE'}
            TIPO_IDENT = {'c': 'C', 'r': 'R', 'p': 'P'}

            if transfer.partner_id.bank_ids:
                string += 'PA\t%s\t%s\t%s'%(self.bank_account_id.acc_number.replace('-', ''), sequence, '')
                string += '%s%s'%(transfer.partner_id.ident_num.upper().ljust(13, ' ')[:13],' ')
                string += 'USD%s%s%s'%(' ',str(int(round(transfer.amount, 2) * 100)).rjust(14, '0'),' ')
                string += 'CTA%s%s%s'%(' ',transfer.partner_id.bank_ids.bank_bic.replace('-', '').rjust(4, '0'),' ')
                string += '%s%s%s'%(' ',TIPO_CUENTA[transfer.partner_id.bank_ids.acc_type],' ')      
                string += '%s%s%s%s%s%s%s'%(transfer.partner_id.bank_ids.acc_number.replace('-', '').rjust(11, '0'),' ',TIPO_IDENT[transfer.partner_id.ident_type],' ',transfer.partner_id.ident_num.upper().ljust(13, ' ')[:13],' ',transfer.partner_id.name.upper().ljust(40, ' ')[:40])
                string += '|%s'%(transfer.partner_id.email or '')
                string += NEWLINE
            else:
                continue
            
            
        file = base64.encodestring(string.encode(CODIF))
        filename = time.strftime('CASH'+self.bank_account_id.bank_bic+'%Y%m%d.txt')
        return file, filename
