import os
import requests
import logging

from core.interface.service import WhatsappService
from core.shared.errors import ErrorSendingMessageToWhatsapp

logger = logging.getLogger(__name__)


class ZApiService(WhatsappService):
    
    ZAPI_BASE_URL = "https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}"
    
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Client-Token": os.getenv("ZAPI_SECURITY_TOKEN"),
        }
        
        self.zapi_base_url = self.ZAPI_BASE_URL.format(
            ZAPI_INSTANCE_ID=os.getenv("ZAPI_INSTANCE_ID"),
            ZAPI_TOKEN=os.getenv("ZAPI_TOKEN"),
        )
        
    def send_text(
        self, 
        phone: str, 
        message: str,
    ) -> None:
        
        payload = {
            "phone": phone,
            "message": message,
        }

        try:
            response = requests.post(
                url=f"{self.zapi_base_url}/send-text", 
                json=payload, 
                headers=self.headers,
            )
            response.raise_for_status()
            logger.info(f"Message sent to {phone}")
            
        except Exception as e:
            logger.error(f"Error sending message via Z-API: {e}")
            raise ErrorSendingMessageToWhatsapp(error=e)