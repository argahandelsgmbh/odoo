# -*- coding: utf-8 -*-
{
    'name': "Import Discount",

    'summary': """
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "HAK Technologies",
    'website': "http://www.yourcompany.com",
    "license": "AGPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/discount_wizard.xml',
    ],

}
