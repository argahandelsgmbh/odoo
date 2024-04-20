# -*- coding: utf-8 -*-
{
    'name': "Arga Customization",

    'summary': """
        Arga Customizations""",

    'description': """
    """,

    'author': "HAK Technologies",
    'website': "http://www.haktechnologies.com",
    'images': ['static/description/icon.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.1',
    'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'account', 'purchase', 'project'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/picking.xml',
        'views/project.xml',
        'views/sale.xml',
        'views/report_delivery_order.xml',
        "data/sequencer.xml"
    ],

}
