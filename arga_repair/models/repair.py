# -*- coding: utf-8 -*-

from odoo import models, fields, api


class RepairOrderLineInh(models.Model):
    _inherit = 'stock.move'

    qty_available = fields.Float(related='product_id.qty_available')


class RepairOrderInh(models.Model):
    _inherit = 'repair.order'

    def action_repair_end(self):
        if self.ticket_id:
            done_state = self.env['helpdesk.stage'].search([('name', '=', 'Done')], limit=1)
            if done_state:
                self.ticket_id.stage_id = done_state.id
        return super().action_repair_end()

    delivery_count = fields.Integer(string='Delivery Count', compute='count_delivery')
    is_po_created = fields.Boolean()

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
            rec.delivery_count = self.env['stock.picking'].search_count([('origin', '=', self.name)])

    def open_repair_to_rfq_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RFQ/PO',
            'view_id': self.env.ref('arga_repair.repair_to_rfq_wizard_form', False).id,
            'context': {'default_repair_id': self.id, 'default_vendor_id': self.partner_id.id,'default_repair_line_ids': self.move_ids.mapped('id')},
            'target': 'new',
            'res_model': 'repair.rfq.wizard',
            'view_mode': 'form',
        }

    def open_repair_to_delivery_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Delivery',
            'view_id': self.env.ref('arga_repair.repair_to_delivery_wizard_form', False).id,
            'context': {'default_repair_id': self.id, 'default_partner_id': self.partner_id.id,
                        'default_repair_line_ids': self.move_ids.mapped('id')},
            'target': 'new',
            'res_model': 'repair.delivery.wizard',
            'view_mode': 'form',
        }
