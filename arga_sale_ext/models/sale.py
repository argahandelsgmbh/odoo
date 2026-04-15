# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    stock_val = fields.Selection([('stock', '100% Stock')], string='100% Stock')
    commitment_date = fields.Datetime('Liefertermin Bestätigt', copy=False)
    batch_payment_id = fields.Many2one('account.batch.payment')

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
