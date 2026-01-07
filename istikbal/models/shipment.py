# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json
from datetime import datetime
import qrcode
import base64
from io import BytesIO
from odoo import models, fields, api
from odoo.http import request
from odoo import exceptions, _


class IncomingShipments(models.Model):
    _name = 'istikbal.incoming.shipments'
    _description = "Istikbal incoming shipments"
    _rec_name = 'producCode'
    _order = "producCode"

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    producCode = fields.Char('Product Code')
    packageEnum = fields.Char('packageNum')
    bdtCode = fields.Char('bdtCode')
    productRef = fields.Char('productRef')
    maktx = fields.Char('maktx')
    vrkme = fields.Char('vrkme')
    lgort = fields.Char('lgort')
    volum = fields.Char('volum')
    audat = fields.Char('audat')
    stawn = fields.Char('stawn')
    quatity = fields.Char('quatity')
    customerRef = fields.Char('customerRef')
    customerBarCode = fields.Char('customerBarCode')
    text = fields.Char('text')
    quantity = fields.Char('Quantity')
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    sale_id = fields.Many2one('sale.order', string="Purchase Order")

    


class Shipments(models.Model):
    _name = 'istikbal.shipments.header'
    _description = "Istikbal shipment Headers"
    _rec_name = 'shipmentNumber'
    _order = "shipmentNumber"

    disPactDate = fields.Char('disPactDate')
    containerNumber = fields.Char('Container Number')
    truckPlate = fields.Char('Truck Plate')
    truckPlate2 = fields.Char('Truck Plate 2')
    shipmentDate = fields.Char('Shipment Date')
    invoiceNumber = fields.Char('Invoice Number')
    shipmentNumber = fields.Char('Shipment Number')
    name = fields.Char('Shipment Number')
    volum = fields.Float('volum')
    voleh = fields.Float('voleh')
    detail_ids = fields.One2many('istikbal.shipments.details', 'shipment_id', string='Shipment Details')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)
    combine_id = fields.Many2one('istikbal.combine.shipments')


class ShipmentDetails(models.Model):
    _name = 'istikbal.shipments.details'
    _description = "Istikbal Shipment Details"
    _rec_name = 'shipMentNumber'
    _order = "shipMentNumber"

    shipment_id = fields.Many2one('istikbal.shipments.header')
    pakageEnum = fields.Char('Package Number')
    shipMentNumber = fields.Char('Shipment Number')
    bdtCode = fields.Char('Code')
    productCode = fields.Char('Product Code')
    productPackage = fields.Char('Product Package')
    quantity = fields.Float('Quantity')
    orderReference = fields.Char('Order Reference')
    bdtOrderNumber = fields.Char('Order Number')
    customerItemReference = fields.Char('Customer Item Reference')
    customerItemCode = fields.Char('Customer Item Code')
    customerOrderReference = fields.Char('Customer Order Reference')
    productName = fields.Char('Product Name')
    productNamePack = fields.Char('Product Name Pack')
    productNameEN = fields.Char('Product Name Eng.')
    volum = fields.Float('Volume')
    vrkme = fields.Char('vrkme')
    inhalt = fields.Char('inhalt')
    mvgr3Desc = fields.Char('mvgr3Desc')
    brgew = fields.Char('brgew')
    gewei = fields.Char('gewei')
    zzbdtAmount = fields.Char('zzbdtAmount')
    voleh = fields.Char('voleh')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env.company)

    qr_image = fields.Binary("QR Code", compute="_generate_qr_code")
    purchase_id = fields.Many2one('purchase.order',string="Purchase Order",compute="compute_the_purchase_no",store=True)
    sale_id = fields.Many2one('sale.order')
    combine_id = fields.Many2one('istikbal.combine.shipments')
    is_received = fields.Boolean('Received')
    price = fields.Float()
    picking_id = fields.Many2one('stock.picking')
    subtotal = fields.Float()
    product_id = fields.Many2one("product.template", "Product")
    pricelist_price = fields.Float("Pricelist Price")

    @api.depends('customerItemCode')
    def compute_the_purchase_no(self):
        for rec in self:
            purchase_id=self.env['purchase.order'].search([('name','=',rec.customerItemCode)],limit=1)
            if not purchase_id:
                if '*' in rec.customerItemCode:
                    name=rec.customerItemCode.split('*')[0]
                    purchase_id=self.env['purchase.order'].search([('name','=',name)],limit=1)
                
            rec.purchase_id=purchase_id.id
    

    def _generate_qr_code(self):
        
        for i in self:
            
            i.product_id = self.env['product.template'].search([("default_code", '=', i.productCode)], limit=1).id
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=20,
                border=4,
            )
            qr.add_data(i.productCode)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_img = base64.b64encode(temp.getvalue())
            i.qr_image = qr_img

    def action_receive_po(self):
        if self.purchase_id.state in ['purchase', 'done'] and not self.is_received:
            lines = self.purchase_id.order_line.filtered(lambda i: i.product_id.default_code == self.productCode)
            if lines:
                if not self.picking_id:
                    pick = lines.move_ids.filtered(
                        lambda h: h.product_id.default_code == self.productCode).picking_id.ids
                    pick_id = pick[-2] if len(pick) > 1 else pick[0]
                    # self.picking_id = pick_id
                    if self.picking_id.state == 'done':
                        self.picking_id = pick_id
                        self.is_received = True
                for move in lines.move_ids:
                    if move.state not in ['done', 'cancel']:
                        move.quantity = self.quantity

                if len(lines.move_ids) > 1:
                    action_data = lines.move_ids.filtered(
                        lambda h: h.state not in ['done', 'cancel']).picking_id.with_context(
                        skip_backorder=False).button_validate()
                    # print(action_data)
                    backorder_wizard = self.env['stock.backorder.confirmation'].with_context(action_data['context'])
                    backorder_wizard.process()

                    if not self.picking_id:
                        pick = lines.move_ids.filtered(
                            lambda h: h.product_id.default_code == self.productCode).picking_id.ids
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
                            lambda h: h.product_id.default_code == self.productCode).picking_id.ids
                        pick_id = pick[-2] if len(pick) > 1 else pick[0]
                        stock_picking = self.env['stock.picking'].browse([pick_id])

                        if stock_picking.state == 'done':
                            self.picking_id = pick_id
                            self.is_received = True


class SalesOrderAnalysis(models.Model):
    _name = 'istikbal.sales.order.analysis'
    _description = "Istikbal Sale order Analysis"
