from datetime import datetime, timezone

from loguru import logger

from core.interface.repository import SubscriptionRepository
from core.interface.service import SubscriptionPaymentService
from core.shared.errors import (
    ActiveSubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)
from .dto import SubscriptionRequestDTO, SubscriptionResponseDTO


class SubscriptionInteractor:

    def __init__(
        self,
        subscription_repository: SubscriptionRepository,
        subscription_payment_service: SubscriptionPaymentService,
    ) -> None:
        self.subscription_repository = subscription_repository
        self.subscription_payment_service = subscription_payment_service

    def get_user_subscription(
        self,
        subscription_request_dto: SubscriptionRequestDTO,
    ) -> SubscriptionResponseDTO:
        logger.info(f"Getting active subscription for user: {subscription_request_dto.user_id}")

        subscription = self.subscription_repository.get_active_by_user_id(
            user_id=subscription_request_dto.user_id,
        )
        if not subscription:
            raise SubscriptionNotFoundError()

        return SubscriptionResponseDTO(
            success=True,
            message="Assinatura ativa encontrada",
            subscription=subscription,
        )

    def create_user_subscription(
        self,
        subscription_request_dto: SubscriptionRequestDTO,
    ) -> SubscriptionResponseDTO:
        logger.info(
            f"Creating subscription for user: {subscription_request_dto.user_id}, "
            f"plan: {subscription_request_dto.plan_id}"
        )

        current_subscription = self.subscription_repository.get_active_by_user_id(
            user_id=subscription_request_dto.user_id,
        )
        if current_subscription:
            raise ActiveSubscriptionAlreadyExistsError()

        status, gateway, expires_at = self.subscription_payment_service.create_subscription(
            user_id=subscription_request_dto.user_id,
            plan_id=subscription_request_dto.plan_id,
        )

        started_at = datetime.now(timezone.utc)
        subscription = self.subscription_repository.create(
            user_id=subscription_request_dto.user_id,
            plan_id=subscription_request_dto.plan_id,
            started_at=started_at,
            expires_at=expires_at,
            status=status,
            is_active=True,
            gateway=gateway,
        )

        return SubscriptionResponseDTO(
            success=True,
            message="Assinatura criada com sucesso",
            subscription=subscription,
        )

    def cancel_user_subscription(
        self,
        subscription_request_dto: SubscriptionRequestDTO,
    ) -> SubscriptionResponseDTO:
        logger.info(f"Canceling active subscription for user: {subscription_request_dto.user_id}")

        subscription = self.subscription_repository.get_active_by_user_id(
            user_id=subscription_request_dto.user_id,
        )
        if not subscription:
            raise SubscriptionNotFoundError()

        self.subscription_payment_service.cancel_subscription(
            user_id=subscription_request_dto.user_id,
            subscription_id=str(subscription.id),
        )

        canceled_at = datetime.now(timezone.utc)
        updated_subscription = self.subscription_repository.cancel_active_by_user_id(
            user_id=subscription_request_dto.user_id,
            canceled_at=canceled_at,
        )
        if not updated_subscription:
            raise SubscriptionNotFoundError()

        return SubscriptionResponseDTO(
            success=True,
            message="Assinatura cancelada com sucesso",
            subscription=updated_subscription,
        )
