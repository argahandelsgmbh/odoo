# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProjectTaskInh(models.Model):
    _inherit = 'project.task'

    delivery_date = fields.Date(string='Delivery Date', copy=False)

    def write(self, vals):
        res = super(ProjectTaskInh, self).write(vals)
        self.sale_line_id.order_id.with_context(from_project=True).update({
            'commitment_date' : self.delivery_date
        })
        return res
