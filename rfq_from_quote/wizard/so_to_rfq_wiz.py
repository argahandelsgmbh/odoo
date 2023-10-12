from odoo import api, fields, models
from datetime import datetime


class SaleQuoteToRfq(models.TransientModel):
    _name = 'quote.rfq.wizard'
    _description = 'Quotation to RFQ Wizard'

    name = fields.Char(string='Name')
    sale_id = fields.Many2one('sale.order', string='Quotation/Sale order')
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain="[('supplier_rank', '>', 0)]")
    vendor_ids = fields.Many2many('res.partner', string='Vendors', domain="[('supplier_rank', '>', 0)]")
    sale_line_ids = fields.Many2many('sale.order.line', string='Products')
    select_po_rfq = fields.Selection([('rfq', 'RFQ'), ('po', 'PO')], string='Create', default='rfq')

    def create_rfq(self):
        if not self.sale_id or not self.sale_line_ids:
            return

        FiscalPosition = self.env['account.fiscal.position']
        purchase_obj = self.env['purchase.order']
        # po_vals = []
        for vendor in self.vendor_ids:
            po_vals = []
            payment_term = vendor.property_supplier_payment_term_id

            fpos = FiscalPosition.with_company(self.sale_id.company_id).get_fiscal_position(vendor.id)
            partner = vendor
            fiscal_position_id = fpos.id
            payment_term_id = payment_term.id,
            company_id = self.sale_id.company_id.id
            currency_id = partner.currency_id.id
            origin = self.sale_id.name
            # notes = self.sale_id.description
            date_order = fields.Datetime.now()

            # Create PO lines if necessary
            order_lines = []
            for line in self.sale_line_ids:
                if vendor.id in line.product_id.seller_ids.mapped('name.id'):

                    product_lang = line.product_id.with_context(
                        lang=partner.lang,
                        partner_id=partner.id
                    )
                    name = product_lang.display_name
                    if product_lang.description_purchase:
                        name += '\n' + product_lang.description_purchase


                    taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(
                        lambda tax: tax.company_id == self.sale_id.company_id)).ids


                    if line.product_uom != line.product_id.uom_po_id:
                        product_qty = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_po_id)
                        price_unit = line.product_uom._compute_price(line.price_unit, line.product_id.uom_po_id)
                    else:
                        product_qty = line.product_uom_qty
                        price_unit = line.price_unit

                    # Create PO line
                    order_line_values = self._prepare_purchase_order_line(
                        name=name, product_id=line.product_id, product_qty=product_qty, price_unit=price_unit,
                        taxes_ids=taxes_ids)
                    # order_line_values['sale_line_ids'] = [(4, line.id, 0)]
                    line.product_status = 'po'
                    order_lines.append((0, 0, order_line_values))
            po_vals += [{
                'partner_id': vendor.id,
                'fiscal_position_id': fiscal_position_id,
                # 'payment_term_id': payment_term_id or False,
                'company_id': company_id,
                'currency_id': currency_id,
                'origin': origin,

                # 'notes': notes,
                'date_order': date_order,
                'order_line': order_lines
            }]
            new_po_ids = purchase_obj.create(po_vals)
            # order_lines = []
            if self.select_po_rfq == "po":
                new_po_ids.button_confirm()
            # action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
            # action['domain'] = [('id', 'in', new_po_ids.ids)]
        self.sale_id.is_po_created = True
            # return action

    def _prepare_purchase_order_line(self, name, product_id, product_qty=0.0, price_unit=0.0, taxes_ids=False):
        self.ensure_one()
        date_planned = datetime.now()
        return {
            'name': name,
            'product_id': product_id.id,
            'product_uom': product_id.uom_po_id.id,
            'product_qty': product_qty,
            'price_unit': price_unit,
            'taxes_id': [(6, 0, taxes_ids)],
            'date_planned': date_planned,
            # 'account_analytic_id': self.account_analytic_id.id,
            # 'analytic_tag_ids': self.analytic_tag_ids.ids,
        }
