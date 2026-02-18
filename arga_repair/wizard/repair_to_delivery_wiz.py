from odoo import api, fields, models
from datetime import datetime


class RepairToDeliveryWi(models.TransientModel):
    _name = 'repair.delivery.wizard'
    _description = 'Repair To Delivery Wizard'

    name = fields.Char(string='Name')
    repair_id = fields.Many2one('repair.order', string='Repair')
    partner_id = fields.Many2one('res.partner', string='Customer')
    operation_type_id = fields.Many2one('stock.picking.type', string='Operation Type')
    repair_line_ids = fields.Many2many('stock.move', string='Products')

    def create_delivery(self):
        if not self.repair_id or not self.repair_line_ids:
            return
        picking_type_id = self.operation_type_id
        customer_location_id = self.env['stock.location'].search([('usage', '=', 'customer')], limit=1)

        vals = {
            'partner_id': self.partner_id.id,
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': customer_location_id.id,
            'origin': self.repair_id.name,
            'picking_type_id': picking_type_id.id,
            'move_ids_without_package': self.repair_line_ids,

        }
        picking = self.env['stock.picking'].create(vals)

