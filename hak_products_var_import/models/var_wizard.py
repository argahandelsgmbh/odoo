import base64
import xlrd
import logging
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

_logger = logging.getLogger(__name__)


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'

    price_code = fields.Char()
    pricelist_price = fields.Char("Pricelist Price")
    factor = fields.Float(related="categ_id.factor",string="Factor")
    price_update = fields.Boolean(string="Updated by Pricelist",readonly=True)

    @api.onchange('factor','categ_id','standard_price')
    def _onchange_categ_factor(self):
        for rec in self:
            if rec.factor:
                rec.list_price=rec.standard_price*rec.factor


class ProductVarImport(models.TransientModel):
    _name = 'product.var.import'
    _description = 'Import products'

    file_upload = fields.Binary(string='Upload File')

    def action_import_products(self):
        wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.file_upload))
        pcount = 0
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
            _logger.info('Length %s', len(data))
            count = 0
            for rec in data:
                if rec.get('pricecode'):
                    _logger.info('Pricecode %s ', rec.get('pricecode'))
                    products = self.env['product.template'].search(
                        [("default_code", 'ilike', rec.get('pricecode')), ("standard_price", '=', False)])
                    for p in products:
                        l = len(rec.get('pricecode'))
                        if p.default_code[:l] == rec.get('pricecode'):
                            factor = self.env['product.category'].search([("name", '=', rec.get('category'))],
                                                                         limit=1).factor

                            p.price_code = rec.get('pricecode')
                            p.standard_price = rec.get('cost')
                            p.list_price = rec.get('cost') * (factor or 1)
                            count = count + 1
                            pcount = pcount + 1
                            if count == 250:
                                _logger.info('Assigned %s price code to %s product', pcount, rec.get('pricecode'))
                                self._cr.commit()
                                count = 0
            _logger.info('All done %s ', pcount)
            return {'type': 'ir.actions.client', 'tag': 'reload'}


class ProductCategories(models.Model):
    _inherit = 'product.category'

    factor = fields.Float("Factor")
