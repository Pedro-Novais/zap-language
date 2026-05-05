from datetime import datetime
from typing import Optional

from sqlalchemy.orm import joinedload
from sqlalchemy import desc

from external.database.models import Subscription
from external.database.connection import get_db_session
from core.interface.repository import SubscriptionRepository
from core.model import SubscriptionModel, PlanModel


class SubscriptionRepositoryImpl(SubscriptionRepository):

    def get_active_by_user_id(self, user_id: str) -> Optional[SubscriptionModel]:
        with get_db_session() as session:
            subscription = (
                session.query(Subscription)
                .options(joinedload(Subscription.plan))
                .filter(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True,
                )
                .first()
            )
            return self._to_subscription_model(subscription=subscription)

    def get_last_by_user_id(self, user_id: str) -> Optional[SubscriptionModel]:
        with get_db_session() as session:
            subscription = (
                session.query(Subscription)
                .options(joinedload(Subscription.plan))
                .filter(Subscription.user_id == user_id)
                .order_by(desc(Subscription.started_at))
                .first()
            )
            return self._to_subscription_model(subscription=subscription)

    def create(
        self,
        user_id: str,
        plan_id: str,
        started_at: datetime,
        expires_at: datetime | None,
        status: str,
        is_active: bool,
        gateway: str | None,
    ) -> SubscriptionModel:
        with get_db_session() as session:
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                status=status,
                started_at=started_at,
                expires_at=expires_at,
                is_active=is_active,
                gateway=gateway,
            )
            session.add(subscription)
            session.commit()
            session.refresh(subscription)

            subscription = (
                session.query(Subscription)
                .options(joinedload(Subscription.plan))
                .filter(Subscription.id == subscription.id)
                .first()
            )
            return self._to_subscription_model(subscription=subscription)

    def cancel_active_by_user_id(
        self,
        user_id: str,
        canceled_at: datetime,
    ) -> Optional[SubscriptionModel]:
        with get_db_session() as session:
            subscription = (
                session.query(Subscription)
                .filter(
                    Subscription.user_id == user_id,
                    Subscription.is_active == True,
                )
                .first()
            )
            if not subscription:
                return None

            subscription.is_active = False
            subscription.status = "canceled"
            subscription.expires_at = canceled_at
            session.commit()
            session.refresh(subscription)

            subscription = (
                session.query(Subscription)
                .options(joinedload(Subscription.plan))
                .filter(Subscription.id == subscription.id)
                .first()
            )
            return self._to_subscription_model(subscription=subscription)

    @staticmethod
    def _to_subscription_model(subscription: Optional[Subscription]) -> Optional[SubscriptionModel]:
        if not subscription:
            return None

        plan_model = None
        if subscription.plan:
            plan_model = PlanModel(
                id=subscription.plan.id,
                name=subscription.plan.name,
                slug=subscription.plan.slug,
                description=subscription.plan.description,
                price=subscription.plan.price,
                currency=subscription.plan.currency,
                billing_cycle=subscription.plan.billing_cycle,
                stripe_price_id=subscription.plan.stripe_price_id,
                message_limit=subscription.plan.message_limit,
                features=subscription.plan.features,
                is_active=subscription.plan.is_active,
                trial_days=subscription.plan.trial_days,
                is_free=subscription.plan.is_free,
            )

        return SubscriptionModel(
            id=subscription.id,
            user_id=subscription.user_id,
            plan_id=subscription.plan_id,
            status=subscription.status,
            started_at=subscription.started_at,
            expires_at=subscription.expires_at,
            is_active=subscription.is_active,
            gateway=subscription.gateway,
            plan=plan_model,
        )
