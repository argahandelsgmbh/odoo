from odoo import api, fields, models, _


class PurchaseOrderSaleOrder(models.Model):
    _inherit = 'purchase.order.line'