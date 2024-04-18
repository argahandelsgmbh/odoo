# -*- coding: utf-8 -*-
{
    'name': "Sale Order Payment",

    'summary': """
      Sale Order Payment""",

    'description': """
        Payment count in sale order
    """,

    'author': "HAK Technologies",
    'website': "http://www.HAKTechnologies.com",
    'images': ['description/icon.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'purchase', 'sale_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
