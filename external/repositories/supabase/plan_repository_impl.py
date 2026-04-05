from typing import Any, List, Optional

from external.database.models import Plan
from external.database.connection import get_db_session
from core.interface.repository import PlanRepository
from core.model import PlanModel


class PlanRepositoryImpl(PlanRepository):

    def get_all(self) -> List[PlanModel]:
        with get_db_session() as session:
            plans = session.query(Plan).all()
            return [self._to_plan_model(plan=plan) for plan in plans]

    def create(
        self,
        name: str,
        slug: str,
        price: int,
        description: str,
        currency: str,
        billing_cycle: str,
        message_limit: int,
        features: Any,
        is_active: bool,
        trial_days: int,
        stripe_price_id: Optional[str],
    ) -> PlanModel:
        with get_db_session() as session:
            plan = Plan(
                name=name,
                slug=slug,
                price=price,
                description=description,
                currency=currency,
                billing_cycle=billing_cycle,
                message_limit=message_limit,
                features=features if features is not None else [],
                is_active=is_active,
                trial_days=trial_days,
                stripe_price_id=stripe_price_id,
            )
            session.add(plan)
            session.commit()
            session.refresh(plan)
            return self._to_plan_model(plan=plan)

    @staticmethod
    def _to_plan_model(plan: Plan) -> PlanModel:
        return PlanModel(
            id=plan.id,
            name=plan.name,
            slug=plan.slug,
            description=plan.description,
            price=plan.price,
            currency=plan.currency,
            billing_cycle=plan.billing_cycle,
            stripe_price_id=plan.stripe_price_id,
            message_limit=plan.message_limit,
            features=plan.features,
            is_active=plan.is_active,
            trial_days=plan.trial_days,
        )
