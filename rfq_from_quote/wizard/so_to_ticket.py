from odoo import api, fields, models
from datetime import datetime

from odoo.exceptions import UserError


class SaleQuoteToTicket(models.TransientModel):
    _name = 'quote.ticket.wizard'
    _description = 'Quotation to Ticket Wizard'

    name = fields.Char(string='Name')
    sale_id = fields.Many2one('sale.order', string='Sale order')
    partner_id = fields.Many2one('res.partner', string='Customer', related='sale_id.partner_id')
    sale_line_ids = fields.Many2many('sale.order.line', string='Products')

    def create_ticket(self):
        if not self.sale_id or not self.sale_line_ids:
            return

        if len(self.sale_line_ids) > 1:
            raise UserError('Lines cannot greater than 1.')
        vals = {
            'partner_id': self.sale_id.partner_id.id,
            'user_id': self.sale_id.user_id.id,
            'sale_line_id': self.sale_line_ids[0].id,
            'product_id': self.sale_line_ids[0].product_id.id,
            'name': self.sale_id.name,
            'company_id': self.sale_id.company_id.id,
        }
        print(self.sale_id.company_id.name)
        ticket = self.env['helpdesk.ticket'].with_context(default_company_id=self.sale_id.company_id.id).with_company(self.sale_id.company_id.id
).sudo().create(vals)
        ticket.company_id = self.sale_id.company_id.id
        tickets = self.env['helpdesk.ticket'].search([('sale_line_id.order_id', '=', self.sale_id.id)]).ids
        self.sale_id.ticket_ids = tickets
