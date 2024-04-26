
{
    "name": "Sale Fixed Discount",
    "summary": "Allows to apply fixed amount discounts in sales orders.",
    "version": "16.1",
    "category": "Sales",
    "website": "hunainfast@gmail.com",
    "author": "HAK Technologies",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'images': ['static/description/banner.png'],
    "depends": ["sale_management"],
    "data": [
        "views/sale_order_views.xml",
        "views/sale_portal_templates.xml",
        "reports/report_sale_order.xml",
    ],
}
