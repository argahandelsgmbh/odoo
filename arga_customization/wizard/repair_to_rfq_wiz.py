from odoo import api, fields, models
from datetime import datetime


class SaleQuoteToRfq(models.TransientModel):
    _name = 'repair.rfq.wizard'
    _description = 'Quotation to RFQ Wizard'

    name = fields.Char(string='Name')
    repair_id = fields.Many2one('repair.order', string='Repair')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    repair_line_ids = fields.Many2many('repair.line', string='Products')
    select_po_rfq = fields.Selection([('rfq', 'RFQ'), ('po', 'PO')], string='Create', default='rfq')

    def create_rfq(self):
        if not self.repair_id or not self.repair_line_ids:
            return

        FiscalPosition = self.env['account.fiscal.position']
        purchase_obj = self.env['purchase.order']
        po_vals = []
        for vendor in self.vendor_id:
            payment_term = vendor.property_supplier_payment_term_id

            fpos = FiscalPosition.with_company(self.repair_id.company_id).get_fiscal_position(vendor.id)
            partner = vendor
            fiscal_position_id = fpos.id
            payment_term_id = payment_term.id,
            company_id = self.repair_id.company_id.id
            currency_id = partner.currency_id.id
            origin = self.repair_id.name
            # notes = self.sale_id.description
            date_order = fields.Datetime.now()

            # Create PO lines if necessary
            order_lines = []
            for line in self.repair_line_ids:
                # Compute name
                product_lang = line.product_id.with_context(
                    lang=partner.lang,
                    partner_id=partner.id
                )
                name = product_lang.display_name
                if product_lang.description_purchase:
                    name += '\n' + product_lang.description_purchase

                # Compute taxes
                taxes_ids = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(
                    lambda tax: tax.company_id == self.repair_id.company_id)).ids

                # Compute quantity and price_unit
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
                order_lines.append((0, 0, order_line_values))
            po_vals += [{
                'partner_id': vendor.id,
                'fiscal_position_id': fiscal_position_id,
                # 'payment_term_id': payment_term_id or False,
                'company_id': company_id,
                'currency_id': currency_id,
                'origin': origin,
                'repair_order_id': self.repair_id.id,

                # 'notes': notes,
                'date_order': date_order,
                'order_line': order_lines
            }]
        new_po_ids = purchase_obj.create(po_vals)
        if self.select_po_rfq == "po":
            new_po_ids.button_confirm()
        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        action['domain'] = [('id', 'in', new_po_ids.ids)]
        # self.repair_id.is_po_created = True
        return action

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
