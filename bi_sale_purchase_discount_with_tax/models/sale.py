# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo.tools import float_is_zero, float_compare
import json


class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.depends('discount_amount', 'discount_method', 'discount_type')
    def _calculate_discount(self):
        res = 0.0
        discount = 0.0
        for self_obj in self:
            if self_obj.discount_method == 'fix':
                discount = self_obj.discount_amount
                res = discount
            elif self_obj.discount_method == 'per':
                discount = self_obj.amount_untaxed * (self_obj.discount_amount / 100)
                res = discount
            else:
                res = discount
        return res

    @api.depends('order_line', 'order_line.price_total', 'order_line.price_subtotal', \
                 'order_line.product_uom_qty', 'discount_amount', \
                 'discount_method', 'discount_type', 'order_line.discount_amount', \
                 'order_line.discount_method', 'order_line.discount_amt')
    def _amount_all(self):
        res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
        cur_obj = self.env['res.currency']
        for order in self:
            applied_discount = line_discount = sums = order_discount = amount_untaxed = amount_tax = amount_after_discount = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                applied_discount += line.discount_amt

                if line.discount_method == 'fix':
                    line_discount += line.discount_amount
                elif line.discount_method == 'per':
                    line_discount += line.price_subtotal * (line.discount_amount / 100)

            if res_config:
                if res_config.tax_discount_policy == 'tax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - line_discount,
                            'discount_amt_line': line_discount,
                        })

                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00

                        if order.discount_method == 'per':
                            order_discount = amount_untaxed * (order.discount_amount / 100)
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt': order_discount,
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax - order_discount,
                                'discount_amt': order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax,
                        })
                elif res_config.tax_discount_policy == 'untax':
                    if order.discount_type == 'line':
                        order.discount_amt = 0.00
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax - applied_discount,
                            'discount_amt_line': applied_discount,
                        })
                    elif order.discount_type == 'global':
                        order.discount_amt_line = 0.00
                        if order.discount_method == 'per':
                            order_discount = amount_untaxed * (order.discount_amount / 100)
                            if order.order_line:
                                for line in order.order_line:
                                    if line.tax_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = ((order.discount_amount * line.price_subtotal) / 100.0)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount
                                        taxes = line.tax_id.compute_all(discount, \
                                                                        order.currency_id, 1.0, product=line.product_id, \
                                                                        partner=order.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'tax_totals_json': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt': order_discount,
                            })
                        elif order.discount_method == 'fix':
                            order_discount = order.discount_amount
                            if order.order_line:
                                for line in order.order_line:
                                    if line.tax_id:
                                        final_discount = 0.0
                                        try:
                                            final_discount = (
                                                        (order.discount_amount * line.price_subtotal) / amount_untaxed)
                                        except ZeroDivisionError:
                                            pass
                                        discount = line.price_subtotal - final_discount

                                        taxes = line.tax_id.compute_all(discount, \
                                                                        order.currency_id, 1.0, product=line.product_id, \
                                                                        partner=order.partner_id)
                                        sums += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': sums,
                                'tax_totals_json': sums,
                                'amount_total': amount_untaxed + sums - order_discount,
                                'discount_amt': order_discount,
                            })
                        else:
                            order.update({
                                'amount_untaxed': amount_untaxed,
                                'amount_tax': amount_tax,
                                'amount_total': amount_untaxed + amount_tax,
                            })
                    else:
                        order.update({
                            'amount_untaxed': amount_untaxed,
                            'amount_tax': amount_tax,
                            'amount_total': amount_untaxed + amount_tax,
                        })
                else:
                    order.update({
                        'amount_untaxed': amount_untaxed,
                        'amount_tax': amount_tax,
                        'amount_total': amount_untaxed + amount_tax,
                    })
            else:
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax,
                })

    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Monetary(compute='_amount_all', string='Discount', store=True, readonly=True)
    discount_type = fields.Selection([('line', 'Order Line'), ('global', 'Global')], string='Discount Applies to',
                                     default='global')
    discount_amt_line = fields.Float(compute='_amount_all', string='Line Discount', digits='Line Discount', store=True, readonly=True)
    total_discount_line = fields.Float(compute='_compute_total_discount', string='Total with Discount', digits='Line Discount', store=True, readonly=True)

    @api.depends('order_line.discount_method', 'order_line.discount_amount', 'order_line.price_unit',
                 'order_line.product_uom_qty')
    def _compute_total_discount(self):
        disc = 0
        for rec in self.order_line:
            if rec.discount_method == 'fix':
                disc += (rec.price_unit * rec.product_uom_qty) - rec.discount_amount
            elif rec.discount_method == 'per':
                disc += (rec.price_unit * rec.product_uom_qty) - (
                            (rec.discount_amount / 100) * (rec.price_unit * rec.product_uom_qty))
        self.total_discount_line = disc

    def _prepare_invoice(self):
        res = super(sale_order, self)._prepare_invoice()
        res.update({'discount_method': self.discount_method,
                    'discount_amount': self.discount_amount,
                    'discount_amt': self.discount_amt,
                    'discount_type': self.discount_type,
                    'discount_amt_line': self.discount_amt_line,
                    'is_line': True, })
        return res

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed', 'discount_amount', \
                 'discount_method', 'discount_type', 'order_line.discount_amount', \
                 'order_line.discount_method', 'order_line.discount_amt', )
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            amount_untaxed = 0.0
            res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
            if res_config.tax_discount_policy == 'tax':
                price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                order = order_line.order_id
                return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                             product=order_line.product_id,
                                                             partner=order.partner_shipping_id)
            elif res_config.tax_discount_policy == 'untax':
                order = order_line.order_id
                if order.discount_type == 'line':
                    order.discount_amt = 0.00
                    for line in order.order_line:
                        amount_untaxed += line.price_subtotal
                    if order_line.discount_method == 'fix':
                        price_amount = order_line.price_subtotal - order_line.discount_amount
                        taxes = order_line.tax_id._origin.compute_all(price_amount, order_line.order_id.currency_id, 1,
                                                                      product=order_line.product_id,
                                                                      partner=order_line.order_id.partner_shipping_id)

                    elif order_line.discount_method == 'per':
                        price_amount = order_line.price_subtotal - (
                                    (order_line.discount_amount * order_line.price_subtotal) / 100.0)
                        taxes = order_line.tax_id._origin.compute_all(price_amount, order_line.order_id.currency_id, 1,
                                                                      product=order_line.product_id,
                                                                      partner=order_line.order_id.partner_shipping_id)
                    else:
                        price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                        order = order_line.order_id
                        taxes = order_line.tax_id._origin.compute_all(price, order.currency_id,
                                                                      order_line.product_uom_qty,
                                                                      product=order_line.product_id,
                                                                      partner=order.partner_shipping_id)
                    return taxes
                elif order.discount_type == 'global':
                    order.discount_amt_line = 0.00
                    if order.discount_method == 'per':
                        for line in order.order_line:
                            amount_untaxed += line.price_subtotal
                        order_discount = amount_untaxed * (order.discount_amount / 100)
                        if order_line.tax_id:
                            final_discount = 0.0
                            try:
                                final_discount = ((order.discount_amount * order_line.price_subtotal) / 100.0)
                            except ZeroDivisionError:
                                pass
                            discount = order_line.price_subtotal - final_discount
                            taxes = order_line.tax_id._origin.compute_all(discount, \
                                                                          order.currency_id, 1.0,
                                                                          product=order_line.product_id, \
                                                                          partner=order.partner_id)
                            return taxes
                        else:
                            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                            order = order_line.order_id
                            return order_line.tax_id._origin.compute_all(price, order.currency_id,
                                                                         order_line.product_uom_qty,
                                                                         product=order_line.product_id,
                                                                         partner=order.partner_shipping_id)


                    elif order.discount_method == 'fix':
                        order_discount = order.discount_amount
                        if order_line.tax_id:
                            for line in order.order_line:
                                amount_untaxed += line.price_subtotal
                            final_discount = 0.0
                            try:
                                final_discount = ((order.discount_amount * order_line.price_subtotal) / amount_untaxed)
                            except ZeroDivisionError:
                                pass
                            discount = order_line.price_subtotal - final_discount

                            taxes = order_line.tax_id._origin.compute_all(discount, \
                                                                          order.currency_id, 1.0,
                                                                          product=order_line.product_id, \
                                                                          partner=order.partner_id)
                            return taxes
                        else:
                            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                            order = order_line.order_id
                            return order_line.tax_id._origin.compute_all(price, order.currency_id,
                                                                         order_line.product_uom_qty,
                                                                         product=order_line.product_id,
                                                                         partner=order.partner_shipping_id)

                    else:
                        price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                        order = order_line.order_id
                        return order_line.tax_id._origin.compute_all(price, order.currency_id,
                                                                     order_line.product_uom_qty,
                                                                     product=order_line.product_id,
                                                                     partner=order.partner_shipping_id)
                else:
                    price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                    order = order_line.order_id
                    return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                                 product=order_line.product_id,
                                                                 partner=order.partner_shipping_id)
            else:
                price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
                order = order_line.order_id
                return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                             product=order_line.product_id,
                                                             partner=order.partner_shipping_id)

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line,
                                                                                         compute_taxes)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total,
                                                      order.amount_untaxed, order.currency_id)
            order.tax_totals_json = json.dumps(tax_totals)


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_method', 'discount_amount')
    def _compute_amount(self):
        for line in self:
            res_config = self.env['res.config.settings'].sudo().search([], order="id desc", limit=1)
            if res_config:
                if res_config.tax_discount_policy == 'untax':
                    if line.discount_type == 'line':
                        if line.discount_method == 'fix':
                            price = (line.price_unit * line.product_uom_qty) - line.discount_amount
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1,
                                                            product=line.product_id,
                                                            partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + line.discount_amount,
                                'price_subtotal': taxes['total_excluded'] + line.discount_amount,
                                'discount_amt': line.discount_amount,
                            })

                        elif line.discount_method == 'per':
                            price = (line.price_unit * line.product_uom_qty) * (
                                        1 - (line.discount_amount or 0.0) / 100.0)
                            price_x = ((line.price_unit * line.product_uom_qty) - (
                                        line.price_unit * line.product_uom_qty) * (
                                                   1 - (line.discount_amount or 0.0) / 100.0))
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, 1,
                                                            product=line.product_id,
                                                            partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'] + price_x,
                                'price_subtotal': taxes['total_excluded'] + price_x,
                                'discount_amt': price_x,
                            })
                        else:
                            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                            product=line.product_id,
                                                            partner=line.order_id.partner_shipping_id)
                            line.update({
                                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                                'price_total': taxes['total_included'],
                                'price_subtotal': taxes['total_excluded'],
                            })
                    else:
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                        product=line.product_id,
                                                        partner=line.order_id.partner_shipping_id)
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                elif res_config.tax_discount_policy == 'tax':
                    if line.discount_type == 'line':
                        price_x = 0.0
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                        product=line.product_id,
                                                        partner=line.order_id.partner_shipping_id)

                        if line.discount_method == 'fix':
                            price_x = (taxes['total_included']) - (taxes['total_included'] - line.discount_amount)
                        elif line.discount_method == 'per':
                            price_x = (taxes['total_included']) - (
                                        taxes['total_included'] * (1 - (line.discount_amount or 0.0) / 100.0))
                        else:
                            price_x = line.price_unit * (1 - (line.discount or 0.0) / 100.0)

                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                            'discount_amt': price_x,
                        })
                    else:
                        price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                        taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                        product=line.product_id,
                                                        partner=line.order_id.partner_shipping_id)
                        line.update({
                            'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                            'price_total': taxes['total_included'],
                            'price_subtotal': taxes['total_excluded'],
                        })
                else:
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                    product=line.product_id, partner=line.order_id.partner_shipping_id)

                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })
            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id, partner=line.order_id.partner_shipping_id)

                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

    is_apply_on_discount_amount = fields.Boolean("Tax Apply After Discount")
    discount_method = fields.Selection([('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    discount_type = fields.Selection(related='order_id.discount_type', string="Discount Applies to")
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float('Discount Final Amount')
    total_discount = fields.Float('Subtotal With Discount', compute='compute_total_discount')

    @api.depends('discount_method', 'discount_amount', 'price_unit', 'product_uom_qty')
    def compute_total_discount(self):
        for rec in self:
            disc = 0
            if rec.discount_method == 'fix':
                disc = (rec.price_unit*rec.product_uom_qty) - rec.discount_amount
            elif rec.discount_method == 'per':
                disc = (rec.price_unit*rec.product_uom_qty) - ((rec.discount_amount/100)*(rec.price_unit*rec.product_uom_qty))
            rec.total_discount = disc

    def _prepare_invoice_line(self, **optional_values):
        res = super(sale_order_line, self)._prepare_invoice_line(**optional_values)
        res.update({'discount': self.discount,
                    'discount_method': self.discount_method,
                    'discount_amount': self.discount_amount,
                    'discount_amt': self.discount_amt, })
        return res


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    tax_discount_policy = fields.Selection([('tax', 'Tax Amount'), ('untax', 'Untax Amount')],
                                           string='Discount Applies On', default='tax',
                                           default_model='sale.order')
    sale_account_id = fields.Many2one('account.account', 'Sale Discount Account',
                                      domain=[('user_type_id.name', '=', 'Expenses'), ('discount_account', '=', True)])
    purchase_account_id = fields.Many2one('account.account', 'Purchase Discount Account',
                                          domain=[('user_type_id.name', '=', 'Income'),
                                                  ('discount_account', '=', True)])

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        tax_discount_policy = ICPSudo.get_param('bi_sale_purchase_discount_with_tax.tax_discount_policy')
        sale_account_id = ICPSudo.get_param('bi_sale_purchase_discount_with_tax.sale_account_id')
        purchase_account_id = ICPSudo.get_param('bi_sale_purchase_discount_with_tax.purchase_account_id')
        res.update(tax_discount_policy=tax_discount_policy, sale_account_id=int(sale_account_id),
                   purchase_account_id=int(purchase_account_id), )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for rec in self:
            ICPSudo = rec.env['ir.config_parameter'].sudo()
            ICPSudo.set_param('bi_sale_purchase_discount_with_tax.sale_account_id', rec.sale_account_id.id)
            ICPSudo.set_param('bi_sale_purchase_discount_with_tax.purchase_account_id', rec.purchase_account_id.id)
            ICPSudo.set_param('bi_sale_purchase_discount_with_tax.tax_discount_policy', str(rec.tax_discount_policy))
