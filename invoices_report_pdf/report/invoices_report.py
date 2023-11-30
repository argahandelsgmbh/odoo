# -*- coding: utf-8 -*-
from odoo import api, models


class SaleReportCustom(models.AbstractModel):
    _name = 'report.invoices_report_pdf.report_invoice_document'
    _description='report invoices_report_pdf report_invoice_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))

        invoices = self.env['account.move'].sudo().search([('invoice_date', '>=', rec_model.date_from),
                                                    ('invoice_date', '<=', rec_model.date_to), ('move_type', 'in', ['out_refund','out_invoice'),
                                                    ('company_id', 'in', rec_model.company_ids.ids),
                                                    ('state', '=', 'posted')])
        print(invoices)
        return {
            'docs': rec_model,
            'doc_model': 'invoices_report_pdf.invoice.report.wizard',
            'invoices': invoices,
            'date_from': rec_model.date_from,
            'date_to': rec_model.date_to,
        }
