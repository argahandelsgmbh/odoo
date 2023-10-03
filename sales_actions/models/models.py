# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        rec = super().button_confirm()
        if self.origin:
            order = self.env['sale.order'].search([('name', '=', self.origin)])
            if order:
                order.compute_is_po_draft()
        return rec


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_ready = fields.Boolean(compute='compute_is_ready', store=True)
    is_po_draft = fields.Boolean(compute='compute_is_po_draft', store=True)
    # is_po_draft = fields.Boolean( store=True)
    is_do_done = fields.Boolean(compute='compute_is_ready', store=True)
    payment_count = fields.Integer(compute='count_payments')
    date_order = fields.Datetime(string='Order Date', required=True, readonly=False,  index=True, copy=False, default=fields.Datetime.now, help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")


    def count_payments(self):
        for rec in self:
            rec.payment_count = self.env['account.payment'].search_count([('ref', '=', self.name)])

    def action_show_payments(self):
        self.ensure_one()
        return {
            'name': 'Payments',
            'res_model': 'account.payment',
            'domain': [('ref', '=', self.name)],
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

    @api.depends('name', 'write_date')
    def compute_is_po_draft(self):
        for r in self:
            po = self.env['purchase.order'].search(['|',('sale_order', '=', r.id),('origin', '=', r.name)])
            if po:
                res = all(rec.state != 'done' for rec in po)
                r.is_po_draft = res
            else:
                r.is_po_draft = False

    @api.depends('picking_ids', 'picking_ids.state')
    def compute_is_ready(self):
        for r in self:
            if r.picking_ids:
                res = all(rec.state == 'assigned'for rec in r.picking_ids)
                done = all(rec.state == 'done'for rec in r.picking_ids)
                r.is_do_done = done
                r.is_ready = res
            else:
                r.is_do_done = False
                r.is_ready = False
            # if res:
            #     r.is_ready = res
            # else:
            #     r.is_ready = False
            # if done:
            #     r.is_do_done = done
            # else:
            #     r.is_do_done = False
