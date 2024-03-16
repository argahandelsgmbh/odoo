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

#     def export_excel_old(self):
#         main_header_style = easyxf('font:height 400;'
#                                    'align: horiz center;font: color black; font:bold True;'
#                                    "borders: top thin,left thin,right thin,bottom thin")
#         main_date_style = easyxf('font:height 300;'
#                                  'align: horiz center;font: color black; font:bold True;'
#                                  "borders: top thin,left thin,right thin,bottom thin")
#
#         header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
#                               'align: horiz center;font: color black; font:bold True;'
#                               "borders: top thin,left thin,right thin,bottom thin")
#         header_style_name = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
#                                    'align: horiz left;font: color black; font:bold True;'
#                                    "borders: top thin,left thin,right thin,bottom thin")
#
#         text_left = easyxf('font:height 200; align: horiz left;' "borders: top thin,bottom thin")
#         text_center = easyxf('font:height 200; align: horiz center;' "borders: top thin,bottom thin")
#         text_left_bold = easyxf(
#             'font:height 200; align: horiz left;font:bold True;' "borders: top thin,bottom thin")
#         text_right_bold = easyxf(
#             'font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin")
#         text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin",
#                             num_format_str='0.00')
#         workbook = xlwt.Workbook()
#         worksheet = []
#         for l in range(0, 3):
#             worksheet.append(l)
#         work = 0
#         worksheet[work] = workbook.add_sheet('Stock Report')
#
#         if self.company_ids:
#             products = self.env['product.product'].search([('company_id', 'in', self.company_ids.ids)])
#         else:
#             products = self.env['product.product'].search([])
#
#         inventory_date = self.date
#         if not self.date:
#             inventory_date = datetime.today()
#
#         worksheet[work].write_merge(3, 4, 3, 7, ','.join(self.company_ids.mapped('name')), main_date_style)
#         worksheet[work].write_merge(5, 6, 4, 6, (inventory_date).strftime("%d-%m-%Y"), main_date_style)
#
#         worksheet[work].write(8, 3, 'Default Code', header_style)
#         worksheet[work].write(8, 4, 'Product', header_style)
#         worksheet[work].write(8, 5, 'Quantity on Hand', header_style)
#         worksheet[work].write(8, 6, 'Cost Price', header_style)
#         worksheet[work].write(8, 7, 'Total Value', header_style)
#
#         worksheet[work].col(3).width = 256 * 20
#         worksheet[work].col(4).width = 256 * 30
#         worksheet[work].col(5).width = 256 * 20
#         worksheet[work].col(6).width = 256 * 20
#         worksheet[work].col(7).width = 256 * 20
#         total_qty = 0
#         total_cost = 0
#         total_value = 0
#         i = 9
#         res = products._compute_quantities_dict(lot_id=False, owner_id=False, package_id=False, from_date=False,
#                                                to_date=inventory_date)
#         for product in products:
#             qty = res[product.id]['qty_available']
#             print(work)
#             worksheet[work].write(i, 3, product.default_code, text_left)
#             worksheet[work].write(i, 4, product.name, text_left)
#             worksheet[work].write(i, 5, qty, text_center)
#             worksheet[work].write(i, 6, product.standard_price, text_center)
#             worksheet[work].write(i, 7, product.standard_price * qty, text_center)
#             total_qty += qty
#             total_cost += product.standard_price
#             total_value += product.standard_price * qty
#             i = i + 1
#             if i == 65500:
#                 i = 9
#                 work += 1
#                 worksheet[work] = workbook.add_sheet('Stock Report '+ str(work))
#                 worksheet[work].write(8, 3, 'Default Code', header_style)
#                 worksheet[work].write(8, 4, 'Product', header_style)
#                 worksheet[work].write(8, 5, 'Quantity on Hand', header_style)
#                 worksheet[work].write(8, 6, 'Cost Price', header_style)
#                 worksheet[work].write(8, 7, 'Total Value', header_style)
#
#                 worksheet[work].col(3).width = 256 * 20
#                 worksheet[work].col(4).width = 256 * 30
#                 worksheet[work].col(5).width = 256 * 20
#                 worksheet[work].col(6).width = 256 * 20
#                 worksheet[work].col(7).width = 256 * 20
#
#         # for line in lines:
#         #     quantity = line.inventory_quantity_auto_apply if line.inventory_quantity_auto_apply > 0 else 0
#         #     if line.inventory_quantity_auto_apply > 0:
#         #         worksheet[work].write(i, 3, line.product_id.default_code, text_left)
#         #         worksheet[work].write(i, 4,  line.product_id.name, text_left)
#         #         worksheet[work].write(i, 5,  quantity, text_center)
#         #         worksheet[work].write(i, 6,  line.product_id.standard_price, text_center)
#         #         worksheet[work].write(i, 7,  line.product_id.standard_price * quantity, text_center)
#         #         total_qty += (line.inventory_quantity_auto_apply)
#         #         total_cost += line.product_id.standard_price
#         #         total_value += line.product_id.standard_price * line.inventory_quantity_auto_apply
#         #         i = i + 1
#
#         worksheet[work].write(i, 4, "Total", header_style)
#         worksheet[work].write(i, 5,  "{:.3f}".format(total_qty), header_style)
#         worksheet[work].write(i, 6,  "{:.3f}".format(total_cost), header_style)
#         worksheet[work].write(i, 7,  "{:.3f}".format(total_value), header_style)
#
#         fp = BytesIO()
#         workbook.save(fp)
#         export_id = self.env['stock.excel'].create(
#             {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': 'StockReport.xlsx'})
#
#         return {
#             'type': 'ir.actions.act_url',
#             'url': 'web/content/?model=stock.excel&field=excel_file&download=true&id=%s&filename=StockReport.xlsx' % (
#                 export_id.id),
#             'target': 'new', }
#
#
class StockExcel(models.TransientModel):
    _name = "stock.excel"

    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('Excel Name', size=64)

