from typing import Any, Dict, List, Tuple

from flask import jsonify

from external.container import plan_repository
from external.utils import validate_request
from core.interactor import PlanInteractor
from core.interactor.plan.dto import CreatePlanDTO


class PlanController:

    def __init__(self) -> None:
        self.plan_interactor = PlanInteractor(plan_repository=plan_repository)

    def get_plans(self) -> Tuple[List[Dict[str, Any]], int]:
        plans = self.plan_interactor.get_all_plans()
        plans_data = [plan.model_dump() for plan in plans]
        return jsonify(plans_data), 200

    def create_plan(self, request: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        validate_request(
            request=request,
            required_fields=["name", "slug", "price"],
        )
        dto = CreatePlanDTO(
            name=request["name"],
            slug=request["slug"],
            price=request["price"],
            description=request.get("description", ""),
            currency=request.get("currency", "BRL"),
            billing_cycle=request.get("billingCycle", "monthly"),
            message_limit=request.get("messageLimit", 0),
            features=request.get("features", []),
            is_active=request.get("isActive", True),
            trial_days=request.get("trialDays", 0),
            stripe_price_id=request.get("stripePriceId"),
        )
        plan = self.plan_interactor.create_plan(dto=dto)
        return jsonify(plan.model_dump()), 201
