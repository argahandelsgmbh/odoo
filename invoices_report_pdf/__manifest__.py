# -*- coding: utf-8 -*-
{
    'name': "Invoices Report",

    'summary': """
        Invoices Report""",

    'description': """
        Invoices Report
    """,

    'author': "Haktechnologies",
    'website': "http://www.haktechnologies.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'license': 'OPL-1',
    

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_de'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/invoice_report_wizard.xml',
        'report/invoices_report.xml',
    ],

}
