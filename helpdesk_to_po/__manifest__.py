# -*- coding: utf-8 -*-
{
    'name': "Helpdesk customizations",

    'summary': """
       Create purchase order from helpdesk""",

    'description': """
        Createpurchase order from helpdesk
    """,

    'author': "HAK Technologies",
    'website': "http://www.haktechnologies.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/views.xml',
        'wizard/help_to_rfq_wiz_view.xml',

    ],
   
}
