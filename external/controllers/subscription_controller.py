from typing import Any, Dict, Tuple

from flask import jsonify

from external.container import subscription_repository, subscription_payment_service
from external.utils import validate_request
from core.interactor import SubscriptionInteractor
from core.interactor.subscription.dto import SubscriptionRequestDTO


class SubscriptionController:

    def __init__(self) -> None:
        self.subscription_interactor = SubscriptionInteractor(
            subscription_repository=subscription_repository,
            subscription_payment_service=subscription_payment_service,
        )

    def get_user_subscription(self, user_id: str) -> Tuple[Dict[str, Any], int]:
        request_dto = SubscriptionRequestDTO(user_id=user_id)
        response_dto = self.subscription_interactor.get_user_subscription(
            subscription_request_dto=request_dto,
        )
        return jsonify(response_dto.model_dump(mode="json")), 200

    def create_user_subscription(self, user_id: str, request: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        validate_request(request=request, required_fields=["planId"])

        request_dto = SubscriptionRequestDTO(
            user_id=user_id,
            plan_id=request["planId"],
        )
        response_dto = self.subscription_interactor.create_user_subscription(
            subscription_request_dto=request_dto,
        )
        return jsonify(response_dto.model_dump(mode="json")), 201

    def cancel_user_subscription(self, user_id: str) -> Tuple[Dict[str, Any], int]:
        request_dto = SubscriptionRequestDTO(user_id=user_id)
        response_dto = self.subscription_interactor.cancel_user_subscription(
            subscription_request_dto=request_dto,
        )
        return jsonify(response_dto.model_dump(mode="json")), 200
