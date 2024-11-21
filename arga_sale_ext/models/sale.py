# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    stock_val = fields.Selection([('stock', '100% Stock')], string='100% Stock')
    commitment_date = fields.Datetime('Liefertermin Bestätigt', copy=False)
    # task_id = fields.Many2one("project.task", string="Task", readonly=True)

    def write(self, vals):
        res = super(SaleOrderInh, self.with_context(from_sale=True)).write(vals)
        if vals.get('commitment_date'):
            if 'from_sale' not in self.env.context:
                project_task = self.env['project.task'].search([("sale_line_id.order_id", '=', self.id)], limit=1)
                if project_task:
                    project_task.with_context(from_sale=True).update({
                        'delivery_date': self.commitment_date,
                        'date_deadline': self.commitment_date,
                    })

                for k in self.picking_ids:
                    if k.state not in ['done', 'cancel']:
                        k.with_context(from_sale=True).update({
                            'delivery_date' : self.commitment_date
                        })
        return res

# class SaleOrderLineInh(models.Model):
#     _inherit = 'sale.order.line'
#
#     number = fields.Integer(string="Sr#")
#
#     @api.depends('sequence', 'order_id')
#     def _compute_get_number(self):
#         for order in self.mapped('order_id'):
#             number = 1
#             for line in order.order_line:
#                 line.number = number
#                 number += 1
