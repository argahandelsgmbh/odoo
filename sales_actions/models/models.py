# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_ready = fields.Boolean(compute='compute_is_ready', store=True)
    is_po_draft = fields.Boolean(compute='compute_is_po_draft', store=True)
    is_do_done = fields.Boolean(compute='compute_is_ready', store=True)

    @api.depends('name', 'write_date')
    def compute_is_po_draft(self):
        for r in self:
            po = self.env['purchase.order'].search(['|',('sale_order', '=', r.id),('origin', '=', r.name)])
            if po:
                res = all(rec.state != 'done' for rec in po)
                r.is_po_draft = res
            else:
                r.is_po_draft = False

    @api.depends('picking_ids', 'picking_ids.state')
    def compute_is_ready(self):
        for r in self:
            if r.picking_ids:
                res = all(rec.state == 'assigned'for rec in r.picking_ids)
                done = all(rec.state == 'done'for rec in r.picking_ids)
                r.is_do_done = done
                r.is_ready = res
            else:
                r.is_do_done = False
                r.is_ready = False