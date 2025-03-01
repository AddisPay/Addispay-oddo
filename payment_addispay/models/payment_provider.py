import logging
import requests
from odoo import http
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json


_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('addispay', 'addispay')],
                            ondelete={'addispay': 'set default'},
                            help="The technical code of this payment provider",
                            string="Code")

    addispay_checkout_api_url = fields.Char(
        string="Addis Pay Checkout API URL", help="The base URL for the Checkout API endpoints",
        required_if_provider='addispay')
    addispay_merchant_id = fields.Char(
        string="Merchant ID", help="The ID That is sent with headers",
        required_if_provider='addispay')

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['addispay'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res

    def _AddisPay_make_request(self, url, data=None, method='GET'):
        not_url= self.env['ir.config_parameter'].sudo().get_param('web.base.url')+"/get-status-addispay"

        datua = {
            "data": {
                "total_amount": -1,
                "tx_ref": "",
                "currency": "ETB",
                "first_name": "haile",
                "email": "remamtsega@gmail.com",
                "phone_number":"0947731212",
                "last_name": "tsega",
                "session_expired":'300',
                "nonce":'780099',
                "order_detail": {
                    "items": "rfid",
                    "description": "I am testing this"
                },
            "success_url":not_url,
            "cancel_url":not_url,
            "error_url":not_url
    
            },
            
            "message": "hello work my.."
            
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Auth": "af026758-109d-46f7-a48d-5048d977898b_1"
            }

    
        self.ensure_one()
        datua["data"]["first_name"]=data["partner_name"]
        datua["data"]["last_name"]=data["partner_name"]
        datua["data"]["tx_ref"]=data["ref"]
        datua["data"]["total_amount"]=str(data["amount"])
        datua["data"]["nonce"]=str(data["ref"])
        headers["Auth"]=self.addispay_merchant_id
        page=self.addispay_checkout_api_url.split("/")
        response = requests.post(self.addispay_checkout_api_url, json=datua, headers=headers)
        response_content = response.json()
        data["Auth_key"]=self.addispay_merchant_id
        data["api_url"] = response_content["checkout_url"] + "/"+response_content["uuid"]
        return data
    
