# -*- coding: utf-8 -*-
{
    'name': "List View Date Filters",

    'summary': "List View Date Filters",

    'description': """
    This add-on is a funtional plug-in that creates a fixed filter bar in the accounting module for list views.
    
    """,

    'author': "Odoo.RED team",
    'website': "https://cdn.odoo.red",
    'category': 'Extra Tools',
    'version': '17.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    'assets': {
        'web.assets_backend': [
            'account_header_search/static/src/js/date_search.js',
            'account_header_search/static/src/js/header_select_model.js',
            'account_header_search/static/src/xml/header_select_model.xml',
            'account_header_search/static/src/css/header_select_model.css',

        ]
    },
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
    'images': ['static/description/images/account.jpg'],
    'sequence': 10
}
