import base64
from datetime import datetime, timedelta
from io import BytesIO

import xlwt
from xlwt import easyxf

from odoo import models, fields


class StockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'
    _description = 'Report wizard'

    company_ids = fields.Many2many('res.company')
    date = fields.Date('Inventory at Date')

    def print_report(self):
        data = {}
        data['form'] = self.read()[0]
        return self.env.ref('stock_report_pdf.action_stock_pdf_report').report_action(self, data=data, config=False)

    def export_excel(self):
        data = {
            'form': self.read()[0],
        }
        return self.env.ref('stock_report_pdf.report_xlsx_stock').report_action(self, data=data)

class StockExcel(models.TransientModel):
    _name = "stock.excel"

    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('Excel Name', size=64)

