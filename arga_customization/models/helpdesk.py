# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError


class HelpdeskTicketInh(models.Model):
    _inherit = 'helpdesk.ticket'

    def action_create_repair(self):
        location = self.env['stock.location'].search([('company_id', '=', self.company_id.id), ('usage', '=', 'internal')], limit=1)
        event = self.env['repair.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'description': self.description,
            'product_qty': self.sale_line_id.product_uom_qty ,
            'schedule_date': datetime.datetime.today().date(),
            'user_id': self.user_id.id or False,
            'ticket_id': self.id,
            'location_id': location.id,
            'sale_order_id': self.sale_line_id.order_id.id or False,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
        })