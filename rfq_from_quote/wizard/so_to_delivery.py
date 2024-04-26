from odoo import api, fields, models
from datetime import datetime


class SaleQuoteToDelivery(models.TransientModel):
    _name = 'sale.delivery.wizard'
    _description = 'Sale to Delivery Wizard'

    name = fields.Char(string='Name')
    sale_id = fields.Many2one('sale.order', string='Quotation/Sale order')
    picking_type_id = fields.Many2one('stock.picking.type')
    company_id = fields.Many2one('res.company',domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    partner_id = fields.Many2one('res.partner', string='Customer', domain="[('customer_rank', '>', 0)]")
    sale_line_ids = fields.Many2many('sale.order.line', string='Products')

    def create_delivery(self):
        picking_type=self.env['stock.picking.type'].search([('code','=','outgoing'),('company_id','=',self.company_id.id)],limit=1)
        vals = {
            'partner_id': self.partner_id.id,
            'location_id': self.picking_type_id.default_location_src_id.id,
            'location_dest_id': self.picking_type_id.default_location_src_id.id,
            'origin': self.sale_id.name,
            'sale_id': self.sale_id.id,
            'company_id': self.company_id.id,
            'picking_type_id': picking_type.id,
        }
        picking = self.env['stock.picking'].create(vals)
        for line in self.sale_line_ids:
            moves = {
                'picking_id': picking.id,
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'product_uom': line.product_id.uom_id.id,
                'location_id': self.picking_type_id.default_location_src_id.id,
                'location_dest_id': self.picking_type_id.default_location_src_id.id,
                'product_uom_qty': line.product_uom_qty,
                'sale_line_id': line.id,
            }
            stock_move = self.env['stock.move'].create(moves)

        self.sale_id.picking_ids = picking.ids + self.sale_id.picking_ids.ids
        self.sale_id._compute_picking_ids()
