from odoo import http
from odoo.http import request
import json
import requests
import time

class PaymentAddisPay(http.Controller): 
    _return_url = '/get-status-addispay'

    @http.route(_return_url, type='json', auth='public',
                methods=['POST'], csrf=False, save_session=False,web=True)
    def AddisPay_return(self, **kw):
        print("the requested payload",json.loads(request.httprequest.data))
        data = json.loads(request.httprequest.data)
        if data:
            stat="Error"
            if data.get('status').upper()=="PROCESSED" or data.get('status').lower()=="success":
                stat="Done"
            data={
                "cartId":data.get("nonce",False),
                "respStatus":stat
            }
        tx_sudo=request.env['payment.transaction'].sudo()._get_tx_from_notification_data(
        'addispay', data)
        tx_sudo._handle_notification_data('addispay', data)
        y=self.poll_status_addispay(tr_id=tx_sudo.id)
        print(y)
        return {
            "state":tx_sudo.state,
            "tx_id":tx_sudo.id,
            "android_url":request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/payment/status/poll",
            "web_url":request.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/payment/status"
        }
    def poll_status_addispay(self, tr_id=None):
        monitored_tx = request.env['payment.transaction'].sudo().browse(tr_id).exists()
        if not monitored_tx:
              # The session might have expired, or the tx has never existed.
            raise Exception('tx_not_found')

        # Finalize the post-processing of the transaction before redirecting the user to the landing
        # route and its document.
        if monitored_tx.state == 'done' and not monitored_tx.is_post_processed:
            try:
                monitored_tx._finalize_post_processing()
            except psycopg2.OperationalError:  # The database cursor could not be committed.
                request.env.cr.rollback()  # Rollback and try later.
                raise Exception('retry')
            except Exception as e:
                request.env.cr.rollback()
                _logger.exception(
                    "Encountered an error while post-processing transaction with id %s:\n%s",
                    monitored_tx.id, e
                )
                raise

        # Return the post-processing values to display the transaction summary to the customer.
        return monitored_tx._get_post_processing_values()




