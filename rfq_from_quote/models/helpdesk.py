from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def open_ticket_to_delivery_wizard(self):
        picking = self.env['stock.picking.type'].search([('code', '=', 'outgoing')], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Delivery',
            'view_id': self.env.ref('rfq_from_quote.ticket_delivery_wizard_form', False).id,
            'context': {'default_ticket_id': self.id, 'default_product_id': self.product_id.id,
                        'default_picking_type_id': picking.id,
                        'default_partner_id': self.partner_id.id,
                        'default_src_location_id': self.partner_id.property_stock_customer.id
                        },
            'target': 'new',
            'res_model': 'ticket.delivery.wizard',
            'view_mode': 'form',
        }
