
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    repair_order_id = fields.Many2one(
        "repair.order", string="Repair Order", readonly=True)
