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
    sales_price = fields.Float(string='Sales Price')
    category = fields.Char(string='Category')
    imp = fields.Boolean(string='Imported')
    product_tmpl_id = fields.Many2one('product.template',string='Product Template')
    

    def action_import_products(self):
        pcount = 0
        for rec in self.env['pricelist.pricelist'].search([("id", 'in',self.env.context.get('active_ids')),("imp", '=', False)]):
            pcount = pcount + 1
            if rec.pricecode and rec.imp==False:
                l = len(rec.pricecode)
                products = self.env['product.template'].search(['|',('price_code','=',rec.pricecode),('default_code','ilike',rec.pricecode)]).filtered(lambda o:o.default_code[:l] == rec.pricecode)
                for p in products:
                    if p.default_code[:l] == rec.pricecode or p.pricecode == rec.pricecode:
                        categ_id = self.env['product.category'].search([("name", '=', rec.category)], limit=1)
                        p.price_code = rec.pricecode
                        p.standard_price = rec.cost
                        rec.product_tmpl_id=p.id
                        if categ_id:
                            p.categ_id = categ_id.id
                            p.list_price = rec.cost * categ_id.factor
                        else:
                            if not p.list_price:
                                if rec.sales_price:
                                    p.list_price = rec.sales_price
                                else:
                                    p.list_price = rec.cost
                            
                        rec.imp = True
                        _logger.info('Assigned %s price code to %s product', pcount, rec.pricecode)
                    else:
                        _logger.info('No product found %s', rec.pricecode)

    def cron_import_products(self):
        for rec in self.env['pricelist.pricelist'].search([("imp", '=', False)]):
            if rec.pricecode and rec.imp == False:
                l = len(rec.pricecode)
                products = self.env['product.template'].search([('default_code','!=',False)]).filtered(lambda o:o.default_code[:l] == rec.pricecode)
                for p in products:
                    if p.default_code[:l] == rec.pricecode or p.pricecode == rec.pricecode:
                        categ_id = self.env['product.category'].search([("name", '=', rec.category)], limit=1)
                        p.price_code = rec.pricecode
                        p.standard_price = rec.cost
                        rec.product_tmpl_id=p.id
                        if categ_id:
                            p.categ_id = categ_id.id
                            p.list_price = rec.cost * categ_id.factor
                        else:
                            if not p.list_price:
                                if rec.sales_price:
                                    p.list_price = rec.sales_price
                                else:
                                    p.list_price = rec.cost
                        rec.imp = True
                        _logger.info('Cron Assigned %s price code', rec.pricecode)
                        self._cr.commit()
