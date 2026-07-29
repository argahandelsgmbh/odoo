# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    stock_val = fields.Selection([('stock', '100% Stock')], string='100% Stock')
    commitment_date = fields.Datetime('Liefertermin Bestätigt', copy=False)
    batch_payment_id = fields.Many2one('account.batch.payment')

    sale_order_status = fields.Selection([
        ('waiting_purchase', 'Waiting for Purchase'),
        ('production', 'In Production'),
        ('partial_received', 'Partially Received'),
        ('ready_warehouse', 'Ready in Warehouse'),
        ('available_stock', 'Available from Stock'),
        ('delivery_planned', 'Delivery Planned'),
        ('delivered', 'Delivered'),
    ], string="Workflow Status", compute="_compute_sale_order_status", store=True)

    @api.depends(
        'state',
        'stock_val',
        'picking_ids.state',
        'picking_ids.picking_type_id.code',
        'picking_ids.move_ids.product_uom_qty',
        'picking_ids.move_ids.quantity',
        'order_line.qty_delivered','po_receipt_status'
    )
    def _compute_sale_order_status(self):
        PurchaseOrder = self.env['purchase.order']

        for order in self:
            order._compute_receipt_status()
            status = 'waiting_purchase'

            # Ignore quotations
            if order.state not in ['sale', 'done']:
                order.sale_order_status = False
                continue

            # Fully delivered
            if order.order_line and all(
                    line.qty_delivered >= line.product_uom_qty
                    for line in order.order_line
                    if not line.display_type
            ):
                order.sale_order_status = 'delivered'
                continue

            # Delivery planned
            outgoing = order.picking_ids.filtered(
                lambda p: p.picking_type_id.code == 'outgoing'
                          and p.state not in ('done', 'cancel')
            )
            if outgoing:
                if all(
                        line.qty_delivered >= line.product_uom_qty
                        for line in order.order_line
                        if not line.display_type
                ):
                    order.sale_order_status = 'delivery_planned'
                    continue

            # 100% Stock Order
            if order.stock_val == 'stock':
                order.sale_order_status = 'available_stock'
                continue

            purchase_orders = PurchaseOrder.search([
                ('origin', '=', order.name)
            ])

            # Waiting for Purchase
            if not purchase_orders:
                order.sale_order_status = 'waiting_purchase'
                continue

            incoming_pickings = purchase_orders.picking_ids.filtered(
                lambda p: p.picking_type_id.code == 'incoming'
                          and p.state != 'cancel'
            )

            # Nothing received yet
            if not incoming_pickings or all(
                    p.state != 'done' and
                    sum(p.move_ids.mapped('quantity')) == 0
                    for p in incoming_pickings
            ):
                order.sale_order_status = 'production'
                continue

            total_qty = sum(incoming_pickings.move_ids.mapped('product_uom_qty'))
            received_qty = sum(incoming_pickings.move_ids.mapped('quantity'))

            if received_qty == 0:
                status = 'production'
            elif received_qty < total_qty:
                status = 'partial_received'
            else:
                status = 'ready_warehouse'

            # If delivery has already been created after stock is ready
            if status == 'ready_warehouse':
                delivery = order.picking_ids.filtered(
                    lambda p: p.picking_type_id.code == 'outgoing'
                              and p.state not in ('done', 'cancel')
                )
                if delivery:
                    status = 'delivery_planned'

            order.sale_order_status = status

    po_receipt_status = fields.Selection([
        ('pending', 'Not Received'),
        ('partial', 'Partially Received'),
        ('full', 'Fully Received'),
    ], string='Receipt Status',
        compute='_compute_receipt_status')

    def _compute_receipt_status(self):
        for order in self:
            purchase_orders = self.env['purchase.order'].search([
                ('origin', '=', order.name)
            ])

            if not purchase_orders:
                order.po_receipt_status = 'pending'
                continue

            statuses = purchase_orders.mapped('receipt_status')

            if all(s == 'full' for s in statuses):
                order.po_receipt_status = 'full'
            elif any(s in ['partial', 'full'] for s in statuses):
                order.po_receipt_status = 'partial'
            else:
                order.po_receipt_status = 'pending'

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
