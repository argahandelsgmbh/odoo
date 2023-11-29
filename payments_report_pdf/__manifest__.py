# -*- coding: utf-8 -*-
{
    'name': "Payments Report",

    'summary': """
        Payments Report""",

    'description': """
        Payments Report
    """,

    'author': "HAKTechnologies.com",
    'website': "http://www.HAKTechnologies.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/payment_report_wizard.xml',
        'report/payment_report.xml',
    ],

}
