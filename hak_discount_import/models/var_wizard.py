import base64
import xlrd
import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)


class DiscountInvoiceImport(models.TransientModel):
    _name = 'discount.invoice.import'

    file_upload = fields.Binary(string='Upload File')

    def action_import_products(self):
        wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.file_upload))
        for s in wb.sheets():
            first_row = []  # Header
            for col in range(s.ncols):
                first_row.append(s.cell_value(0, col))
            data = []
            for row in range(1, s.nrows):
                elm = {}
                for col in range(s.ncols):
                    elm[first_row[col]] = s.cell_value(row, col)
                data.append(elm)
            for rec in data:
                order = self.env['account.move.line'].search(
                    [('product_id', '=', rec.get('Product')), ('move_id.name', '=', rec.get('Order Reference')),
                     ('quantity', '=', rec.get('Quantity'))],limit=1)
                if order:
                    if not order.discount_fixed
                        order.discount_fixed = rec.get('Discount')

        return {'type': 'ir.actions.client', 'tag': 'reload'}


class ProductVarImport(models.TransientModel):
    _name = 'discount.import'

    file_upload = fields.Binary(string='Upload File')

    def action_import_products(self):
        wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.file_upload))
        for s in wb.sheets():
            first_row = []  # Header
            for col in range(s.ncols):
                first_row.append(s.cell_value(0, col))
            data = []
            for row in range(1, s.nrows):
                elm = {}
                for col in range(s.ncols):
                    elm[first_row[col]] = s.cell_value(row, col)
                data.append(elm)
            _logger.info(data)
            for rec in data:
                order = self.env['sale.order.line'].search([('product_id', '=', rec.get('Product')), ('order_id.name', '=', rec.get('Order Reference')), ('product_uom_qty', '=', rec.get('Quantity'))],limit=1)
                _logger.info(order)
                if order:
                    if not order.discount_fixed:
                        order.discount_fixed = rec.get('Discount')
                        _logger.info(rec.get('Discount'))

        return {'type': 'ir.actions.client', 'tag': 'reload'}
