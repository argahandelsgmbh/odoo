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
    not_imp = fields.Boolean(string='No Odoo Product')
    product_tmpl_id = fields.Many2one('product.template',string='Product Template')
    vendor_id = fields.Many2one('res.partner',string='Vendor')
    product_name = fields.Char(string='Product Name')

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
                        p.list_price = rec.cost * p.factor
                        if categ_id:
                            p.categ_id = categ_id.id
                            
                        # else:
                        #     if not p.list_price:
                        #         if rec.sales_price:
                        #             p.list_price = rec.sales_price
                        #         else:
                        #             p.list_price = rec.cost
                        rec.imp = True
                        _logger.info('Assigned %s price code to %s product', pcount, rec.pricecode)

                        vendor_pricelist = self.env['product.supplierinfo'].search([('product_tmpl_id', '=',p.id),('product_code', '=', rec.pricecode)],limit=1)

                        if vendor_pricelist:
                            vendor_pricelist = self.env['product.supplierinfo'].update({
                                "partner_id": rec.vendor_id.id,
                                "product_tmpl_id": p.id,
                                "product_name": rec.product_name,
                                "product_code": rec.pricecode,
                                "price": rec.cost
                            })
                        else:
                            vendor_pricelist=self.env['product.supplierinfo'].create({
                                                                                    "partner_id":rec.vendor_id.id,
                                                                                    "product_tmpl_id":p.id,
                                                                                    "product_name":rec.product_name,
                                                                                    "product_code":rec.pricecode,
                                                                                    "price":rec.cost
                                                                                  })
                    else:
                        _logger.info('No product found %s', rec.pricecode)

    def cron_import_products(self):
        count=0
        for rec in self.env['pricelist.pricelist'].search([("imp", '=', False),("not_imp",'=',False)],limit=200):
            if rec.pricecode and rec.imp == False:
                l = len(rec.pricecode)
                products = self.env['product.template'].search(['|',('price_code','=',rec.pricecode),('default_code','ilike',rec.pricecode)]).filtered(lambda o:o.default_code[:l] == rec.pricecode)
                if not products:
                    rec.not_imp=True
                for p in products:
                    p.price_update = False
                    if p.default_code[:l] == rec.pricecode or p.pricecode == rec.pricecode:
                        categ_id = self.env['product.category'].search([("name", '=', rec.category)], limit=1)
                        p.price_code = rec.pricecode
                        p.standard_price = rec.cost
                        rec.product_tmpl_id=p.id
                        p.list_price = (rec.cost * p.factor)
                        if categ_id:
                            p.categ_id = categ_id.id
                            
                        else:
                            if not p.list_price:
                                if rec.sales_price:
                                    p.list_price = rec.sales_price
                                else:
                                    p.list_price = rec.cost
                        rec.imp = True
                        p.price_update = True
                        count=count+1

                        vendor_pricelist = self.env['product.supplierinfo'].search(
                            [('product_tmpl_id', '=', p.id), ('product_code', '=', rec.pricecode)], limit=1)

                        if vendor_pricelist:
                            vendor_pricelist = self.env['product.supplierinfo'].update({
                                "partner_id": rec.vendor_id.id,
                                "product_tmpl_id": p.id,
                                "product_name": rec.product_name,
                                "product_code": rec.pricecode,
                                "price": rec.cost
                            })
                        else:
                            vendor_pricelist = self.env['product.supplierinfo'].create({
                                "partner_id": rec.vendor_id.id,
                                "product_tmpl_id": p.id,
                                "product_name": rec.product_name,
                                "product_code": rec.pricecode,
                                "price": rec.cost
                            })
                        _logger.info('Cron Assigned %s price code', rec.pricecode)
                        _logger.info('Count %s ', count)
                        self._cr.commit()
