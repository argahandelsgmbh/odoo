
from odoo.addons.payment.controllers.portal import PaymentPortal
from odoo.http import route

# class PaymentPortalInh(PaymentPortal):

    # @route()
    # def shop_payment_transaction(self, order_id, access_token, **kwargs):
    #     order_sudo = self._document_check_access(
    #         'sale.order', order_id, access_token
    #     )
    #     order_sudo.write({'active': True})
    #     return super().shop_payment_transaction(order_id, access_token, **kwargs)


