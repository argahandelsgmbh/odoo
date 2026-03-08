from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    delivery_count = fields.Integer(string='Delivery Count', compute='count_delivery')
    sale_order_count = fields.Integer(string='Order Count', compute='count_delivery')
    invoices_count = fields.Integer(string='Invoice Count', compute='count_delivery')
    all_ticket_count = fields.Integer(string='Tickets Count', compute='count_delivery')

    def action_open_related_tickets(self):
        self.ensure_one()
        return {
            'name': 'Tickets',
            'res_model': 'helpdesk.ticket',
            'domain': [('partner_id', '=', self.partner_id.id), ('id', '!=', self.id)],
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }

    def action_open_related_invoices(self):
        self.ensure_one()
        return {
            'name': 'Invoices',
            'res_model': 'account.move',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }

    def action_open_related_orders(self):
        self.ensure_one()
        return {
            'name': 'Sale Orders',
            'res_model': 'sale.order',
            'domain': [('partner_id', '=', self.partner_id.id)],
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }

    def action_open_delivery(self):
        self.ensure_one()
        return {
            'name': 'Delivery Orders',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name)],
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }

    def count_delivery(self):
        for rec in self:
            rec.delivery_count = self.env['stock.picking'].search_count([('origin', '=', self.name)])
            rec.sale_order_count = self.env['sale.order'].search_count([('partner_id', '=', self.partner_id.id)])
            rec.invoices_count = self.env['account.move'].search_count([('partner_id', '=', self.partner_id.id),('move_type', '=', 'out_invoice')])
            rec.all_ticket_count = self.env['helpdesk.ticket'].search_count([('partner_id', '=', self.partner_id.id),('id', '!=', self.id)])

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
