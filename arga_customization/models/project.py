# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError

class ProjectTaskInh(models.Model):
    _inherit = 'project.task'

    delivery_date = fields.Date(string='Delivery Date', copy=False)

    def write(self, vals):
        res = super(ProjectTaskInh, self).write(vals)
        if vals.get('delivery_date'):
            if self.sale_line_id.order_id.delivery_date != self.delivery_date:
                self.sale_line_id.order_id.delivery_date = self.delivery_date
