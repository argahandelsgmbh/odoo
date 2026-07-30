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
            if order.state in ['sale', 'done']:

                purchase_orders = PurchaseOrder.search([
                    ('origin', '=', order.name)
                ])
    
                # Waiting for Purchase
                if not purchase_orders:
                     if not order.stock_val == 'stock':
                            order.sale_order_status = 'waiting_purchase'

                
                # In Production
                if purchase_orders and purchase_orders.receipt_status=='pending':
                   order.sale_order_status = 'production'

                # Partially Received
                if purchase_orders and purchase_orders.receipt_status=='partial':
                   order.sale_order_status = 'partial_received'

                # Ready in Warehouse
                if purchase_orders and purchase_orders.receipt_status=='full':
                   order.sale_order_status = 'ready_warehouse'

               available = True
               for line in order.order_line.filtered(lambda l: not l.display_type):
                   product = line.product_id
    
                   # Skip services
                   if product.type != 'product':
                      continue
    
                   qty_available = product.with_context(
                        warehouse=order.warehouse_id.id
                    ).qty_available
    
                   if qty_available < line.product_uom_qty:
                      available = False
                      break

                # 100% Stock Order
                if order.stock_val == 'stock' or available:
                   order.stock_status = 'stock'

                # Fully delivered
                if order.order_line and all(
                        line.qty_delivered >= line.product_uom_qty
                        for line in order.order_line
                        if not line.display_type
                ):
                    order.sale_order_status = 'delivered'
                    continue
    
                # Delivery planned
                outgoing = order.picking_ids.filtered(lambda p: p.picking_type_id.code == 'outgoing' and p.state in ('confirmed', 'assigned'))
                if outgoing:
                   order.sale_order_status = 'delivery_planned'

                # Delivered
                outgoing = order.picking_ids.filtered(lambda p: p.picking_type_id.code == 'outgoing' and p.state == 'done')
                if outgoing:
                   order.sale_order_status = 'delivery_planned'

                

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
