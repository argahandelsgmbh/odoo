# -*- coding: utf-8 -*-
{
    'name': "PO Export",

    'summary': """
        PO Export""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report_xlsx', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/po_export.xml',
        'views/views.xml',

    ],

}
