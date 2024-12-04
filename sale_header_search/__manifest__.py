# -*- coding: utf-8 -*-
{
    'name': "Sale Order Date Filters",

    'summary': "Sale Order Date Filters",

    'description': """
    This add-on is a funtional plug-in that places a fixed filter bar for sale order module. It expedites the record filtering process with one single click.
    
    """,

    'author': "Odoo.RED team",
    'website': "https://cdn.odoo.red",
    'category': 'Extra Tools',
    'version': '17.0.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_header_search/static/src/js/date_search.js',
            'sale_header_search/static/src/js/header_select_model.js',
            'sale_header_search/static/src/js/sale_order_list.js',
            'sale_header_search/static/src/xml/header_select_model.xml',
            'sale_header_search/static/src/css/header_select_model.css',
        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'images': ['static/description/images/sale.jpg'],
    'sequence': 100
}
