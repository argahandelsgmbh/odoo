# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime
from datetime import timedelta

from odoo.exceptions import UserError


class AccountLineInh(models.Model):
    _inherit = 'account.analytic.line'

    def write(self, vals):
        res = super(AccountLineInh, self).write(vals)
        if "date" in vals:
            planning = self.env['planning.slot'].search([('employee_id', '=', self.employee_id.id)]).filtered(lambda i:i.start_datetime.date() >= self.date and i.end_datetime.date() <= self.date)
            if not planning:
                raise UserError('This employee is not available on this slot.')
        return res