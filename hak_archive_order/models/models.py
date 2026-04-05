
from odoo import  fields, models,api

class WebsiteInh(models.Model):
    _inherit= 'website'

    def _create_cart(self):
        sale_order_sudo = super()._create_cart()
        sale_order_sudo.active = False
        return sale_order_sudo


class SaleOrderInh(models.Model):
    _inherit= 'sale.order'

    active = fields.Boolean(string='Active', default=True)

    @api.model
    def create(self, val_list):
        for vals in val_list:
            if vals.get('name', '/') == '/':
                if vals.get('website_id'):
                    vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.website') or '/'
        return super().create(val_list)