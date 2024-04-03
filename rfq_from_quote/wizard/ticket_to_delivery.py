from odoo import api, fields, models
from datetime import datetime

from odoo.exceptions import UserError


class TicketToDelivery(models.TransientModel):
    _name = 'ticket.delivery.wizard'
    _description = 'Ticket to Delivery Wizard'

    name = fields.Char(string='Name')
    ticket_id = fields.Many2one('helpdesk.ticket', string='Quotation/Sale order')
    partner_id = fields.Many2one('res.partner',string="Customer")
    product_id = fields.Many2one('product.product')
    src_location_id = fields.Many2one('stock.location')
    picking_type_id = fields.Many2one('stock.picking.type', string="Operation Type")

    def create_delivery(self):
        vals = {
            'partner_id': self.partner_id.id,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.src_location_id.id,
            'origin': self.ticket_id.name,
            'picking_type_id': self.picking_type_id.id,
        }
        picking = self.env['stock.picking'].create(vals)
        moves = {
            'picking_id': picking.id,
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_uom': self.product_id.uom_id.id,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.src_location_id.id,
            'product_uom_qty': 1,
        }
        stock_move = self.env['stock.move'].create(moves)
