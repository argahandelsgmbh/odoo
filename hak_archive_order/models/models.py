
from odoo import  fields, models

class WebsiteInh(models.Model):
    _inherit= 'website'

    def _create_cart(self):
        sale_order_sudo = super()._create_cart()
        sale_order_sudo.active = False
        return sale_order_sudo


class SaleOrderInh(models.Model):
    _inherit= 'sale.order'

    active = fields.Boolean(string='Active', default=True)