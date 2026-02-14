# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    delivery_date = fields.Date(string='Delivery Date', copy=False)

    def write(self, vals):
        res = super(StockPickingInh, self.with_context(from_picking=True)).write(vals)
        if vals.get('delivery_date'):
            if 'from_picking' not in self.env.context:
                project_task = self.env['project.task'].search([("sale_line_id.order_id", '=', self.sale_id.id)], limit=1)
                if project_task:
                    project_task.with_context(from_picking=True).update({
                        'delivery_date': self.delivery_date,
                        'date_deadline': self.delivery_date,
                    })

                self.sale_id.with_context(from_picking=True).update({
                    'commitment_date': self.delivery_date
                })
        return res
