from odoo import api, fields, models, _ 
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    product_status = fields.Selection([('stock', 'Stock'), ('po', 'PO')], string='Product Status', default='stock')


class SaleOrderRFQ(models.Model):
    _inherit = 'sale.order'

    is_po_created = fields.Boolean()


    def get_products_vendor(self):
        vendor_list = []
        for line in self.order_line:
          if line.product_id.type == 'product': 
            if line.product_id.type == 'product' and line.product_id.seller_ids:
                vendor_list.append(line.product_id.seller_ids[0].name.id)
        return vendor_list

    def open_so_to_rfq_wizard(self):
        sale_line_ids = self.order_line.filtered(lambda line: line.product_id.type in ['product']).mapped('id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RFQ/PO',
            'view_id': self.env.ref('rfq_from_quote.so_to_rfq_wizard_form', False).id,
            'context': {'default_sale_id': self.id, 'default_vendor_id': False, 'default_vendor_ids': self.get_products_vendor(), 'default_sale_line_ids': sale_line_ids},
            'target': 'new',
            'res_model': 'quote.rfq.wizard',
            'view_mode': 'form',
        }
