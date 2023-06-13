# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Employee Time-off Report in Excel',
    'version' : '14.0.1.1',
    'description': """Employee Time-off detailed report in Excel Format""",
    'category': 'Human Resource',
    'website': 'shads7039@gmail.com',
    'author': 'Suhaib Khateeb',
    'summary': 'Employee leave/Time-off report with all the required details in Excel format',
    'depends': ['hr', 'hr_holidays'],
    'data': ['wizard/sak_employee_timeoff_report.xml'],
    'demo': [],
    'qweb': [],
    'images':['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
