from odoo import models, fields, api,_
from odoo.exceptions import UserError


class StockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'
    _description = 'Advance Payment'

    company_ids = fields.Many2many('res.company')

    def print_report(self):
        data = {}
        data['form'] = self.read()[0]
        return self.env.ref('stock_report_pdf.action_stock_pdf_report').report_action(self, data=data, config=False)
