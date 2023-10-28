# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Open One2many in External ListView',
    'version': '15.0.1.0.0',
    'sequence': 1,
    'summary': """
        External List View, External One2many List, All in one External One2many List, All in one One2many List, 
        Open One2many FormView, All in one ListView Manager, Open One2many Form View, All in one List View Manager,
        Dynamic View List Dynamic List View, Search Filters Search, Search Group by Search, External Table List,
        Open ListView One2many, Open List View One2many, Open One2many in List, External SubList View, External Sub List
    """,
    'description': "Open One2many in External ListView to allow users to search, filter and group by.",
    'author': 'Innoway',
    'maintainer': 'Innoway',
    'price': '0.0',
    'currency': 'USD',
    'website': 'https://innoway-solutions.com',
    'license': 'LGPL-3',
    'images': [
        'static/description/wallpaper.png'
    ],
    'depends': [

    ],
    'data': [
        
    ],
    'assets': {
        'web.assets_backend': [
            'open_one2many_externally/static/src/scss/list_view.scss',
            'open_one2many_externally/static/src/js/list_view.js',
        ],
    },
    'demo': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': [
        
    ],
}