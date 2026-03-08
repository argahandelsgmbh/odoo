# -*- coding: utf-8 -*-
{
    'name': "Import Vendor Pricelist",

    'summary': """Import Vendor Pricelist
        """,

    'description': """
       Vendor Pricelist
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
    'version': '19.6',
        'installable': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock','product','sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/views.xml',
        'wizard/pricelists.xml',
    ],

}
