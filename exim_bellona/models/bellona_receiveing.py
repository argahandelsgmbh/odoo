from odoo import fields, models
from odoo.exceptions import UserError


class BellonaReceive(models.Model):
    _name = 'bellona.receiving'
    scription = "Bellona Receiving"

    name = fields.Char()
    invoice = fields.Char()
    packet_no = fields.Char()
    internal_ref = fields.Char("Product Code")
    product_name = fields.Char("Product Name")
    satinalma_siparis_no = fields.Char()
    dosya_numarasi = fields.Char()
    bdt = fields.Char(string="BDT için Mlz. Tnm İn")

    gtip = fields.Char()
    quantity = fields.Float()
    musteri_referans = fields.Char('Customer Reference')
    po_no = fields.Char('Purchase Order')
    fob_brfiyat = fields.Float("Unit Price")
    fob_tutar = fields.Char()
    doviz_cinsi = fields.Char("Currency")
    hacim = fields.Float()
    hacim_birimi = fields.Char()
    dosya_tarihi = fields.Date()
    fatura_tarihi = fields.Date("Invoice Date")
    net_agirlik = fields.Float()
    brut_agirlik = fields.Float()
    ihracat_kap_adeti= fields.Float()
    purchase_id = fields.Many2one('purchase.order')
    picking_id = fields.Many2one('stock.picking', copy=False)
    is_received = fields.Boolean(copy=False)

    def action_receive(self):
        self.purchase_id = self.env['purchase.order'].search([("name", '=', self.po_no)], limit=1)
        if self.is_received:
            raise UserError('Already Received.')
        if self.purchase_id.state != 'purchase':
            raise UserError('Purchase Order is not in Done state.')
        if self.purchase_id.state == 'purchase' and not self.is_received:
            lines = self.purchase_id.order_line.filtered(lambda i: i.product_id.default_code == self.internal_ref)
            if lines:
                if not self.picking_id:
                    pick = lines.move_ids.filtered(
                        lambda h: h.product_id.default_code == self.internal_ref).picking_id.ids
                    pick_id = pick[-2] if len(pick) > 1 else pick[0]
                    # self.picking_id = pick_id
                    if self.picking_id.state == 'done':
                        self.picking_id = pick_id
                        self.is_received = True
                for move in lines.move_ids:
                    if move.state not in ['done', 'cancel']:
                        move.quantity_done = self.quantity
                # if self.purchase_id.name == 'BNR*85 * 00013':
                #     print('hhh')
                if len(lines.move_ids) > 1:
                    action_data = lines.move_ids.filtered(
                        lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                        skip_backorder=False).button_validate()
                    # print(action_data)
                    backorder_wizard = self.env['stock.backorder.confirmation'].with_context(action_data['context'])
                    backorder_wizard.process()
                    if not self.picking_id:
                        pick = lines.move_ids.filtered(
                            lambda h: h.product_id.default_code == self.internal_ref).picking_id.ids
                        pick_id = pick[-2] if len(pick) > 1 else pick[0]
                        stock_picking = self.env['stock.picking'].browse([pick_id])

                        if stock_picking.state == 'done':
                            self.picking_id = pick_id
                            self.is_received = True
                    # self.is_received = True
                else:
                    action_data = lines.move_ids.filtered(
                        lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                        skip_backorder=False).button_validate()
                    if 'context' in str(action_data):
                        backorder_wizard = self.env['stock.backorder.confirmation'].with_context(action_data['context'])
                        backorder_wizard.process()
                    if not self.picking_id:
                        pick = lines.move_ids.filtered(
                            lambda h: h.product_id.default_code == self.internal_ref).picking_id.ids
                        pick_id = pick[-2] if len(pick) > 1 else pick[0]
                        stock_picking = self.env['stock.picking'].browse([pick_id])

                        if stock_picking.state == 'done':
                            self.picking_id = pick_id
                            self.is_received = True

    def receive_all_products(self):
        for rec in self:
            rec.purchase_id = self.env['purchase.order'].search([("name", '=', rec.po_no)], limit=1)
            if rec.purchase_id.state == 'purchase' and not rec.is_received:
                lines = rec.purchase_id.order_line.filtered(lambda i: i.product_id.default_code == rec.internal_ref)
                if lines:
                    if not rec.picking_id:
                        pick = lines.move_ids.filtered(
                            lambda h: h.product_id.default_code == rec.internal_ref).picking_id.ids
                        pick_id = pick[-2] if len(pick) > 1 else pick[0]
                        if rec.picking_id.state == 'done':
                            rec.picking_id = pick_id
                            rec.is_received = True
                    for move in lines.move_ids:
                        if move.state not in ['done', 'cancel']:
                            move.quantity_done = rec.quantity
                    if len(lines.move_ids) > 1:
                        action_data = lines.move_ids.filtered(
                            lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                            skip_backorder=False).button_validate()
                        backorder_wizard = self.env['stock.backorder.confirmation'].with_context(action_data['context'])
                        backorder_wizard.process()
                        if not rec.picking_id:
                            pick = lines.move_ids.filtered(
                                lambda h: h.product_id.default_code == rec.internal_ref).picking_id.ids
                            pick_id = pick[-2] if len(pick) > 1 else pick[0]
                            stock_picking = self.env['stock.picking'].browse([pick_id])
                            if stock_picking.state == 'done':
                                rec.picking_id = pick_id
                                rec.is_received = True
                    else:
                        action_data = lines.move_ids.filtered(
                            lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                            skip_backorder=False).button_validate()
                        if 'context' in str(action_data):
                            backorder_wizard = self.env['stock.backorder.confirmation'].with_context(action_data['context'])
                            backorder_wizard.process()
                        if not rec.picking_id:
                            pick = lines.move_ids.filtered(
                                lambda h: h.product_id.default_code == rec.internal_ref).picking_id.ids
                            pick_id = pick[-2] if len(pick) > 1 else pick[0]
                            stock_picking = self.env['stock.picking'].browse([pick_id])
                            if stock_picking.state == 'done':
                                rec.picking_id = pick_id
                                rec.is_received = True
