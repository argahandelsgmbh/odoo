# -*- coding: utf-8 -*-

{
    'name': "Multiple Product Selection",
    'version': '19.6',
    'category': 'Purchases,Sales',
    'summary': 'Multiple product selection for creating sale and'
               ' purchase order',
    'description': 'This module help you to select multiple products while '
                   'creating a sale order or purchase order.We can add the '
                   'selected products in to the corresponding order line.',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['purchase', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/multiple_product_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
