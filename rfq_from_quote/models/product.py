from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    purchase_method = fields.Selection([
        ('purchase', 'On ordered quantities'),
        ('receive', 'On received quantities'),
    ], string="Control Policy", help="On ordered quantities: Control bills based on ordered quantities.\n"
                                     "On received quantities: Control bills based on received quantities.",
        default="purchase")
