# -*- coding: utf-8 -*-
{
    'name': "Sale Menus",

    'summary': """
        Menues in sales order""",

    'description': """
         Menues in sales order
1.Quotation
2.Orders
3.PO orders
4.Ready Orders
5.Done Orders
    """,

    'author': "HAK Technologies",
    'website': "http://www.HAKTechnologies.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.2',
     'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
