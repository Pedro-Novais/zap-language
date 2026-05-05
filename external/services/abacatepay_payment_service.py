import os
from datetime import datetime, timedelta, timezone

import requests

from core.interface.service import PaymentService


class AbacatePayPaymentService(PaymentService):
    
    URL_BASE = "https://api.abacatepay.com/v2"


    def __init__(self):
        self.api_key = os.getenv("ABACATEPAY_API_KEY")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_subscription(
        self,
        user: str,
        plan_id: str,
    ) -> tuple[str, str, datetime]:

        url = f"{self.URL_BASE}/subscriptions/create"
        payload = {
            "customerId": user,
            "items": plan_id,
            "frequency": "monthly"
        }
        response = requests.post(url, json=payload, headers=self.headers)
        return response.json()

    def create_customer(
        self,
        user_id: str,
        name: str,
        email: str,
    ) -> str:

        url = f"{self.URL_BASE}/customers/create"
        payload = {
            "name": name,
            "email": email,
            "externalId": user_id,
        }
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        response_data = response.json()
        customer_id = response_data.get("customerId")
        if not customer_id:
            raise ValueError("Missing customerId in payment gateway response")
        
        return customer_id

    def cancel_subscription(
        self,
        user_id: str,
        subscription_id: str,
    ) -> None:

        url = f"{self.URL_BASE}/subscriptions/{subscription_id}/cancel"
        response = requests.post(url, headers=self.headers)
        return response.status_code == 200
