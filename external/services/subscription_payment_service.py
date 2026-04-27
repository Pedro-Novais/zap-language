from datetime import datetime, timedelta, timezone

from core.interface.service import SubscriptionPaymentService


class AbacatePaySubscriptionPaymentService(SubscriptionPaymentService):

    def create_subscription(
        self,
        user_id: str,
        plan_id: str,
    ) -> tuple[str, str, datetime]:

        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        return "active", "abacatepay", expires_at

    def cancel_subscription(
        self,
        user_id: str,
        subscription_id: str,
    ) -> None:

        return None
