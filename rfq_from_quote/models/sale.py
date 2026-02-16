from odoo import api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    product_status = fields.Selection([('stock', 'Stock'), ('po', 'PO')], string='Product Status', default='stock')

    def _get_protected_fields(self):
        return [
        ]


class SaleOrderRFQ(models.Model):
    _inherit = 'sale.order'

    is_po_created = fields.Boolean()
    ticket_ids = fields.Many2many('helpdesk.ticket',string="Yardim masasi")
    ticket_so_count = fields.Integer(compute="compute_related_tickets")

    @api.depends('ticket_ids')
    def compute_related_tickets(self):
        for rec in self:
            rec.ticket_so_count = len(self.ticket_ids.ids)

    def action_open_ticket(self):
        return {
            'name': ('Tickets'),
            'type': 'ir.actions.act_window',
            'res_model': 'helpdesk.ticket',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.ticket_ids.ids)],
        }

    def action_confirm(self):
        r = super().action_confirm()
        return r

    def get_products_vendor(self):
        vendor_list = []
        for line in self.order_line:
            if line.product_id.type == 'product':
                if line.product_id.type == 'product' and line.product_id.seller_ids:
                    vendor_list.append(line.product_id.seller_ids[0].name.id)
        return vendor_list

    def open_so_to_rfq_wizard(self):
        sale_line_ids = self.order_line.filtered(lambda line: not line.display_type and line.product_id.type in ['product']).mapped('id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RFQ/PO',
            'view_id': self.env.ref('rfq_from_quote.so_to_rfq_wizard_form', False).id,
            'context': {'default_sale_id': self.id, 'default_sale_line_ids': sale_line_ids},
            'target': 'new',
            'res_model': 'quote.rfq.wizard',
            'view_mode': 'form',
        }

    def open_so_to_ticket_wizard(self):
        sale_line_ids = self.order_line.filtered(lambda line: not line.display_type).mapped('id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Ticket',
            'view_id': self.env.ref('rfq_from_quote.so_to_ticket_wizard_form', False).id,
            'context': {'default_sale_id': self.id, 'default_sale_line_ids': sale_line_ids},
            'target': 'new',
            'res_model': 'quote.ticket.wizard',
            'view_mode': 'form',
        }

    def open_so_to_delivery_wizard(self):
        sale_line_ids = self.order_line.filtered(lambda line: not line.display_type and line.product_id.type in ['product']).mapped('id')
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('company_id', '=', self.company_id.id)], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Delivery',
            'view_id': self.env.ref('rfq_from_quote.so_to_delivery_wizard_form', False).id,
            'context': {'default_picking_type_id':picking_type.id,'default_company_id': self.company_id.id,'default_sale_id': self.id, 'default_partner_id': self.partner_shipping_id.id, 'default_sale_line_ids': sale_line_ids},
            'target': 'new',
            'res_model': 'sale.delivery.wizard',
            'view_mode': 'form',
        }
