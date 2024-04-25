from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    delivery_count = fields.Integer(string='Delivery Count', compute='count_delivery')


    def action_open_delivery(self):
        self.ensure_one()
        return {
            'name': 'Delivery Orders',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name)],
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }

    def count_delivery(self):
        for rec in self:
            rec.delivery_count = self.env['stock.picking'].search_count([('origin', '=', self.name),('group_id', '=',False)])

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
