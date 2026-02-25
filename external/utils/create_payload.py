from datetime import datetime, timezone
from typing import Dict, Union

def create_payload_to_queue(
        self,
        phone: str,
        message_text: str,
        attempt: int = 0,
    ) -> Dict[str, Union[str, int]]:

        return {
            "phone": phone,
            "message": message_text,
            "attempt": attempt,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }