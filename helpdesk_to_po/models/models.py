# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
    received_status = fields.Selection([
        ('received', 'Received'),
        ('not_received', 'Not Received'),
    ], 'Receiving Status', readonly=True)

    def action_purchase_qty(self):
        orders = self.env['purchase.order'].search([('state', '=', 'purchase')])
        # orders = self.env['purchase.order'].search([('id', '=', 1857)])
        for purchase in orders:
            res = all(line.product_qty == line.qty_received for line in purchase.order_line)
            if not res:
                purchase.received_status = 'not_received'
            else:
                purchase.button_done()
                purchase.received_status = 'received'


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    po_count = fields.Integer(string='Po Count', compute='count_po')

    def count_po(self):
        for rec in self:
            rec.po_count = self.env['purchase.order'].search_count([('origin', '=', self.name)])

    def action_open_po(self):
        self.ensure_one()
        return {
            'name': 'purchases',
            'res_model': 'purchase.order',
            'domain': [('origin', '=', self.name)],
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }

    def open_helpdesk_to_rfq_wizard(self):
        lines = [(0, 0, {"product_id": self.product_id.id, "price_unit": 1})]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RFQ/PO',
            'view_id': self.env.ref('helpdesk_to_po.helpdesk_to_rfq_wizard_form', False).id,
            'context': {'default_ticket_id': self.id, 'default_vendor_id': self.partner_id.id, 'default_helpdesk_lines': lines},
            'target': 'new',
            'res_model': 'helpdesk.rfq.wizard',
            'view_mode': 'form'}
