import logging
import requests
from odoo import http
import random
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import binascii


_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('addispay', 'addispay')],
                            ondelete={'addispay': 'set default'},
                            help="The technical code of this payment provider",
                            string="Code")
    addispay_public_api_key = fields.Char(
        string="Addis Pay Public API Key", help="The API key of the webservice user", required_if_provider='addispay',
        groups='base.group_system')
    addispay_private_key = fields.Char(
        string="Addis Pay Private Key", help="The client key of the webservice user",
        required_if_provider='addispay')
    addispay_checkout_api_url = fields.Char(
        string="Addis Pay Checkout API URL", help="The base URL for the Checkout API endpoints",
        required_if_provider='addispay')
    addispay_return_api_url = fields.Char(
        string="Addis Pay return API URL", help="The base URL for the return API endpoints",
        required_if_provider='addispay')
    addispay_callback_api_url = fields.Char(
        string="Addis Pay callback API URL", help="The base URL for the callback API endpoints",
        required_if_provider='addispay')
    
    def parse_public_key(self,public_key):
        decoded_public_key = base64.b64decode(public_key)
        rsa_key = RSA.import_key(decoded_public_key)
        return rsa_key

    def parse_private_key(self,private_key):
        decoded_private_key = base64.b64decode(private_key)
        rsa_key = RSA.import_key(decoded_private_key)
        return rsa_key

    def encrypt_data(self,data, public_key):
        rsa_key = self.parse_public_key(public_key)
        cipher = PKCS1_v1_5.new(rsa_key)
        encrypted_bytes = cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_bytes).decode()

    def decrypt_data(self,encrypted_data, private_key):
        rsa_key = self.parse_private_key(private_key)
        cipher = PKCS1_v1_5.new(rsa_key)
        decoded_encrypted_data = base64.b64decode(encrypted_data)
        decrypted_bytes = cipher.decrypt(decoded_encrypted_data, None)
        return decrypted_bytes.decode()

    def encryptor(self,data):
        return data
        public_key = "LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBdDlHVXhjdXd6cFFZcU9xaWNiOHIKaHh1R1c3VmtmSkx3d2I4U0ltSjliVFBvdnhGRjJHRVpvZUs4aEFHTTV1NmZOWk9BaVNxZWZPZ2JsbXFLWnlRUgpwWnNqQ3BkSmo3aDVuaks4MHFiY0dqTXRNK0l5ODEvaGhra01GcG1ack5YWXNDdWQ3UWdhZEN2ZnVRMFlRUUtvCkRRNk9oUUdDZnRVK1ZhOHpIc3RlbHl6THV3eE90eU9oQ3Z1WFdkTDZ5Rit0NWp0dzcyY29MSnlIUnJ6TkVqbHgKUkdqbXB2aGxBRXhnby82T3AzZ2RFeHF5YTk2Y1VPVThYVmlaQlBHcE4yaVdRdGlMSXk5RWlpbmpWV2VKc1hpSgpiVVNRQUpXVGFHemRrb1lYQ3orTHJIcDVOcG1lQzM5S1lCeTBsUGorV1R6TDMzd0xreVcreXpQRHg5bW1oa0R4CnRRSURBUUFCCi0tLS0tRU5EIFJTQSBQVUJMSUMgS0VZLS0tLS0K"
        private_key = "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBdDlHVXhjdXd6cFFZcU9xaWNiOHJoeHVHVzdWa2ZKTHd3YjhTSW1KOWJUUG92eEZGCjJHRVpvZUs4aEFHTTV1NmZOWk9BaVNxZWZPZ2JsbXFLWnlRUnBac2pDcGRKajdoNW5qSzgwcWJjR2pNdE0rSXkKODEvaGhra01GcG1ack5YWXNDdWQ3UWdhZEN2ZnVRMFlRUUtvRFE2T2hRR0NmdFUrVmE4ekhzdGVseXpMdXd4Twp0eU9oQ3Z1WFdkTDZ5Rit0NWp0dzcyY29MSnlIUnJ6TkVqbHhSR2ptcHZobEFFeGdvLzZPcDNnZEV4cXlhOTZjClVPVThYVmlaQlBHcE4yaVdRdGlMSXk5RWlpbmpWV2VKc1hpSmJVU1FBSldUYUd6ZGtvWVhDeitMckhwNU5wbWUKQzM5S1lCeTBsUGorV1R6TDMzd0xreVcreXpQRHg5bW1oa0R4dFFJREFRQUJBb0lCQVFDRUtadmQydVgwb1daWgpqTm5mRHFRdE1BMGFRd0ZNMEJscU5BYkYwaXA4S2FaZU9mME41a0tYc24zNEsyVXpaTDN6dDJuak5WRmVYVVA0CmtnR1F4czRwVTdHT0c5ZzREVnJqODNidnZpamliWWxDbEpBdGkvS0txbHFXcFRsb214aUJFZHNxWVhranJhZmQKVlJ6cklRM1MxWFNERE9MV2JsdXpINVNSdjRiekNYa216bHB6QW1FeHc1cGozaU1vS250anhVYWdyNmpNOCtqQwpvNGNGUnRuZEZZWUltViswUkJVZFg0UVB4azlZRHJPZC9peThraG5wdHdYcmxGOTNBenRIRmlDc0JhNmpaRnUwCjV2cTFmRUh2b05OTWpUZ2VCUzhMdGU4T01FcVBmMFBOS2RFUWJXZjEvLzZTMll1dHJlUW1rejNaeWRUTVhnaGsKbWtQczg2NEJBb0dCQU92MGhGL21jNTBrZXdvUXRrU1pSMk1NZm9TdUxxQkFiTkJZd0RJWjkxWmdEbEplRnJ2cApGNkxtbCszQ0dEV1B5ZTRWRG5Mdyt6bk5sRGxweGIxaFpCUUhwQlM4OXNmc1B5N1RuVDJ6STRiNWFlYnZ5dmQxClkwUFVjZlJqaUd0SWNvd2hZUm5xd0RXdStIWG5zdnB1QUJ1VlVRVklDb0xFdXhhOE9YOThVK3dwQW9HQkFNZHYKTnl1K1hQb2tYanlUcGpFbXcwSXExbFlETlMwYU1FckJ3dFZXUE9Uamt5YmFrd2lNbjdLRXN3ZVBoWFlyUk9HbQp4cmNZSG1SS1RxMGhnVGs1NGMvNWtVSWsvYXFOVENlNHpPZ2lNZkFMMzl3eFl1RkJqQmdLNVNMa3ZkdjYrRUxtCk5NbXpab3NucXJJdjk3TzdvdEZpZDZ1T3grRVE0eUs2OFdJRjRzcXRBb0dCQUo5Z1F3V3YySW5kT1VwOExWRTYKbzNCdzRRaG55dEN0azVKTFVFN0hJVHp6bHRqbCtyOGtXN1hKd2ZkenNmeUR5aWFKakgvdzdCQ0lIc1dFLzI3QwoyT0Y2bzhicU9GcWo1YTJRZkZaUHFRQ2plWGZtb3BieGNJSkJmbE5QNDdacmNndmJCQWFJZlJvRnZJZVBZR0l0CmFOODR4VWdtK0FxS0xjRFdsSlBhKzZpNUFvR0JBS3lmK0pwVmlUYy91WTRubzJmU0RKcytadzVHY29YYXNFaFYKRlNjQ0lXMWlDdUpMdVk5aDRXMXRiV1d5OWl2RjRqYUwzRjlwY2cwUFFMQ2RXclJGQk0rM1R1TjVEMVRNUDBuMgpyTzZWZ3JJc0pSWDhiWUZhOGo5eFZzcndRZUtpaHJlcGViSEpKbzUyeEVxK09HTUxuREF2VWpSZVAyYng3aGtHCnhaODZSd2QxQW44b3NvSjBZV2E5ckdYWDNyRXd2SjltdlBHdEFJNSsvUk9sZ2N1blZ0aWFCYktxSFlqNW5HR3YKMVdFLzRsMktHK21BS21DOXNkcnBLVU9tL29WSjFvTkVJMFRqRnJiTUg0WUtYRXN4S3RQM0k3a0NBMW15SGFMeAppcCtTZTlHUmFYUUlZYWtUenV6amc1YWFNdE9KcERUbjk1YlpkaGdvVTJMa3JZY2xmWlJOCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg=="
        encrypted_data="gCWrQkYZ+If1vAknZkUMtxBuRQz7C64rqOqbgFjj9ylYcT51TQaX+YemrsXFwVwOMcPhg9bHiYH1prrZclBt5Cy4yesciKe8XqZtpQk8hRk8t7sVHtwjvYscBJ3xSl9RxTHDnDWQhECfzW72SlGzHHaOdHOsAIxtalnspI4xOr2UMKeNwGhm2Fravc6BiEDjH7EEBBgfIdFIVuI3ytqdGeF18hq+TrKWy3Wg+y6bbhmpilPV/gkbSfldgl260uFPvAtOMVfJqtjNF0qavo+fhVlqVOkxZUAFOdtD4PvEzKoE8f6I7vw0emwff+6wDdYdBDCS0pZqSEFTdsj79oojzw=="
        public_key="LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBdFV5b2ZkRWdwQXlLRXBEaWRyWmoKVjFYU3hmUU43VzZGTlV1eW54d1liaTBoSHRVMUNUaGR6TWJlbkFkV0l4ZGU3SDZvWXVHTmVFaW9rdGp0VXdHbQpLTjRwMWUyNHY1cVE0YXR2NjhJaU1CS3ZkZmVRRkJDUHIvbHNVUE5vd3JabFdTUExIQmhTQmNmRlNNYWh6UnN1CkRWWEp0YzRlL08wYlF1TjJkYUdrengwOWVjTkY4V1hwZWtnV2hqcFlFT050ZGM3d3pkVERPbUJQMHNUVmJoc1AKSGpKNmZ3dklhbFF3SjN0dWs3Ry9SczRyZW9QUTY2a1JFd2thNVpCNDBDdlRaVE1IL2U4U2cyei9GcVVkakc2WgpnRTFtSEdseTNxWHBpdVg4bGgzMGhweGZ2WGVkbGttTUh1ZC9mQVJGOFVySC92TFI5cm5oK0dlZmczQUJJQ2dTClV3SURBUUFCCi0tLS0tRU5EIFJTQSBQVUJMSUMgS0VZLS0tLS0K"
        public_key="LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JSUJJakFOQmdrcWhraUc5dzBCQVFFRkFBT0NBUThBTUlJQkNnS0NBUUVBd3dISjBtdmVMWXh3MDRvdGtxTVkKRXAwQzdkSkN1VmxJd3ZOOTRaalA0WS90YTBWNyt1S1JqRGJFRkl6SUZWR1YxYXZMcDhPZDNJbXVTZnBlT29kOApQbitjL2hGY0dSYnlqa2dhNitwZHZNZ21EWFlPZDUyR05OZFZHRm00eDhnUzdWTEgrZmJHUDM2aVgwdnE4TFIrCmhoa3RXdFpUWDM3SGRWWEZySkQxaERBc3dDemhQSVNSbS9rallGMkRObVFybGhwNXhSd1Q3VFBaNEdBVkpSdkkKSDZaMFpkT0t6cCtTUnJhVTUvNjdBS2VuNnBxUXZvcmh1U21QN0RXQVpBV3U2YVlIR0tBY0hWVEc0YmZHZHFSdgpPcUViZWhEeXpmS01lR3FFZzg4bC91czV5M0V3blRFNVllOTNtdHNYbUFrZElIdmpxWFNBemlWTVJHRlFmRlpaCk93SURBUUFCCi0tLS0tRU5EIFJTQSBQVUJMSUMgS0VZLS0tLS0K"
        #if pu
        encrypted = self.encrypt_data(data, str(self.addispay_public_api_key).strip())
        #print("Encrypted Data:", encrypted)
        #decrypted = self.decrypt_data(encrypted_data, private_key)
        #print("Decrypted Data:", decrypted)
        return encrypted


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
                "currency": self.encryptor("ETB"),
                "first_name": "haile",
                "email": self.encryptor("remamtsega@gmail.com"),
                "phone_number":self.encryptor("0947731212"),
                "last_name": "tsega",
                "session_expired":self.encryptor(300),
                "nonce":'780099',
                "order_detail": {
                    "items": "rfid",
                    "description": "I am testing this"
                },
            "success_url":self.encryptor(not_url),
            "cancel_url":self.encryptor(not_url),
            "error_url":self.encryptor(not_url)
    
            },
            
            "message": self.encryptor("hello work my..")
            
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            "Auth": "af026758-109d-46f7-a48d-5048d977898b_1"
            }

    
        self.ensure_one()
        datua["data"]["first_name"]=self.encryptor(data["partner_name"])
        datua["data"]["last_name"]=self.encryptor(data["partner_name"])
        datua["data"]["tx_ref"]=self.encryptor(data["ref"])
        datua["data"]["total_amount"]=self.encryptor(str(data["amount"]))
        datua["data"]["nonce"]=self.encryptor(str(data["ref"]))
        headers["Auth"]=self.addispay_callback_api_url
        page=self.addispay_checkout_api_url.split("/")
        response = requests.post(self.addispay_checkout_api_url, json=datua, headers=headers)
        print("Abd",response)
        response_content = response.json()
        print(response_content)
        data["Auth_key"]=self.addispay_public_api_key
        data["api_url"] = response_content["checkout_url"] + "/"+response_content["uuid"]
        return data
    
