import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from datetime import datetime
import base64

class MpesaClient:
    consumer_key = "uZuD4wzEOJSaUrYZ2SQ0yuF1PSarRo7ApExK3PqKA0Rs2bHP"
    consumer_secret = "XD3hZnsDoAYXMGSskefW5pqn4eNEQi2RGRpjkRUAXLy3nn0AdGf24ODaOUs6SAE0"
    business_short_code = "174379"  # Default Sandbox Shortcode
    passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919" # Default Sandbox Passkey

    def get_token(self):
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        return response.json().get('access_token')

    def stk_push(self, phone, amount, callback_url):
        token = self.get_token()
        # FIXED: This must be the processrequest endpoint for the pop-up to trigger
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{self.business_short_code}{self.passkey}{timestamp}".encode()).decode()
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "BusinessShortCode": self.business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone, 
            "PartyB": self.business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": "MakaoBooking",
            "TransactionDesc": "Booking Deposit"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def check_status(self, checkout_request_id):
        """
        Manually query the status of a specific STK Push request.
        """
        token = self.get_token()
        url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{self.business_short_code}{self.passkey}{timestamp}".encode()).decode()
        
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "BusinessShortCode": self.business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    