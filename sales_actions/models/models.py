# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_ready = fields.Boolean(compute='compute_is_ready')

    @api.depends('picking_ids')
    def compute_is_ready(self):
        for r in self:
            print(all(rec.state == 'assigned'for rec in r.picking_ids))
            res = all(rec.state == 'assigned'for rec in r.picking_ids)
            r.is_ready = res
