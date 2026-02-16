# -*- coding: utf-8 -*-
{
    'name': "Repair/Helpdesk",

    'summary': """
       Repair/Helpdesk""",

    'description': """
        Create Delivery from Repair
        Create PO from Repair
        Create Repair from Helpdesk
    """,

    'author': "HAK Technologies",
    'website': "http://www.haktechnologies.com",
    'images': ['static/description/icon.png'],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.2',
    'license': 'OPL-1',
        'installable': True,

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'stock', 'helpdesk', 'repair', 'helpdesk_sale_timesheet', 'helpdesk_repair',
                'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/helpdesk.xml',
        'views/repair.xml',
        # 'views/report_delivery_order.xml',
        'wizard/repair_to_rfq_wiz_view.xml',
        'wizard/repair_to_delivery_wiz_view.xml',
        "data/sequencer.xml"
    ],

}
