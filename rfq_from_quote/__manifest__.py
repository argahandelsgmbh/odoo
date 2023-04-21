{
    'name': 'Generate RFQ from Sales Quotation',
    'version': '1.0',
    'summary': '',
    'description': '',
    'license': 'OPL-1',
    'category': 'Sales',
    'author': 'abc',
    'website': 'www.abc.tech',
    'depends': ['sale_management', 'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/so_to_rfq_wiz_view.xml',
        'views/sale_order_views_inherit.xml',
        'views/purchase_order_views_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
}