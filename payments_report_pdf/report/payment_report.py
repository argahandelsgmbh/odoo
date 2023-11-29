# -*- coding: utf-8 -*-
from odoo import api, models


class SaleReportCustom(models.AbstractModel):
    _name = 'report.payments_report_pdf.report_payment_document'
    _description='report payment document'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))

        payments = self.env['account.payment'].sudo().search([('date', '>=', rec_model.date_from),
                                                    ('date', '<=', rec_model.date_to), ('partner_type', '=', 'customer'),
                                                    ('company_id', 'in', rec_model.company_ids.ids),
                                                    ('state', '=', 'posted')])
        return {
            'docs': rec_model,
            'doc_model': 'payments_report_pdf.payment.report.wizard',
            'payments': payments,
            'date_from': rec_model.date_from,
            'date_to': rec_model.date_to,
        }
