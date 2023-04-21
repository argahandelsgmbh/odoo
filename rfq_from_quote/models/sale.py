from odoo import api, fields, models, _ 
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SaleOrderRFQ(models.Model):
    _inherit = 'sale.order'

    purchase_count = fields.Integer(string='Purchase Order Count', compute='count_purchase_order')
    is_po_created = fields.Boolean()

    def count_purchase_order(self):
        for rec in self:
            rec.purchase_count = self.env['purchase.order'].search_count([('origin', '=', self.name)])

    def open_related_po(self):
        po_id = self.env['purchase.order'].search([('origin', '=', self.name)])
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        action['domain'] = [('id', 'in', po_id.ids)]
        return action

    def get_products_vendor(self):
        vendor_list = []
        for line in self.order_line:
            if line.product_id.type == 'product' and line.product_id.seller_ids:
                vendor_list.append(line.product_id.seller_ids[0].name.id)
        return vendor_list

    def open_so_to_rfq_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RFQ/PO',
            'view_id': self.env.ref('rfq_from_quote.so_to_rfq_wizard_form', False).id,
            'context': {'default_sale_id': self.id, 'default_vendor_id': self.partner_id.id, 'default_vendor_ids': self.get_products_vendor(), 'default_sale_line_ids': self.order_line.mapped('id')},
            'target': 'new',
            'res_model': 'quote.rfq.wizard',
            'view_mode': 'form',
        }