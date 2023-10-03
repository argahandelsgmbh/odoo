import base64
from io import BytesIO

import qrcode

from odoo import fields, models


class IstikbalLogNotes(models.Model):
    _name = 'istikbal.combine.shipments'
    _description = "Combine Shipments"
    _rec_name = 'truckPlate'

    disPactDate = fields.Char('disPactDate')
    containerNumber = fields.Char('Container Number')
    truckPlate = fields.Char('Truck Plate')
    truckPlate2 = fields.Char('Truck Plate 2')
    shipmentDate = fields.Char('Shipment Date')
    invoiceNumber = fields.Char('Invoice Number')
    name = fields.Char('Shipment Number')
    volum = fields.Float('volum')
    voleh = fields.Float('voleh')
    detail_ids = fields.One2many('istikbal.shipments.details', 'combine_id', string='Shipment Details')
    company_id = fields.Many2one('res.company', string='Company')
    shipment_ids = fields.One2many('istikbal.shipments.header', 'combine_id')

    total_lines = fields.Integer(compute='compute_line')
    total_value = fields.Integer(compute='compute_line')
    is_all_received = fields.Boolean()

    def action_receive_po(self):
        try:
            purchase_order = self.detail_ids.filtered(lambda r: not r.is_received).mapped('purchase_id')
            for po in purchase_order:
                if po.state == 'purchase':
                    products_codes = self.detail_ids.filtered(lambda j: j.purchase_id.id == po.id and not j.is_received).mapped(
                        'productCode')
                    lines = po.order_line.filtered(lambda i: i.product_id.default_code in products_codes)
                    if lines:
                        print(po.name)
                        for move in lines.move_ids:
                            if move.state not in ['done', 'cancel']:
                                qty = self.detail_ids.filtered(lambda k:k.purchase_id.id == po.id and k.productCode == move.product_id.default_code and not k.is_received).quantity
                                move.quantity_done = qty
                        if len(lines.move_ids) > 1:
                            action_data = lines.move_ids.filtered(
                                lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                                skip_backorder=False).button_validate()
                            if 'context' in str(action_data):
                                backorder_wizard = self.env['stock.backorder.confirmation'].with_context(
                                    action_data['context'])
                                backorder_wizard.process()
                        else:
                            action_data = lines.move_ids.filtered(
                                lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                                skip_backorder=False).button_validate()
                            if 'context' in str(action_data):
                                backorder_wizard = self.env['stock.backorder.confirmation'].with_context(
                                    action_data['context'])
                                backorder_wizard.process()
                        for r in self.detail_ids:
                            if not r.is_received and not r.picking_id:
                                # stml = self.env['stock.move.line'].search([('picking_id.purchase_id.name','=', r.purchase_id.name)],limit=1)
                                # r.picking_id = stml.picking_id.id
                                # if r.picking_id.state == 'done':
                                #     r.is_received = True

                                pick = self.env['stock.move.line'].search([('picking_id.purchase_id.name', '=', r.purchase_id.name)], order='id asc').picking_id.ids
                                if pick:
                                    pick_id = pick[-2] if len(pick) > 1 else pick[0]
                                    stock_picking = self.env['stock.picking'].browse([pick_id])
    
                                    if stock_picking.state == 'done':
                                        r.picking_id = stock_picking.id
                                        r.is_received = True
                    self.env.cr.commit()
        except Exception as e:
            raise Warning(str(e))


    def compute_line(self):
        self.total_lines = len(self.detail_ids)
        self.total_value = sum(self.detail_ids.mapped('subtotal'))
        self.is_all_received = True if all([x.is_received for x in self.detail_ids]) else False

    def cron_merger_of_header(self):
        self.merge_header()
        return

    def merge_header(self):
        recs = self.env['istikbal.shipments.header'].search([])
        combine_obj = self.env['istikbal.combine.shipments']
        for rec in recs:
            combine_rec = self.search([('truckPlate', '=', rec.truckPlate), ('shipmentDate', '=', rec.shipmentDate),
                                       ('company_id', '=', rec.company_id.id)], limit=1)
            if combine_rec.id == 935:
                print('acc')
            if combine_rec:
                rec.detail_ids.write({'combine_id': combine_rec.id})
                rec.combine_id = combine_rec

            else:
                combine_rec = combine_obj.create({'disPactDate': rec.disPactDate,
                                                  'containerNumber': rec.containerNumber,
                                                  'truckPlate': rec.truckPlate,
                                                  'truckPlate2': rec.truckPlate2,
                                                  'shipmentDate': rec.shipmentDate,
                                                  'invoiceNumber': rec.invoiceNumber,
                                                  # 'name': rec.name,
                                                  'volum': rec.volum,
                                                  'voleh': rec.voleh,
                                                  'company_id': rec.company_id.id,
                                                  })


                found = False
                val = combine_rec.id
                existing_val = False
                while not found and combine_obj.search([('id', '!=', val), ('company_id', '=', rec.company_id.id)]):
                    val -= 1
                    combine_exist = combine_obj.search([('id', '=', val), ('company_id', '=', rec.company_id.id)])
                    if combine_exist and combine_exist.name:
                        found = True
                        existing_val = combine_exist.id

                if found:
                    if existing_val:
                        existing_obj = combine_obj.browse([existing_val])
                        if existing_obj.truckPlate == combine_rec.truckPlate:
                            combine_rec.truckPlate = existing_obj.truckPlate
                            combine_rec.name = str(combine_rec.create_date.year).split('0')[1] + '-' + str(
                                (int(existing_obj.name.split('-')[1]) + 1))
                        else:
                            # if existing_obj.name:
                            combine_rec.name = str(combine_rec.create_date.year).split('0')[1] + '-' + str((int(existing_obj.name.split('-')[1]) + 1))
                            # else:
                            #     # existing_val = 1
                            #     combine_rec.name = str(combine_rec.create_date.year).split('0')[1] + '-' + str(
                            #         existing_val)
                else:
                    existing_val = 1
                    combine_rec.name = str(combine_rec.create_date.year).split('0')[1] + '-' + str(existing_val)
                rec.detail_ids.write({'combine_id': combine_rec.id})
                rec.combine_id = combine_rec
        return

    def confirm_purchase_receipt(self):
        for i in self.detail_ids:
            po = self.env['purchase.order'].search([("name", '=', i.customerItemCode)], limit=1)
            if i.purchase_id and po:
                for k in po.picking_ids:
                    if k.state not in ['cancel', 'done']:
                        for mv in k.move_ids_without_package or k.move_lines:
                            mv.quantity_done = mv.product_uom_qty
                        k.button_validate()
                        for mv in k.move_ids_without_package or k.move_lines:
                            mv._action_done()
                            i.is_received = True
