# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError

class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    invoice_total = fields.Float('Order Total')
    remaining_amt = fields.Float('Open Amount')
    delivery_date = fields.Date(string='Delivery Date', copy=False)

    def write(self, vals):
        res = super(StockPickingInh, self).write(vals)
        if vals.get('delivery_date'):
            sale_order = self.env['sale.order'].search([("name", '=', self.origin)], limit=1)
            if sale_order and sale_order.delivery_date != self.delivery_date:
                sale_order.delivery_date = self.delivery_date
        return res