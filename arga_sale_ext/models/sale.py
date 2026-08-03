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


    def action_recompute_sale_order_status(self):
        for order in self:
            order._compute_sale_order_status()


    @api.depends(
        'state',
        'stock_val',
        'order_line.qty_delivered',
    )
    def _compute_sale_order_status(self):
        PurchaseOrder = self.env['purchase.order']

        for order in self:
            order.sale_order_status = False

            if order.state not in ('sale', 'done'):
                continue

            # Delivered
            if order.order_line and all(
                    line.display_type or line.qty_delivered >= line.product_uom_qty
                    for line in order.order_line
            ):
                order.sale_order_status = 'delivered'
                continue

            # 100% Stock
            if order.stock_val == 'stock':
                order.sale_order_status = 'available_stock'
                continue

            # Find PO created from this Sale Order
            purchase_orders = PurchaseOrder.search([
                ('origin', '=', order.name)
            ])

            # No PO created
            if not purchase_orders:
                order.sale_order_status = 'waiting_purchase'
                continue

            receipt_statuses = purchase_orders.mapped('receipt_status')

            # Partial received
            if any(status == 'partial' for status in receipt_statuses):
                order.sale_order_status = 'partial_received'
                continue

            # Fully received
            if receipt_statuses and all(
                    status == 'full' for status in receipt_statuses
            ):
                outgoing = order.picking_ids.filtered(
                    lambda p: p.picking_type_id.code == 'outgoing'
                              and p.state not in ('done', 'cancel')
                )

                if outgoing:
                    # Check if delivery is ready (stock reserved/available)
                    ready_delivery = outgoing.filtered(
                        lambda p: p.state in ('assigned', 'confirmed')
                    )

                    if ready_delivery:
                        order.sale_order_status = 'delivery_planned'
                    else:
                        order.sale_order_status = 'ready_warehouse'
                else:
                    order.sale_order_status = 'ready_warehouse'

                continue

            # PO exists but nothing received
            order.sale_order_status = 'production'

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


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()

        sale_orders = self.env['sale.order']

        for picking in self:
            if picking.picking_type_id.code == 'incoming' and picking.purchase_id:
                origin = picking.purchase_id.origin

                if origin:
                    orders = self.env['sale.order'].search([
                        ('name', '=', origin)
                    ])
                    sale_orders |= orders

        if sale_orders:
            sale_orders._compute_sale_order_status()

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
