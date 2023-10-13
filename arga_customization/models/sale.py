# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError

class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    delivery_date = fields.Date(string='Delivery Date', copy=False)
    total_invoice_paid = fields.Float(compute='get_invoice_amount')
    total_invoice_amount = fields.Float(compute='get_invoice_amount')
    total_payment = fields.Float(compute='get_invoice_amount')
    total_open_amount = fields.Float(readonly=True)
    total_qty = fields.Float('Total Lines')
    istikabl_qty = fields.Float('Istikabal')
    bellona_qty = fields.Float('Bellona')
    po_qty = fields.Float('PO')
    do_qty = fields.Float('DO')
    received_qty = fields.Float('Received')
    remaining_qty = fields.Float('Not Available Qty')
    receipt_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'), ('cancel', 'Cancelled'), ('', '    ')
    ], string='Receipt Status', readonly=True, copy=False)
    do_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'), ('cancel', 'Cancelled')
    ], string='DO Status', readonly=True, copy=False)
    po_state = fields.Selection([
        ('draft', 'Draft RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'), ('', '    ')
    ], 'PO Status', readonly=True)

    purchase_count = fields.Integer(string='Purchase Order Count', compute='get_invoice_amount')

    is_ready = fields.Boolean()
    is_po_draft = fields.Boolean()
    is_do_done = fields.Boolean()




    def open_related_po(self):
        po_id = self.env['purchase.order'].search([('origin', '=', self.name)])
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('id', 'in', po_id.ids)]
        return action

    def get_invoice_amount(self):
        for r in self:
            r.is_po_draft = False
            r.is_do_done = False
            r.is_ready = False
            po = self.env['purchase.order'].search(['|', ('sale_order', '=', r.id), ('origin', '=', r.name)])
            if po:
                res = all(rec.state != 'done' for rec in po)
                r.is_po_draft = res

            if r.picking_ids:
                res = all(rec.state == 'assigned' for rec in r.picking_ids)
                done = all(rec.state == 'done' for rec in r.picking_ids)
                r.is_do_done = done
                r.is_ready = res

        for rec in self:
            rec.purchase_count = self.env['purchase.order'].search_count([('origin', '=', rec.name)])
            invoices = self.env['account.move'].search([('invoice_origin', '=', rec.name)]).filtered(lambda i: i.invoice_origin != False)
            payments = self.env['account.payment'].search([('ref', '=', rec.name)]).filtered(lambda i: i.ref != False)
            rec.total_payment=inv_payment=sum(payments.mapped('amount'))
            inv_amount = sum(invoices.mapped('amount_total'))
            paid_amount = sum(invoices.mapped('amount_total')) - sum(invoices.mapped('amount_residual'))
            rec.total_invoice_amount = inv_amount
            rec.total_invoice_paid = paid_amount+inv_payment
            rec.total_open_amount = (rec.amount_total- paid_amount) -inv_payment if invoices else rec.amount_total-inv_payment
            purchase_order = self.env['purchase.order'].search([("origin", "=", rec.name)])
            receipt = self.env['purchase.order'].search([("origin", "=", rec.name)], limit=1)
            po_qty = 0
            istikabl_qty = 0
            bellona_qty = 0
            received_qty = 0
            for po in purchase_order:
                po_qty = po_qty + po.total_lines
                istikabl_qty = istikabl_qty + po.total_istikbal_lines
                bellona_qty = bellona_qty + po.total_bellona_lines
                received_qty = received_qty + po.total_received
            rec.po_qty = po_qty
            rec.istikabl_qty = istikabl_qty
            rec.bellona_qty = bellona_qty
            rec.received_qty = received_qty
            rec.total_qty = len(rec.order_line.filtered(lambda i: i.product_id.type == 'product').mapped('id'))
            rec.do_qty = len(self.env['stock.move.line'].search([("origin", "=", rec.name), ("state", "=", 'done')]))

            if receipt:
                rec.receipt_status = receipt.receipt_status
                rec.po_state = receipt.state
            else:
                rec.receipt_status = ''
                rec.po_state = ''

            rec.do_status = 'draft'
            if rec.picking_ids:
                if all(line.state == 'waiting' for line in rec.picking_ids):
                    rec.do_status = 'waiting'
                if all(line.state == 'confirmed' for line in rec.picking_ids):
                    rec.do_status = 'confirmed'
                if all(line.state == 'assigned' for line in rec.picking_ids):
                    rec.do_status = 'assigned'
                if all(line.state == 'done' for line in rec.picking_ids):
                    rec.do_status = 'done'
                if all(line.state == 'cancel' for line in rec.picking_ids):
                    rec.do_status = 'cancel'

    def write(self, vals):
        res = super(SaleOrderInh, self).write(vals)
        if vals.get('delivery_date'):
            project_task = self.env['project.task'].search([("sale_line_id.order_id", '=', self.id)], limit=1)
            project_task.delivery_date = self.delivery_date
            project_task.planned_date_begin = self.delivery_date
            project_task.date_deadline = self.delivery_date
            self.action_update_appoint()
            for k in self.picking_ids:
                if k.state not in ['done', 'cancel']:
                    k.delivery_date = self.delivery_date
        return res



class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    number = fields.Integer(string="Sr#", compute='_compute_get_number', default=1)
    available = fields.Float('Available Qty', related="product_id.qty_available")
    remaining_qty = fields.Float('Not Available')
    qty_in = fields.Float()
    qty_out = fields.Float()
    free_qty = fields.Float()
    total_price = fields.Float("B.Disc")



    @api.depends('order_id')
    def _compute_get_number(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                line.total_price = line.product_uom_qty * line.price_unit
                if line.product_id:
                    line.number = number
                    number += 1
                else:
                    line.number = number