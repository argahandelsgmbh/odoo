# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
import xlwt
import io
import base64
from xlwt import easyxf
import datetime


class PrintTimeoffReport(models.Model):
    _name = "employee.timeoff.report"

    @api.model
    def _get_from_date(self):
        company = self.env.user.company_id
        current_date = datetime.date.today()
        from_date = company.compute_fiscalyear_dates(current_date)['date_from']
        return from_date

    from_date = fields.Date(string='From Date', default=_get_from_date)
    to_date = fields.Date(string='To Date', default=datetime.date.today())
    timeoff_report_file = fields.Binary('Employee Timeoff Report')
    file_name = fields.Char('File Name')
    timeoff_report_printed = fields.Boolean('Employee Timeoff Report Printed')

    def action_print_timeoff_report(self):
        new_from_date = self.from_date.strftime('%Y-%m-%d')
        new_to_date = self.to_date.strftime('%Y-%m-%d')

        workbook = xlwt.Workbook()
        column_heading_style = easyxf('font:height 200;font:bold True')
        worksheet = workbook.add_sheet('Employee Timeoff Report')
        worksheet.write(2, 3, self.env.user.company_id.name,
                        easyxf('font:height 300;font:bold True;align: horiz center;'))
        worksheet.write(3, 2, new_from_date, easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write(3, 3, 'To', easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write(3, 4, new_to_date, easyxf('font:height 250;font:bold True;align: horiz center;'))
        worksheet.write(6, 0, _('Employee'), column_heading_style)
        worksheet.write(6, 1, _('Position'), column_heading_style)
        worksheet.write(6, 2, _('Mobile'), column_heading_style)
        worksheet.write(6, 3, _('Email'), column_heading_style)
        worksheet.write(6, 4, _('Department'), column_heading_style)
        worksheet.write(6, 5, _('Leave Type'), column_heading_style)
        worksheet.write(6, 6, _('Leave from'), column_heading_style)
        worksheet.write(6, 7, _('To'), column_heading_style)
        worksheet.write(6, 8, _('Number of leave days'), column_heading_style)
        worksheet.write(6, 9, _('Description'), column_heading_style)
        worksheet.write(6, 10, _('Status'), column_heading_style)
        worksheet.write(6, 11, _('Requested on'), column_heading_style)
        worksheet.write(6, 12, _('Requested by'), column_heading_style)
        worksheet.write(6, 13, _('Leaves used'), column_heading_style)
        worksheet.write(6, 14, _('Allocated Leaves'), column_heading_style)
        worksheet.write(6, 15, _('Remaining Leaves'), column_heading_style)

        worksheet.col(0).width = 5000
        worksheet.col(1).width = 5000
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 5000
        worksheet.col(6).width = 5000
        worksheet.col(7).width = 5000
        worksheet.col(8).width = 5000
        worksheet.col(9).width = 5000
        worksheet.col(10).width = 5000
        worksheet.col(11).width = 5000
        worksheet.col(12).width = 5000
        worksheet.col(13).width = 5000
        worksheet.col(14).width = 5000
        worksheet.col(15).width = 5000
        worksheet.row(2).height = 400
        worksheet.row(3).height = 400
        worksheet.row(0).height = 400


        row = 7

        for wizard in self:
            heading = 'Employee Timeoff Report'
            worksheet.write_merge(0, 0, 0, 9, heading, easyxf(
                'font:height 300; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
            leave_rep= self.env['hr.leave'].search([('create_date', '>=', wizard.from_date),
                                                                 ('create_date', '<=', wizard.to_date)])

            for leave in leave_rep:
                date = leave.create_date.strftime('%Y-%m-%d')
                start = leave.request_date_from.strftime('%Y-%m-%d')
                to = leave.request_date_to.strftime('%Y-%m-%d')
                worksheet.write(row, 0, leave.employee_id.name)
                worksheet.write(row, 1, leave.employee_id.job_title)
                worksheet.write(row, 2, leave.employee_id.mobile_phone)
                worksheet.write(row, 3, leave.employee_id.work_email)
                worksheet.write(row, 4, leave.employee_id.department_id.name)
                worksheet.write(row, 5, leave.holiday_status_id.name)
                worksheet.write(row, 6, start)
                worksheet.write(row, 7, to)
                worksheet.write(row, 8, leave.number_of_days)
                worksheet.write(row, 9, leave.name)
                worksheet.write(row, 10, leave.state)
                worksheet.write(row, 11, date)
                worksheet.write(row, 12, leave.create_uid.name)
                worksheet.write(row, 13, leave.employee_id.allocation_used_display)
                worksheet.write(row, 14, leave.employee_id.allocation_display)
                worksheet.write(row, 15, leave.employee_id.remaining_leaves)

                row += 1
                key = u'_'.encode('utf-8')
                str(key, 'utf-8')




            fp = io.BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.timeoff_report_file = excel_file
            wizard.file_name = 'Employee Timeoff Report.xls'
            wizard.timeoff_report_printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'employee.timeoff.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }

# vim:expandtab:smartindent:tabstop=2:softtabstop=2:shiftwidth=2:

