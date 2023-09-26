# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError


class RepairOrderLineInh(models.Model):
    _inherit = 'repair.line'

    qty_available = fields.Float(related='product_id.qty_available')


class RepairOrderInh(models.Model):
    _inherit = 'repair.order'

    def action_repair_end(self):
        if self.ticket_id:
            done_state = self.env['helpdesk.stage'].search([('name', '=', 'Done')], limit=1)
            if done_state:
                self.ticket_id.stage_id = done_state.id
        return super().action_repair_end()

    delivery_count = fields.Integer(string='Delivery Count', compute='count_delivery')
    is_po_created = fields.Boolean()

    def action_open_delivery(self):
        self.ensure_one()
        return {
            'name': 'purchases',
            'res_model': 'stock.picking',
            'domain': [('origin', '=', self.name)],
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': "{'create': False}"
        }

    def count_delivery(self):
        for rec in self:
            rec.delivery_count = self.env['stock.picking'].search_count([('origin', '=', self.name)])

    # def open_related_po(self):
    #     po_id = self.env['purchase.order'].search([('origin', '=', self.name)])
    #     action = self.env.ref('purchase.purchase_rfq').read()[0]
    #     action['domain'] = [('id', '=', po_id.id)]
    #     return action

    def open_repair_to_rfq_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create RFQ/PO',
            'view_id': self.env.ref('arga_customization.repair_to_rfq_wizard_form', False).id,
            'context': {'default_repair_id': self.id, 'default_vendor_id': self.partner_id.id,
                        'default_repair_line_ids': self.operations.mapped('id')},
            'target': 'new',
            'res_model': 'repair.rfq.wizard',
            'view_mode': 'form',
        }

    def open_repair_to_delivery_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Delivery',
            'view_id': self.env.ref('arga_customization.repair_to_delivery_wizard_form', False).id,
            'context': {'default_repair_id': self.id, 'default_partner_id': self.partner_id.id,
                        'default_repair_line_ids': self.operations.mapped('id')},
            'target': 'new',
            'res_model': 'repair.delivery.wizard',
            'view_mode': 'form',
        }


class HelpdeskTicketInh(models.Model):
    _inherit = 'helpdesk.ticket'

    # @api.model
    # def create(self, vals_list):
    #     rec = super().create(vals_list)
    #     rec.action_create_repair()
    #     return rec

    def action_create_repair(self):
        location = self.env['stock.location'].search([('company_id', '=', self.company_id.id), ('usage', '=', 'internal')], limit=1)
        event = self.env['repair.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'description': self.description,
            'product_qty': self.sale_line_id.product_uom_qty ,
            'schedule_date': datetime.datetime.today().date(),
            'user_id': self.user_id.id or False,
            'ticket_id': self.id,
            'location_id': location.id,
            'sale_order_id': self.sale_line_id.order_id.id or False,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_id.id,
        })


class AccountLineInh(models.Model):
    _inherit = 'account.analytic.line'

    def write(self, vals):
        res = super(AccountLineInh, self).write(vals)
        if "date" in vals:
            planning = self.env['planning.slot'].search([('employee_id', '=', self.employee_id.id)]).filtered(lambda i:i.start_datetime.date() >= self.date and i.end_datetime.date() <= self.date)
            if not planning:
                raise UserError('This employee is not available on this slot.')
        return res


class ProjectTaskInh(models.Model):
    _inherit = 'project.task'

    delivery_date = fields.Date(string='Delivery Date', copy=False)

    def write(self, vals):
        res = super(ProjectTaskInh, self).write(vals)
        if vals.get('delivery_date'):
            if self.sale_line_id.order_id.delivery_date != self.delivery_date:
                self.sale_line_id.order_id.delivery_date = self.delivery_date


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = _inherit

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('customer.number')
        return super(ResPartner, self).create(vals)


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    delivery_date = fields.Date(string='Delivery Date', copy=False)
    total_invoice_paid = fields.Float(compute='get_invoice_amount')
    total_invoice_amount = fields.Float(compute='get_invoice_amount')
    total_open_amount = fields.Float()
    total_qty = fields.Float('Total Lines')
    istikabl_qty = fields.Float('Istikabal')
    bellona_qty = fields.Float('Bellona')
    po_qty = fields.Float('PO')
    do_qty = fields.Float('DO')
    received_qty = fields.Float('Received', compute='_compute_total_qty')
    remaining_qty = fields.Float('Not Available Qty')
    receipt_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'), ('cancel', 'Cancelled'), ('', '    ')
    ], string='Receipt Status', readonly=True, copy=False)
    do_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'), ('cancel', 'Cancelled')
    ], string='DO Status', readonly=True, copy=False)
    po_state = fields.Selection([
        ('draft', 'Draft RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'), ('', '    ')
    ], 'PO Status', readonly=True)

    def get_invoice_amount(self):
        for rec in self:
            invoices = self.env['account.move'].search([('invoice_origin', '=', rec.name)]).filtered(lambda i: i.invoice_origin != False)
            inv_amount = sum(invoices.mapped('amount_total'))
            paid_amount = sum(invoices.mapped('amount_total')) - sum(invoices.mapped('amount_residual'))
            rec.total_invoice_amount = inv_amount
            rec.total_invoice_paid = paid_amount
            rec.total_open_amount = inv_amount - paid_amount

    def _compute_total_qty(self):
        for rec in self:
            purchase_order = self.env['purchase.order'].search([("origin", "=", rec.name)])
            receipt = self.env['purchase.order'].search([("origin", "=", rec.name)], limit=1)
            po_qty = 0
            istikabl_qty = 0
            bellona_qty = 0
            received_qty = 0
            for po in purchase_order:
                po_qty = po_qty + po.total_lines
                istikabl_qty = istikabl_qty + po.total_istikbal_lines
                bellona_qty = bellona_qty + po.total_bellona_lines
                received_qty = received_qty + po.total_received
            rec.po_qty = po_qty
            rec.istikabl_qty = istikabl_qty
            rec.bellona_qty = bellona_qty
            rec.received_qty = received_qty
            rec.total_qty = len(rec.order_line.filtered(lambda i: i.product_id.type == 'product').mapped('id'))
            rec.do_qty = len(self.env['stock.move.line'].search([("origin", "=", rec.name), ("state", "=", 'done')]))

            if receipt:
                rec.receipt_status = receipt.receipt_status
                rec.po_state = receipt.state
            else:
                rec.receipt_status = ''
                rec.po_state = ''

            rec.do_status = 'draft'
            if rec.picking_ids:
                if all(line.state == 'waiting' for line in rec.picking_ids):
                    rec.do_status = 'waiting'
                if all(line.state == 'confirmed' for line in rec.picking_ids):
                    rec.do_status = 'confirmed'
                if all(line.state == 'assigned' for line in rec.picking_ids):
                    rec.do_status = 'assigned'
                if all(line.state == 'done' for line in rec.picking_ids):
                    rec.do_status = 'done'
                if all(line.state == 'cancel' for line in rec.picking_ids):
                    rec.do_status = 'cancel'

    def write(self, vals):
        res = super(SaleOrderInh, self).write(vals)
        if vals.get('delivery_date'):
            project_task = self.env['project.task'].search([("sale_line_id.order_id", '=', self.id)], limit=1)
            project_task.delivery_date = self.delivery_date
            project_task.planned_date_begin = self.delivery_date
            project_task.date_deadline = self.delivery_date
            self.action_update_appoint()
            for k in self.picking_ids:
                if k.state not in ['done', 'cancel']:
                    k.delivery_date = self.delivery_date
        return res

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if vals.get('delivery_date'):
            rec.action_create_appoint()
        return rec

    def action_update_appoint(self):
        event_search = self.env['calendar.event'].sudo().search([('sale_id', '=', self.id)])
        if event_search:
            event_search.update({
                'privacy': 'private',
                'show_as': 'free',
                'start': self.delivery_date,
                'stop': self.delivery_date + timedelta(minutes=30),
                'user_id': self.user_id.id,
                'partner_ids': [(4, self.partner_id.id)],
            })
        else:
            self.action_create_appoint()

    def action_create_appoint(self):
        name = self.name + "-" + self.partner_id.name
        event = self.env['calendar.event'].sudo().create({
            'name': name,
            'privacy': 'private',
            'show_as': 'free',
            # 'duration': self.duration,
            'start': self.delivery_date,
            'stop': self.delivery_date,
            # 'description': self.service,
            'user_id': self.user_id.id,
            'sale_id': self.id,
            'partner_ids': [(4, self.partner_id.id)],
        })


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    number = fields.Integer(string="Sr#", compute='_compute_get_number', default=1)
    available = fields.Float('Available Qty', related="product_id.qty_available")
    remaining_qty = fields.Float('Not Available')
    qty_in = fields.Float()
    qty_out = fields.Float()
    free_qty = fields.Float()
    total_price = fields.Float("Before Discount",compute="_compute_total_price",store=True)



    @api.depends('order_id')
    def _compute_get_number(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                if line.product_id:
                    line.number = number
                    number += 1
                else:
                    line.number = number


    @api.depends('product_id','price_unit','product_uom_qty')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price=rec.product_uom_qty*rec.price_unit


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    invoice_total = fields.Float('Order Total')
    remaining_amt = fields.Float('Open Amount')
    delivery_date = fields.Date(string='Delivery Date', copy=False)

    def _compute_total_amt(self):
        for i in self:
            sale_order = self.env['sale.order'].search([("name", '=', i.origin)], limit=1)
            i.invoice_total = sale_order.amount_total
            i.remaining_amt = sale_order.total_open_amount

    def write(self, vals):
        res = super(StockPickingInh, self).write(vals)
        if vals.get('delivery_date'):
            sale_order = self.env['sale.order'].search([("name", '=', self.origin)], limit=1)
            if sale_order and sale_order.delivery_date != self.delivery_date:
                sale_order.delivery_date = self.delivery_date
        #                 obj = self.env['calendar.event'].search([("picking_id", '=', self.id)])
        #                 if obj:
        #                     obj.sudo().write({
        #                         'name': self.name,
        #                         'start': self.delivery_date,
        #                         'duration': 1,
        #                         'privacy': 'confidential',
        #                         'stop':self.delivery_date + timedelta(hours=1),
        #                         'description': self.note,
        #                     })
        return res


#     def unlink(self):
#         res = super(StockPickingInh, self).unlink()
#         for i in self:
#             obj = self.env['calendar.event'].search([("picking_id", '=', i.id)]).unlink()
#         return res

#     @api.model_create_multi
#     def create(self, vals_list):
#         res_ids = super(StockPickingInh, self).create(vals_list)
#         res_ids._create_calander_envent()
#         return res_ids


#     def _create_calander_envent(self):

#         sale_order=self.env['sale.order'].search([("name",'=',self.origin)],limit=1)
#         print(sale_order.user_id.partner_id.id)
#         obj = self.env['calendar.event'].search([("picking_id", '=', self.id)])
#         if not obj:
#             obj = self.env['calendar.event'].create({
#                 'name': self.name,
#                 'start': self.delivery_date,
#                 'duration': 1,
#                 'partner_ids': [(6, 0, sale_order.user_id.partner_id.ids)],
#                 'privacy': 'confidential',
#                 'stop': self.delivery_date + timedelta(hours=1),
#                 'description': self.note,
#                 'picking_id': self.id,
#                 'user_id': sale_order.user_id.id,
#                 'allday': False
#             })


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    picking_id = fields.Many2one('stock.picking', "Picking")
    sale_id = fields.Many2one('sale.order')


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    sale_order = fields.Many2one('sale.order',compute="_compute_sale_order",store=True)
    sale_repair_id = fields.Many2one('sale.order')
    receipt_status = fields.Selection(selection=[
        ('draft', 'Draft'), ('waiting', 'Waiting for another Operations'),
        ('confirmed', 'Waiting'), ('assigned', 'Ready'),
        ('done', 'Done'), ('cancel', 'Cancelled')
    ], string='Receipt Status', readonly=True, copy=False)

    total_lines = fields.Integer()
    total_istikbal_lines = fields.Integer(string="Istikbal Lines")
    total_bellona_lines = fields.Integer(string="Bellona Lines")
    total_received = fields.Integer(string="Received")

    @api.depends('order_line', 'istikbal_shp_details', 'bellona_shipments', 'picking_ids')
    def _compute_lines(self):
        for rec in self:
            moves = len(self.env['stock.move.line'].search(
                [("move_id.picking_id.purchase_id", '=', rec.id), ("state", '=', 'done')]))
            rec.total_lines = len(rec.order_line.mapped('id'))
            rec.total_istikbal_lines = len(rec.istikbal_shp_details.mapped('id'))
            rec.total_bellona_lines = len(rec.bellona_shipments.mapped('id'))
            rec.total_received = moves if moves else 0

    def _compute_sale_order(self):
        for rec in self:
            sale_order = self.env['sale.order'].search([("name", '=', rec.origin)], limit=1).id
            rec.sale_order = sale_order
            rec.receipt_status = 'draft'
            if rec.picking_ids:
                if all(line.state == 'waiting' for line in rec.picking_ids):
                    rec.receipt_status = 'waiting'
                if all(line.state == 'confirmed' for line in rec.picking_ids):
                    rec.receipt_status = 'confirmed'
                if all(line.state == 'assigned' for line in rec.picking_ids):
                    rec.receipt_status = 'assigned'
                if all(line.state == 'done' for line in rec.picking_ids):
                    rec.receipt_status = 'done'
                if all(line.state == 'cancel' for line in rec.picking_ids):
                    rec.receipt_status = 'cancel'
            


class PurchaseOrderLineInh(models.Model):
    _inherit = 'purchase.order.line'

    number = fields.Integer(compute='_compute_get_number', store=True)

    @api.depends('sequence', 'order_id')
    def _compute_get_number(self):
        for order in self.mapped('order_id'):
            number = 1
            for line in order.order_line:
                line.number = number
                number += 1
