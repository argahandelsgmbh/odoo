# -*- coding: utf-8 -*-
{
    'name': "Import Products",

    'summary': """Import Products with price and sales price and cost price
        """,

    'description': """
       Import Products with price and sales price and cost price
       Created a factor field in categor	
    """,

    'author': "HAKTechnologies",
    'website': "http://www.HAKTechnologies.com",
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/var_wizard.xml',
        'wizard/pricelists.xml',
    ],

}
