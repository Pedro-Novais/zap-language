import os
from datetime import datetime, timezone
from typing import Any, Optional

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

    @staticmethod
    def _parse_subscription_response_payload(
        data: dict[str, Any],
    ) -> tuple[str, Optional[datetime]]:
        payload = data.get("data") if isinstance(data.get("data"), dict) else data
        status = str(
            payload.get("status")
            or payload.get("subscriptionStatus")
            or payload.get("state")
            or "pending",
        )
        expires_raw = (
            payload.get("expiresAt")
            or payload.get("expires_at")
            or payload.get("currentPeriodEnd")
        )
        expires_at: Optional[datetime] = None
        if expires_raw:
            try:
                if isinstance(expires_raw, (int, float)):
                    expires_at = datetime.fromtimestamp(
                        expires_raw / 1000 if expires_raw > 1e12 else expires_raw,
                        tz=timezone.utc,
                    )
                elif isinstance(expires_raw, str):
                    normalized = expires_raw.replace("Z", "+00:00")
                    expires_at = datetime.fromisoformat(normalized)
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    else:
                        expires_at = expires_at.astimezone(timezone.utc)
            except (ValueError, OSError):
                expires_at = None
        return status, expires_at

    def create_subscription(
        self,
        customer_id: str,
        plan_id: str,
    ) -> tuple[str, Optional[str], Optional[datetime]]:

        url = f"{self.URL_BASE}/subscriptions/create"
        payload = {
            "customerId": customer_id,
            "items": [
                {
                    "id": plan_id,
                    "quantity": 1,
                }
            ],
            "methods": [
                "CARD",
            ],
        }
        response = requests.post(url, json=payload, headers=self.headers, timeout=60)
        response.raise_for_status()
        data = response.json() if response.content else {}
        if not isinstance(data, dict):
            data = {}

        gateway = "abacatepay"
        status, expires_at = self._parse_subscription_response_payload(data=data)
        return status, gateway, expires_at

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
        customer_id = response_data.get("data", {}).get("id")
        if not customer_id:
            raise ValueError("Missing customerId in payment gateway response")
        
        return customer_id

    def cancel_subscription(
        self,
        user_id: str,
        subscription_id: str,
    ) -> None:

        url = f"{self.URL_BASE}/subscriptions/{subscription_id}/cancel"
        response = requests.post(url, headers=self.headers, timeout=30)
        response.raise_for_status()
