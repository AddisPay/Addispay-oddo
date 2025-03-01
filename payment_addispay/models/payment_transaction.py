import logging
from werkzeug import urls
from odoo import api, models, _,fields
from odoo.exceptions import ValidationError
from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_addispay.controllers.payment_AddisPay_odoo import PaymentAddisPay

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    addispay_type = fields.Char(string="Addispay Transaction Type")
    @api.model
    def _compute_reference(self, provider_code, prefix=None, separator='-',
                           **kwargs):
        if provider_code == 'addispay':
            prefix = payment_utils.singularize_reference_prefix()
        return super()._compute_reference(provider_code, prefix=prefix,
                                          separator=separator, **kwargs)

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'addispay':
            return res
        return self.execute_payment()

    def execute_payment(self):
        api_url = self.provider_id.addispay_checkout_api_url
        AddisPay_values = {
            "public_key": self.provider_id.addispay_merchant_id,
            "amount": self.amount,
            "email": self.partner_email,
            "ref":   self.reference,
            'return': urls.url_join("http://127.0.0.1:8069/",
                                    PaymentAddisPay._return_url),
            'callback': urls.url_join("http://127.0.0.1:8069/",
                                      PaymentAddisPay._return_url),
            'partner_name':self.partner_name,
            'partner_email':self.partner_email,
            'partner_phone':self.partner_phone,
            'provider_id':self.provider_id,

        }
        response_content = self.provider_id._AddisPay_make_request(
            api_url, AddisPay_values)
        return response_content

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        tx = super()._get_tx_from_notification_data(provider_code,
                                                    notification_data)
        if provider_code != 'addispay':
            return tx
        reference = notification_data.get('cartId', False)
        if not reference:
            raise ValidationError(_("addispay: No reference found."))
        tx = self.search(
            [('reference', '=', reference), ('provider_code', '=', 'addispay')])
        if not tx:
            raise ValidationError(
                _("AddisPay: No transaction found matching reference"
                  "%s.") % reference)
        return tx

    def _handle_notification_data(self, provider_code, notification_data):
        tx = self._get_tx_from_notification_data(provider_code,
                                                 notification_data)
        tx._process_notification_data(notification_data)
        tx._execute_callback()
        return tx

    def _process_notification_data(self, notification_data):
        super()._process_notification_data(notification_data)
        if self.provider_code != 'addispay':
            return
        status = notification_data.get('respStatus')
        if status == 'Done':
            self._set_done(state_message="Authorised")
        elif status == 'APPROVED':
            self._set_pending(state_message="https:example.comAuthorised but on hold for "
                                            "further anti-fraud review")
        elif status in ('E', 'D'):
            self._set_canceled(state_message="Error")
        else:
            _logger.warning("Received unrecognized payment state %s for "
                            "transaction with reference %s",
                            status, self.reference)
            self._set_error("addispay: " + _("Invalid payment status."))
