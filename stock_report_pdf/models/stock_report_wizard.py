import base64
from io import BytesIO

import xlwt
from xlwt import easyxf

from odoo import models, fields


class StockReportWizard(models.TransientModel):
    _name = 'stock.report.wizard'
    _description = 'Report wizard'

    company_ids = fields.Many2many('res.company')

    def print_report(self):
        data = {}
        data['form'] = self.read()[0]
        return self.env.ref('stock_report_pdf.action_stock_pdf_report').report_action(self, data=data, config=False)

    def export_excel(self):
        main_header_style = easyxf('font:height 400;'
                                   'align: horiz center;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")
        main_date_style = easyxf('font:height 300;'
                                 'align: horiz center;font: color black; font:bold True;'
                                 "borders: top thin,left thin,right thin,bottom thin")

        header_style = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")
        header_style_name = easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                                   'align: horiz left;font: color black; font:bold True;'
                                   "borders: top thin,left thin,right thin,bottom thin")

        text_left = easyxf('font:height 200; align: horiz left;' "borders: top thin,bottom thin")
        text_center = easyxf('font:height 200; align: horiz center;' "borders: top thin,bottom thin")
        text_left_bold = easyxf(
            'font:height 200; align: horiz left;font:bold True;' "borders: top thin,bottom thin")
        text_right_bold = easyxf(
            'font:height 200; align: horiz right;font:bold True;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin",
                            num_format_str='0.00')
        workbook = xlwt.Workbook()
        worksheet = []
        for l in range(0, 1):
            worksheet.append(l)
        work = 0
        # date_from = self.date_from.strftime("%d-%m-%Y")
        # date_to = self.date_from.strftime("%d-%m-%Y")
        worksheet[work] = workbook.add_sheet('Stock Report')

        if self.company_ids:
            lines = self.env['stock.quant'].sudo().search([('company_id', 'in', self.company_ids.ids)])
        else:
            lines = self.env['stock.quant'].sudo().search([])
        # worksheet[work].write_merge(0, 1, 3, 6, ','.join(lines.mapped('company_id.name')), main_header_style)
        worksheet[work].write_merge(3, 4, 3, 7, ','.join(lines.mapped('company_id.name')), main_date_style)

        worksheet[work].write(6, 3, 'Default Code', header_style)
        worksheet[work].write(6, 4, 'Product', header_style)
        worksheet[work].write(6, 5, 'Quantity on Hand', header_style)
        worksheet[work].write(6, 6, 'Cost Price', header_style)
        worksheet[work].write(6, 7, 'Total Value', header_style)

        worksheet[work].col(3).width = 256 * 20
        worksheet[work].col(4).width = 256 * 30
        worksheet[work].col(5).width = 256 * 20
        worksheet[work].col(6).width = 256 * 20
        worksheet[work].col(7).width = 256 * 20
        total_qty = 0
        total_cost = 0
        total_value = 0
        i = 7
        for line in lines:
            quantity=line.inventory_quantity_auto_apply if line.inventory_quantity_auto_apply >0 else 0
            worksheet[work].write(i, 3, line.product_id.default_code, text_center)
            worksheet[work].write(i, 4,  line.product_id.name, text_center)
            worksheet[work].write(i, 5,  line.inventory_quantity_auto_apply, text_center)
            worksheet[work].write(i, 6,  line.product_id.standard_price, text_center)
            worksheet[work].write(i, 7,  line.product_id.standard_price * line.inventory_quantity_auto_apply, text_center)
            total_qty += line.inventory_quantity_auto_apply
            total_cost += line.product_id.standard_price
            total_value += line.product_id.standard_price * line.inventory_quantity_auto_apply
            i = i + 1

        worksheet[work].write(i, 4, "Total", header_style)
        worksheet[work].write(i, 5,  "{:.3f}".format(total_qty), header_style)
        worksheet[work].write(i, 6,  "{:.3f}".format(total_cost), header_style)
        worksheet[work].write(i, 7,  "{:.3f}".format(total_value), header_style)

        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['stock.excel'].create(
            {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': 'Stock Report.xls'})

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=stock.excel&field=excel_file&download=true&id=%s&filename=Stock Report.xls' % (
                export_id.id),
            'target': 'new', }


class StockExcel(models.TransientModel):
    _name = "stock.excel"

    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('Excel Name', size=64)

