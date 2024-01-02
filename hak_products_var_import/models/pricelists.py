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
        pcount = 0
        for rec in self.env['pricelist.pricelist'].search([("id", 'in',self.env.context.get('active_ids'))]):
            pcount = pcount + 1
            if rec.pricecode:
                l = len(rec.pricecode)
                products = self.env['product.template'].search([("price_code", '=', rec.pricecode)])
                for p in products:
                    if p.default_code[:l] == rec.pricecode or p.pricecode == rec.pricecode:
                        factor = self.env['product.category'].search([("name", '=', rec.category)], limit=1).factor
                        p.price_code = rec.pricecode
                        p.standard_price = rec.cost
                        p.list_price = rec.cost * factor if factor else 0
                        rec.imp = True
                        _logger.info('Assigned %s price code to %s product', pcount, rec.pricecode)
                    else:
                        _logger.info('No product found %s', rec.pricecode)

    def cron_import_products(self):
        for rec in self.env['pricelist.pricelist'].search([("imp", '=', False)], order='id DESC'):
            if rec.pricecode and rec.imp == False:
                l = len(rec.pricecode)
                products = self.env['product.template'].search(['|',('price_code','=',rec.pricecode),('default_code','!=',False)]).filtered(lambda o:o.default_code[:l] == rec.pricecode)
                for p in products:
                    if p.default_code[:l] == rec.pricecode or p.pricecode == rec.pricecode:
                        factor = self.env['product.category'].search([("name", '=', rec.category)], limit=1).factor
                        p.price_code = rec.pricecode
                        p.standard_price = rec.cost
                        p.list_price = rec.cost * factor if factor else 0
                        rec.imp = True
