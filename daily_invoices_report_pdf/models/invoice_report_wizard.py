from odoo import models, fields, api,_
from odoo.exceptions import UserError


class InvoiceReportWizard(models.TransientModel):
    _name = 'invoice.sale.report.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    company_id = fields.Many2one('res.company')

    def print_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'company_id'])[0]
        return self.env.ref('daily_invoices_report_pdf.action_invoice_sale_pdf_report').report_action(self, data=data, config=False)
