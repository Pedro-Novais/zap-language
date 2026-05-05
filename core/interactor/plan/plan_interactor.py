from loguru import logger
from typing import List

from core.interface.repository import PlanRepository
from core.model import PlanModel
from .dto import CreatePlanDTO


class PlanInteractor:
    
    MAX_FREE_PLAN = 1

    def __init__(
        self,
        plan_repository: PlanRepository,
    ) -> None:

        self.plan_repository = plan_repository
        self.plans_cache: List[PlanModel] = []

    def get_all_plans(self) -> List[PlanModel]:
        logger.info("Getting all plans")
        if not self.plans_cache:
            self.plans_cache = self.plan_repository.get_all()
            exceeded = self.__is_free_plan_limit_exceeded()
            if exceeded:
                raise RuntimeError("Cannot have more than one free plan")

        return self.plans_cache

    def create_plan(self, dto: CreatePlanDTO) -> PlanModel:
        logger.info(f"Creating plan: {dto.name}")
        plan = self.plan_repository.create(
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
            is_free=dto.is_free,
        )
        self.plans_cache = []
        return plan
    
    def __is_free_plan_limit_exceeded(
        self, 
    ) -> bool:
        
        quantity_free_plan = 0
        for plan in self.plans_cache:
            if plan.is_free:
                quantity_free_plan += 1
                
        return quantity_free_plan > self.MAX_FREE_PLAN
