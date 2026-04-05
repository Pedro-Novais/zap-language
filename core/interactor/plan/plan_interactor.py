from loguru import logger
from typing import List

from core.interface.repository import PlanRepository
from core.model import PlanModel
from .dto import CreatePlanDTO


class PlanInteractor:

    def __init__(
        self,
        plan_repository: PlanRepository,
    ) -> None:

        self.plan_repository = plan_repository

    def get_all_plans(self) -> List[PlanModel]:
        logger.info("Getting all plans")
        return self.plan_repository.get_all()

    def create_plan(self, dto: CreatePlanDTO) -> PlanModel:
        logger.info(f"Creating plan: {dto.name}")
        return self.plan_repository.create(
            name=dto.name,
            slug=dto.slug,
            price=dto.price,
            description=dto.description,
            currency=dto.currency,
            billing_cycle=dto.billing_cycle,
            message_limit=dto.message_limit,
            features=dto.features if dto.features is not None else [],
            is_active=dto.is_active,
            trial_days=dto.trial_days,
            stripe_price_id=dto.stripe_price_id,
        )
