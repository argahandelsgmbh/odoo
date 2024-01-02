import base64
import xlrd
import logging
from odoo import models, fields, api
_logger = logging.getLogger(__name__)

class ProductVarImport(models.Model):
    _name = 'pricelist.pricelist'
    _description = 'Import product pricelists'

    pricecode = fields.Char(string='Pricecode')
    cost = fields.Float(string='Cost')
    category = fields.Char(string='Category')
    imp = fields.Boolean(string='Imported')

    def action_import_products(self):
            count=0
            pcount=0
            for rec in self:
                pcount = pcount + 1
                if rec.pricecode:
                    products = self.env['product.template'].search([("default_code", 'ilike', rec.pricecode)])
                    for p in products:
                        count = count + 1
                        l = len(rec.pricecode)
                        if p.default_code[:l] == rec.pricecode or p.pricecode == rec.pricecode:
                            factor = self.env['product.category'].search([("name", '=',rec.category)],limit=1).factor
                            p.price_code = rec.pricecode
                            p.standard_price = rec.cost
                            p.list_price = rec.cost * factor if factor else 0
                            rec.imp=True

                            if count % 250==0:
                                _logger.info('Assigned %s price code to %s product', pcount, rec.pricecode)
                                self._cr.commit()
                                count = 0
            _logger.info('All done %s ', pcount)
