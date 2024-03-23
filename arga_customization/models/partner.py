# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = _inherit
    
    partner_invoice_id = fields.Many2one('res.partner', 'Invoicing Address', check_company=True)

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('customer.number')
        return super(ResPartner, self).create(vals)
