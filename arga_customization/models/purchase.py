# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    sale_order = fields.Many2one('sale.order')
    sale_repair_id = fields.Many2one('sale.order')
    receipt_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'), ('cancel', 'Cancelled')
    ], string='Receipt Status', readonly=True, copy=False)

    total_lines = fields.Integer(compute="_compute_sale_order")
    total_istikbal_lines = fields.Integer(string="Istikbal Lines")
    total_bellona_lines = fields.Integer(string="Bellona Lines")
    total_received = fields.Integer(string="Received")
    sale_ids = fields.Many2many('sale.order')



    def _compute_sale_order(self):
        sale_order_ids = self._get_sale_orders().ids
        self.sale_ids = sale_order_ids
        for rec in self:
            rec.receipt_status = 'draft'
            if rec.picking_ids:
                if all(line.state == 'waiting' for line in rec.picking_ids):
                    rec.receipt_status = 'waiting'
                if all(line.state == 'confirmed' for line in rec.picking_ids):
                    rec.receipt_status = 'confirmed'
                if all(line.state == 'assigned' for line in rec.picking_ids):
                    rec.receipt_status = 'assigned'
                if all(line.state == 'done' for line in rec.picking_ids):
                    rec.receipt_status = 'done'
                if all(line.state == 'cancel' for line in rec.picking_ids):
                    rec.receipt_status = 'cancel'

            moves = len(self.env['stock.move.line'].search(
                [("move_id.picking_id.purchase_id", '=', rec.id), ("state", '=', 'done')]))
            rec.total_lines = len(rec.order_line.mapped('id'))
            rec.total_istikbal_lines = len(rec.istikbal_shp_details.mapped('id'))
            rec.total_bellona_lines = len(rec.bellona_shipments.mapped('id'))
            rec.total_received = moves if moves else 0



class PurchaseOrderLineInh(models.Model):
    _inherit = 'purchase.order.line'

    number = fields.Integer(compute='_compute_get_number', store=True)

    @api.depends('sequence', 'order_id')
    def _compute_get_number(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                line.number = number
                number += 1
