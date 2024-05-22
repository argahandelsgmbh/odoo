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
    pricelist_price = fields.Float("Pricelist Price")
    factor = fields.Float(related="categ_id.factor",string="Factor")
    price_update = fields.Boolean(string="Updated by Pricelist")

    @api.onchange('factor','categ_id','standard_price')
    def _onchange_categ_factor(self):
        for rec in self:
            if rec.factor:
                rec.list_price=rec.standard_price*rec.factor

class ProductCategories(models.Model):
    _inherit = 'product.category'

    factor = fields.Float("Factor")
