# -*- coding: utf-8 -*-
{
    'name': "Arga Customization",

    'summary': """
        Arga Customizations""",

    'description': """
        Arga Customization
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
    'depends': ['base', 'sale', 'stock', 'calendar', 'account', 'purchase', 'exim_bellona', 'istikbal', 'project', 'helpdesk', 'repair', 'bsi_repair_parts_immediate_buying','planning','helpdesk_sale_timesheet','helpdesk_repair'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/report_delivery_order.xml',
        'wizard/repair_to_rfq_wiz_view.xml',
        'wizard/repair_to_delivery_wiz_view.xml',
        "data/sequencer.xml"
    ],

}
