from odoo import api, fields, models
from datetime import datetime

class HelpdeskToRfq(models.TransientModel):
    _name = 'helpdesk.rfq.wizard'
    _description = 'Ticket to RFQ Wizard'

    name = fields.Char(string='Name')
    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
    select_po_rfq = fields.Selection([('rfq', 'RFQ'), ('po', 'PO')], string='Create', default='rfq')
    helpdesk_lines = fields.One2many('helpdesk.rfq.wizard.line', 'ticket_wizard_id')

    def create_rfq(self):
        if not self.ticket_id or not self.helpdesk_lines:
            return

        FiscalPosition = self.env['account.fiscal.position']
        purchase_obj = self.env['purchase.order']
        po_vals = []
        for vendor in self.vendor_id:
            payment_term = vendor.property_supplier_payment_term_id

            fpos = FiscalPosition.with_company(self.ticket_id.company_id)._get_fiscal_position(vendor)
            partner = vendor
            fiscal_position_id = fpos.id
            payment_term_id = payment_term.id,
            company_id = self.ticket_id.company_id.id
            currency_id = partner.currency_id.id
            origin = self.ticket_id.name
            date_order = fields.Datetime.now()

            # Create PO lines if necessary
            order_lines = []
            for line in self.helpdesk_lines:
                # Compute name
                product_lang = line.product_id.with_context(
                    lang=partner.lang,
                    partner_id=partner.id
                )
                name = product_lang.display_name
                if product_lang.description_purchase:
                    name += '\n' + product_lang.description_purchase

                product_qty = line.quantity
                price_unit = line.price_unit

                # Create PO line
                order_line_values = self._prepare_purchase_order_line(
                    name=name, product_id=line.product_id, product_qty=product_qty, price_unit=price_unit)
                order_lines.append((0, 0, order_line_values))
            po_vals += [{
                'partner_id': vendor.id,
                'fiscal_position_id': fiscal_position_id,
                'company_id': company_id,
                'currency_id': currency_id,
                'origin': origin,
                'ticket_id': self.ticket_id.id,
                'date_order': date_order,
                'order_line': order_lines
            }]
        new_po_ids = purchase_obj.create(po_vals)
        new_po_ids.name=new_po_ids.name+"/TS"
        if self.select_po_rfq == "po":
            new_po_ids.button_confirm()

        action = self.env.ref('purchase.purchase_rfq').sudo().read()[0]
        action['domain'] = [('id', 'in', new_po_ids.ids)]
        return action

    def _prepare_purchase_order_line(self, name, product_id, product_qty=0.0, price_unit=0.0):
        self.ensure_one()
        date_planned = datetime.now()
        return {
            'name': name,
            'product_id': product_id.id,
            'product_uom': product_id.uom_po_id.id,
            'product_qty': product_qty,
            'price_unit': price_unit,
            'date_planned': date_planned,
        }


class HelpdeskToRfqLine(models.TransientModel):
    _name = 'helpdesk.rfq.wizard.line'
    _description = 'Helpdesk Rfq Wizard Line'

    ticket_wizard_id = fields.Many2one('helpdesk.rfq.wizard')
    product_id = fields.Many2one('product.product')
    quantity = fields.Float()
    price_unit = fields.Float()

