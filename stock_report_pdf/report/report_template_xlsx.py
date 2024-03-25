from odoo import models
from datetime import date
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta


class ReportXlsx(models.AbstractModel):
    _name = 'report.stock_report_pdf.report_id_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, report):
        sheet = workbook.add_worksheet('Test Report')
        bold = workbook.add_format({'bold': True})
        style = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'green' })

        result = self.env['stock.report.wizard'].browse(self.env.context.get('active_ids'))
        if result.company_ids:
            products = self.env['product.product'].search([('company_id', 'in', result.company_ids.ids)])
        else:
            products = self.env['product.product'].search([])

        inventory_date = result.date
        if not result.date:
            inventory_date = datetime.today()
        row = 3
        col = 3
        res = products._compute_quantities_dict(lot_id=False, owner_id=False, package_id=False, from_date=False,
                                                to_date=inventory_date)
        for obj in report:
            sheet.write(row, col, 'Default Code', bold)
            col += 1
            sheet.write(row, col, 'Product' , bold)
            col += 1
            sheet.write(row, col, 'Quantity on Hand' , bold)
            col += 1
            sheet.write(row, col, 'Cost Price' , bold)
            col += 1
            sheet.write(row, col, 'Total Price' , bold)
            sheet.set_column('D:U', 10)
        i = 4
        total_current = 0

        for product in products:
            qty = res[product.id]['qty_available']
            if qty>0:
                sheet.write(i, 3, product.default_code)
                sheet.write(i, 4, product.name)
                sheet.write(i, 5, qty)
                sheet.write(i, 6, product.standard_price)
                sheet.write(i, 7, product.standard_price * qty)
                i = i + 1
