# -*- coding: utf-8 -*-
import json

from odoo import api, models


class SaleReportCustom(models.AbstractModel):
    _name = 'report.daily_invoices_report_pdf.report_invoice_sale_document'

    def get_order_payment(self, order):
        pay_list = []
        for inv in order.invoice_ids:
            reconciled_payments_widget_vals = json.loads(inv.invoice_payments_widget)

            if inv.invoice_payments_widget != 'false':
                pay_list += [vals['account_payment_id'] for vals in reconciled_payments_widget_vals['content']]

        payment = self.env['account.payment'].search([('ref', '=', order.name)]).ids
        payments = sum(self.env['account.payment'].browse(payment + pay_list).mapped('amount'))
        return payments

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))

        invoices = self.env['account.move'].search([('invoice_date', '>=', rec_model.date_from),
                                                    ('invoice_date', '<=', rec_model.date_to),
                                                    ('company_id', '=', rec_model.company_id.id),
                                                    ('state', '=', 'posted'), ('move_type', '=', 'out_invoice')])
        payments = self.env['account.payment'].search([('date', '>=', rec_model.date_from),
                                                    ('date', '<=', rec_model.date_to),
                                                    ('company_id', '=', rec_model.company_id.id),
                                                    ('state', '=', 'posted'), ('partner_type', '=', 'customer')])
        orders = self.env['sale.order'].search([('date_order', '>=', rec_model.date_from),
                                                       ('date_order', '<=', rec_model.date_to),
                                                       ('company_id', '=', rec_model.company_id.id),
                                                       ('state', 'in', ['sale', 'done'])])
        return {
            'docs': rec_model,
            'doc_model': 'daily_invoices_report_pdf.invoice.sale.report.wizard',
            'invoices': invoices,
            'payments': payments,
            'orders': orders,
            'date_from': rec_model.date_from,
            'date_to': rec_model.date_to,
            'get_order_payment': self.get_order_payment,
        }
