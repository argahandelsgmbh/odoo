# -*- coding: utf-8 -*-
import json

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_count = fields.Integer(compute='compute_payments')
    date_order = fields.Datetime(string='Order Date', required=True, readonly=False,  index=True, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    payment_ids = fields.Many2many('account.payment', compute="compute_payments")
    purchase_order_ids = fields.Many2many('purchase.order', compute="compute_payments")
    commitment_date = fields.Datetime('Delivery Date', copy=False,
                                      help="This is the delivery date promised to the customer. "
                                           "If set, the delivery order will be scheduled based on "
                                           "this date rather than product lead times.")





    def compute_payments(self):
        
        for rec in self:
            rec.purchase_order_ids = self.env['purchase.order'].search([('origin', '=', rec.name)]).ids
            pay_list = []
            for inv in rec.invoice_ids:
                reconciled_payments_widget_vals = json.loads(inv.invoice_payments_widget)

                if inv.invoice_payments_widget != 'false':
                    pay_list += [vals['account_payment_id'] for vals in reconciled_payments_widget_vals['content']]
            rec.payment_count = self.env['account.payment'].search_count([('ref', '=', rec.name)]) + len(pay_list)


            pay_list = []
            for inv in self.invoice_ids:
                reconciled_payments_widget_vals = json.loads(inv.invoice_payments_widget)
    
                if inv.invoice_payments_widget != 'false':
                    pay_list += [vals['account_payment_id'] for vals in reconciled_payments_widget_vals['content']]
    
            payment = self.env['account.payment'].search([('ref', '=', rec.name)]).ids
           rec.payment_ids = payment + pay_list




    def action_show_payments(self):
        self.ensure_one()
        pay_list = []
        for inv in self.invoice_ids:
            reconciled_payments_widget_vals = json.loads(inv.invoice_payments_widget)

            if inv.invoice_payments_widget != 'false':
                pay_list += [vals['account_payment_id'] for vals in reconciled_payments_widget_vals['content']]
        return {
            'name': 'Payments',
            'res_model': 'account.payment',
            'domain': ['|', ('ref', '=', self.name), ('id', 'in', pay_list)],
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }

    def action_open_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Payment',
            'view_id': self.env.ref('account.view_account_payment_form', False).id,
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_amount': self.amount_total,
                'default_ref': self.name,
                'default_payment_type': 'inbound',
                'default_partner_type': 'customer',
                'search_default_inbound_filter': 1,
                'default_move_journal_types': ('bank', 'cash'),
                "edit": False,
                "create": False,
            },
            'target': 'new',
            'res_model': 'account.payment',
            'view_mode': 'form',
        }
