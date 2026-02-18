# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlwt
from io import BytesIO
import base64
from xlwt import easyxf

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def generate_report(self):
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
        text_center_bold = easyxf(
            'font:height 200; align: horiz center;font:bold True;' "borders: top thin,bottom thin")
        text_right = easyxf('font:height 200; align: horiz right;' "borders: top thin,bottom thin",
                            num_format_str='0.00')

        workbook = xlwt.Workbook()
        worksheet = []
        for l in range(0, 1):
            worksheet.append(l)

        work = 0
        worksheet[work] = workbook.add_sheet('PO Export')

        worksheet[work].col(0).width = 256 * 15
        worksheet[work].col(1).width = 256 * 20
        worksheet[work].col(2).width = 256 * 20
        worksheet[work].col(3).width = 256 * 40
        worksheet[work].col(4).width = 256 * 20
        worksheet[work].col(5).width = 256 * 20
        worksheet[work].col(6).width = 256 * 20
        worksheet[work].col(7).width = 256 * 20
        worksheet[work].col(8).width = 256 * 20
        worksheet[work].col(9).width = 256 * 20

        worksheet[work].write(0, 0, 'Customer Code', header_style)
        # worksheet[work].write_merge(7, 7, 1, 4, date_from + " TO " + date_to, header_style)
        worksheet[work].write(0, 1, 'Customer Reference', header_style)
        worksheet[work].write(0, 2, 'Internal Reference', header_style)
        worksheet[work].write(0, 3, 'Quantity', header_style)
        worksheet[work].write(0, 4, 'Customer Name', header_style)
        worksheet[work].write(0, 5, 'Purchase Order No', header_style)

        i = 1
        for po in self:
            sale_order = self.env['sale.order'].search([('name', '=', po.origin)], limit=1)
            code = sale_order.name.split(" ")[0] if sale_order else ""
            for line in po.order_line:
                worksheet[work].write(i, 0, sale_order.partner_id.company_registry or "", text_center)
                worksheet[work].write(i, 1, code or '', text_center)
                worksheet[work].write(i, 2, line.product_id.default_code or '', text_center)
                worksheet[work].write(i, 3, line.product_qty, text_center)
                worksheet[work].write(i, 4, sale_order.partner_id.name or '', text_center)
                worksheet[work].write(i, 5, po.name, text_center)
                i = i + 1
        fp = BytesIO()
        workbook.save(fp)
        export_id = self.env['purchase.excel'].create(
            {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': 'PO Export.xls'})

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=purchase.excel&field=excel_file&download=true&id=%s&filename=PO Export.xls' % (
                export_id.id),
            'target': 'new', }



class PurchaseExcel(models.TransientModel):
    _name = "purchase.excel"
    _description = "purchase.excel"

    excel_file = fields.Binary('Excel File')
    file_name = fields.Char('Excel Name', size=64)

