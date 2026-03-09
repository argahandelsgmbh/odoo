# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    partner_invoice_id = fields.Many2one('res.partner', 'Invoicing Address', check_company=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('ref'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('customer.number')
        return super().create(vals_list)
