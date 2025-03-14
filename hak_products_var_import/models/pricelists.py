import base64
import xlrd
import logging
from odoo import models, fields, api

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

    internal_reference = fields.Char(string="Internal Reference")
    product_model_name = fields.Char(string="Product Model Name")
    check_code = fields.Char(string="Check Code")
    pricelist_price = fields.Float(string="Pricelist Price")
    compare_to_price = fields.Float(string="Compare to Price?")
    sale_tax = fields.Char(string="Sale Tax")
    so_delivery_time_days = fields.Integer(string="SO Delivery Time (Days)")
    vendor_delivery_lead_time = fields.Integer(string="Vendor Delivery Lead Time (Days)")
    vendor_tax = fields.Char(string="Vendor Tax")
    factor = fields.Float(string="Factor")
    vendor_price = fields.Float(string="Vendor Price")


    def action_import_products(self):
        pcount = 0
        for rec in self.env['pricelist.pricelist'].search([]):
            pcount = pcount + 1
            if rec.pricecode or rec.internal_reference:
                l = len(rec.pricecode)
                products = self.env['product.template'].search(['|',('price_code','=',rec.pricecode),('default_code','=',rec.internal_reference)])
                for p in products:
                    if p.default_code[:l] == rec.pricecode or p.price_code == rec.pricecode or p.default_code== rec.internal_reference:
                        categ_id = self.env['product.category'].search([("name", '=', rec.category)], limit=1)

                        vals={
                            "price_code":rec.pricecode,
                            "standard_price":rec.cost,
                            "product_model_name":rec.product_model_name,
                            "list_price":p.list_price if p.list_price >1 else rec.sales_price,
                            "compare_price":rec.sales_price,
                            "pricelist_price":rec.cost*(rec.factor+1),
                        }
                        p.write(vals)
                        rec.product_tmpl_id=p.id
                        if categ_id:
                            p.categ_id = categ_id.id

                        vendor_pricelist = self.env['product.supplierinfo'].search([('product_tmpl_id', '=',p.id),('product_code', '=', rec.pricecode)],limit=1)

                        if vendor_pricelist:
                            vendor_pricelist = self.env['product.supplierinfo'].write({
                                "partner_id": rec.vendor_id.id,
                                "product_tmpl_id": p.id,
                                "product_name": rec.product_name,
                                "product_code": rec.pricecode,
                                "price": rec.vendor_price,
                                "delay": rec.vendor_delivery_lead_time
                            })
                        else:
                            vendor_pricelist=self.env['product.supplierinfo'].create({
                                                                                    "partner_id":rec.vendor_id.id,
                                                                                    "product_tmpl_id":p.id,
                                                                                    "product_name":rec.product_name,
                                                                                    "product_code":rec.pricecode,
                                                                                    "price":rec.vendor_price,
                                                                                    "delay":rec.vendor_delivery_lead_time,
                                                                                    "company_id":False
                                                                                  })

                    else:
                        _logger.info('No product found %s', rec.pricecode)
                    self.env.cr.commit()
    def cron_import_products(self):
        pass
        # count=0
        # for rec in self.env['pricelist.pricelist'].search([("imp", '=', False),("not_imp",'=',False)],limit=200):
        #     if rec.pricecode and rec.imp == False:
        #         l = len(rec.pricecode)
        #         products = self.env['product.template'].search(['|',('price_code','=',rec.pricecode),('default_code','ilike',rec.pricecode)]).filtered(lambda o:o.default_code[:l] == rec.pricecode)
        #         if not products:
        #             rec.not_imp=True
        #         for p in products:
        #             p.price_update = False
        #             if p.default_code[:l] == rec.pricecode or p.price_code == rec.pricecode:
        #                 categ_id = self.env['product.category'].search([("name", '=', rec.category)], limit=1)
        #                 p.price_code = rec.pricecode
        #                 p.standard_price = rec.cost
        #                 rec.product_tmpl_id=p.id
        #                 p.list_price = rec.sales_price if rec.sales_price else rec.cost * p.factor 
        #                 if categ_id:
        #                     p.categ_id = categ_id.id
                            
        #                 else:
        #                     if not p.list_price:
        #                         if rec.sales_price:
        #                             p.list_price = rec.sales_price
        #                         else:
        #                             p.list_price = rec.cost
        #                 rec.imp = True
        #                 p.price_update = True
        #                 count=count+1

        #                 vendor_pricelist = self.env['product.supplierinfo'].search(
        #                     [('product_tmpl_id', '=', p.id), ('product_code', '=', rec.pricecode)], limit=1)

        #                 if vendor_pricelist:
        #                     vendor_pricelist = self.env['product.supplierinfo'].update({
        #                         "partner_id": rec.vendor_id.id,
        #                         "product_tmpl_id": p.id,
        #                         "product_name": rec.product_name,
        #                         "product_code": rec.pricecode,
        #                         "price": rec.cost
        #                     })
        #                 else:
        #                     vendor_pricelist = self.env['product.supplierinfo'].create({
        #                         "partner_id": rec.vendor_id.id,
        #                         "product_tmpl_id": p.id,
        #                         "product_name": rec.product_name,
        #                         "product_code": rec.pricecode,
        #                         "price": rec.cost
        #                     })
        #                 self._cr.commit()
