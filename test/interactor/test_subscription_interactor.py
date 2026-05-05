from datetime import datetime, timezone, timedelta

import pytest
from faker import Faker

from core.interactor.subscription.subscription_interactor import SubscriptionInteractor
from core.interactor.subscription.dto import SubscriptionRequestDTO
from core.interface.repository import SubscriptionRepository
from core.interface.service import PaymentService
from core.model import SubscriptionModel
from core.shared.errors import (
    ActiveSubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)

fake = Faker()


class TestSubscriptionInteractor:

    @pytest.fixture
    def interactor(
        self,
        subscription_repository_mock: SubscriptionRepository,
        subscription_payment_service_mock: PaymentService,
    ):
        return SubscriptionInteractor(
            subscription_repository=subscription_repository_mock,
            subscription_payment_service=subscription_payment_service_mock,
        )

    def test_get_user_subscription_success(
        self,
        interactor: SubscriptionInteractor,
        subscription_repository_mock: SubscriptionRepository,
    ) -> None:
        user_id = fake.uuid4()
        expected_subscription = SubscriptionModel(
            id=fake.uuid4(),
            user_id=user_id,
            plan_id=fake.uuid4(),
            status="active",
            started_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
            is_active=True,
            gateway="generic",
            plan=None,
        )
        subscription_repository_mock.get_active_by_user_id.return_value = expected_subscription
        request_dto = SubscriptionRequestDTO(user_id=user_id)

        result = interactor.get_user_subscription(subscription_request_dto=request_dto)

        subscription_repository_mock.get_active_by_user_id.assert_called_once_with(user_id=user_id)
        assert result.success is True
        assert result.message == "Assinatura ativa encontrada"
        assert result.subscription == expected_subscription

    def test_get_user_subscription_not_found(
        self,
        interactor: SubscriptionInteractor,
        subscription_repository_mock: SubscriptionRepository,
    ) -> None:
        user_id = fake.uuid4()
        subscription_repository_mock.get_active_by_user_id.return_value = None
        request_dto = SubscriptionRequestDTO(user_id=user_id)

        with pytest.raises(SubscriptionNotFoundError):
            interactor.get_user_subscription(subscription_request_dto=request_dto)

    def test_create_user_subscription_success(
        self,
        interactor: SubscriptionInteractor,
        subscription_repository_mock: SubscriptionRepository,
        subscription_payment_service_mock: PaymentService,
    ) -> None:
        user_id = fake.uuid4()
        plan_id = fake.uuid4()

        subscription_repository_mock.get_active_by_user_id.return_value = None
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        subscription_payment_service_mock.create_subscription.return_value = ("active", "generic", expires_at)

        expected_subscription = SubscriptionModel(
            id=fake.uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            status="active",
            started_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            is_active=True,
            gateway="generic",
            plan=None,
        )
        subscription_repository_mock.create.return_value = expected_subscription
        request_dto = SubscriptionRequestDTO(user_id=user_id, plan_id=plan_id)

        result = interactor.create_user_subscription(subscription_request_dto=request_dto)

        subscription_repository_mock.get_active_by_user_id.assert_called_once_with(user_id=user_id)
        subscription_payment_service_mock.create_subscription.assert_called_once_with(user_id=user_id, plan_id=plan_id)
        subscription_repository_mock.create.assert_called_once()
        assert result.success is True
        assert result.message == "Assinatura criada com sucesso"
        assert result.subscription == expected_subscription

    def test_create_user_subscription_when_active_exists(
        self,
        interactor: SubscriptionInteractor,
        subscription_repository_mock: SubscriptionRepository,
    ) -> None:
        user_id = fake.uuid4()
        plan_id = fake.uuid4()
        active_subscription = SubscriptionModel(
            id=fake.uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            status="active",
            started_at=datetime.now(timezone.utc),
            expires_at=None,
            is_active=True,
            gateway="generic",
            plan=None,
        )
        subscription_repository_mock.get_active_by_user_id.return_value = active_subscription
        request_dto = SubscriptionRequestDTO(user_id=user_id, plan_id=plan_id)

        with pytest.raises(ActiveSubscriptionAlreadyExistsError):
            interactor.create_user_subscription(subscription_request_dto=request_dto)

    def test_cancel_user_subscription_success(
        self,
        interactor: SubscriptionInteractor,
        subscription_repository_mock: SubscriptionRepository,
        subscription_payment_service_mock: PaymentService,
    ) -> None:
        user_id = fake.uuid4()
        plan_id = fake.uuid4()
        active_subscription = SubscriptionModel(
            id=fake.uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            status="active",
            started_at=datetime.now(timezone.utc),
            expires_at=None,
            is_active=True,
            gateway="generic",
            plan=None,
        )
        canceled_subscription = SubscriptionModel(
            id=active_subscription.id,
            user_id=user_id,
            plan_id=plan_id,
            status="canceled",
            started_at=active_subscription.started_at,
            expires_at=datetime.now(timezone.utc),
            is_active=False,
            gateway="generic",
            plan=None,
        )

        subscription_repository_mock.get_active_by_user_id.return_value = active_subscription
        subscription_repository_mock.cancel_active_by_user_id.return_value = canceled_subscription
        request_dto = SubscriptionRequestDTO(user_id=user_id)

        result = interactor.cancel_user_subscription(subscription_request_dto=request_dto)

        subscription_payment_service_mock.cancel_subscription.assert_called_once_with(
            user_id=user_id,
            subscription_id=str(active_subscription.id),
        )
        subscription_repository_mock.cancel_active_by_user_id.assert_called_once()
        assert result.success is True
        assert result.message == "Assinatura cancelada com sucesso"
        assert result.subscription == canceled_subscription

    def test_cancel_user_subscription_not_found(
        self,
        interactor: SubscriptionInteractor,
        subscription_repository_mock: SubscriptionRepository,
    ) -> None:
        user_id = fake.uuid4()
        subscription_repository_mock.get_active_by_user_id.return_value = None
        request_dto = SubscriptionRequestDTO(user_id=user_id)

        with pytest.raises(SubscriptionNotFoundError):
            interactor.cancel_user_subscription(subscription_request_dto=request_dto)
