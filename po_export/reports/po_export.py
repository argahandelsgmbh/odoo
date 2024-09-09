from odoo import models
import string


class CustomerExport(models.AbstractModel):
    _name = 'report.po_export.xlsx_po_export'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format(
            {'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': '#d3dde3', 'color': 'black',
             'bottom': True, })
        format2 = workbook.add_format(
            {'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': '#edf4f7', 'color': 'black',
             'num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format(
            {'font_size': 11, 'align': 'vcenter', 'bg_color': '#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format5 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': False})

        sheet = workbook.add_worksheet("PO Export")
        customers = self.env['res.partner'].search([])
        print(lines)
        print(data)

        sheet.write(1, 0, 'Customer Code', format1)
        sheet.write(1, 1, 'Customer Reference', format1)
        sheet.write(1, 2, 'Internal Reference', format1)
        sheet.write(1, 3, 'Quantity', format1)
        sheet.write(1, 4, 'Customer Name', format1)
        sheet.write(1, 5, 'Purchase Order No', format1)
        sheet.set_column('A:A', 20)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 32)
        sheet.set_column('E:E', 20)
        sheet.set_column('F:F', 20)
        sheet.set_column('D:D', 15)
        sheet.set_column('G:G', 20)
        sheet.set_column('H:H', 15)

        i = 3
        for po in lines:
            sale_order = self.env['sale.order'].search([('name', '=', po.origin)])
            code=sale_order.name.split(" ")[0]
            for line in po.order_line:
                sheet.write(i, 0, sale_order.partner_id.company_registry or '', format5)
                sheet.write(i, 1, code or '', format5)
                sheet.write(i, 2, line.product_id.default_code or '', format5)
                sheet.write(i, 3, line.product_qty, format5)
                sheet.write(i, 4, sale_order.partner_id.name or '', format5)
                sheet.write(i, 5, po.name, format5)
                # if customer.category_id:
                #     sheet.write(i, 5, customer.category_id[0].name, format5)
                i = i + 1
