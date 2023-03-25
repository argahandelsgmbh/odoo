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
        action['domain'] = [('id', '=', po_id.id)]
        return action

    def open_so_to_rfq_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RFQ/PO',
            'view_id': self.env.ref('rfq_from_quote.so_to_rfq_wizard_form', False).id,
            'context': {'default_sale_id': self.id, 'default_vendor_id': self.partner_id.id, 'default_sale_line_ids': self.order_line.mapped('id')},
            'target': 'new',
            'res_model': 'quote.rfq.wizard',
            'view_mode': 'form',
        }
