from odoo import models, fields, api,_
from odoo.exceptions import UserError


class InvoiceReportWizard(models.TransientModel):
    _name = 'invoice.report.wizard'
    _description = 'Invoice report wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    company_ids = fields.Many2many('res.company')

    def print_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'company_ids'])[0]
        return self.env.ref('invoices_report_pdf.action_invoice_pdf_report').report_action(self, data=data, config=False)
