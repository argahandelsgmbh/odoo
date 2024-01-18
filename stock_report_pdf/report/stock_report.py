# -*- coding: utf-8 -*-
from odoo import api, models


class StockReportCustom(models.AbstractModel):
    _name = 'report.stock_report_pdf.report_stock_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        print(rec_model.company_ids)
        if rec_model.company_ids:
            lines = self.env['stock.quant'].search([('company_id', 'in', rec_model.company_ids.ids)])
        else:
            lines = self.env['stock.quant'].search([])
        print(len(lines))
        return {
            'doc_ids': self.ids,
            'doc_model': 'stock_report_pdf.stock.report.wizard',
            'lines': lines,
            'companies': ','.join(lines.mapped('company_id.name')),
        }