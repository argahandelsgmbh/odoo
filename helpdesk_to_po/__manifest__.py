# -*- coding: utf-8 -*-
{
    'name': "Helpdesk to PO",

    'summary': """
        Create Purchase order from Helpdesk""",

    'description': """
        Create Purchase order from Helpdesk
    """,

    'author': "HAK Technologies",
    'website': "http://www.HAKTechnologies.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '19.2',
     'license': 'OPL-1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'purchase','helpdesk_timesheet', 'helpdesk_stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/views.xml',
        'wizard/help_to_rfq_wiz_view.xml',

    ],
   
}
