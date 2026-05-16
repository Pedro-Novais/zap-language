from datetime import datetime, timezone, timedelta

import pytest
from faker import Faker

from core.interactor.subscription.subscription_interactor import SubscriptionInteractor
from core.interactor.subscription.dto import SubscriptionRequestDTO
from unittest.mock import create_autospec

from core.interface.repository import PlanRepository, SubscriptionRepository, UserRepository
from core.interface.service import PaymentService
from core.model import SubscriptionModel, UserModel
from core.shared.errors import (
    ActiveSubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)

fake = Faker()


class TestSubscriptionInteractor:

    @pytest.fixture
    def plan_repository_mock(self) -> PlanRepository:
        return create_autospec(spec=PlanRepository, instance=True)

    @pytest.fixture
    def user_repository_mock(self) -> UserRepository:
        return create_autospec(spec=UserRepository, instance=True)

    @pytest.fixture
    def interactor(
        self,
        plan_repository_mock: PlanRepository,
        subscription_repository_mock: SubscriptionRepository,
        subscription_payment_service_mock: PaymentService,
        user_repository_mock: UserRepository,
    ):
        return SubscriptionInteractor(
            plan_repository=plan_repository_mock,
            subscription_repository=subscription_repository_mock,
            subscription_payment_service=subscription_payment_service_mock,
            user_repository=user_repository_mock,
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
        user_repository_mock: UserRepository,
    ) -> None:
        user_id = fake.uuid4()
        plan_id = fake.uuid4()

        subscription_repository_mock.get_active_by_user_id.return_value = None
        user_repository_mock.get_user_by_id.return_value = UserModel(
            id=user_id,
            email="subscriber@example.com",
            name="Subscriber",
            phone=None,
            whatsapp_enabled=False,
            is_valid=True,
            created_at=datetime.now(timezone.utc),
            google_id=None,
            last_login=None,
            payment_customer_id="cust-existing",
            study_settings=None,
            password="x",
            current_topic=None,
        )
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        subscription_payment_service_mock.create_subscription.return_value = ("active", "abacatepay", expires_at)

        expected_subscription = SubscriptionModel(
            id=fake.uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            status="active",
            started_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            is_active=True,
            gateway="abacatepay",
            plan=None,
        )
        subscription_repository_mock.create.return_value = expected_subscription
        request_dto = SubscriptionRequestDTO(user_id=user_id, plan_id=plan_id)

        result = interactor.create_user_subscription(subscription_request_dto=request_dto)

        subscription_repository_mock.get_active_by_user_id.assert_called_once_with(user_id=user_id)
        user_repository_mock.get_user_by_id.assert_called_once_with(user_id=user_id)
        subscription_payment_service_mock.create_subscription.assert_called_once_with(
            customer_id="cust-existing",
            plan_id=plan_id,
        )
        subscription_payment_service_mock.create_customer.assert_not_called()
        subscription_repository_mock.create.assert_called_once()
        assert result.success is True
        assert result.message == "Assinatura criada com sucesso"
        assert result.subscription == expected_subscription

    def test_create_user_subscription_creates_customer_when_missing(
        self,
        interactor: SubscriptionInteractor,
        subscription_repository_mock: SubscriptionRepository,
        subscription_payment_service_mock: PaymentService,
        user_repository_mock: UserRepository,
    ) -> None:
        user_id = fake.uuid4()
        plan_id = fake.uuid4()

        subscription_repository_mock.get_active_by_user_id.return_value = None
        user_repository_mock.get_user_by_id.return_value = UserModel(
            id=user_id,
            email="newsubscriber@example.com",
            name="New Subscriber",
            phone=None,
            whatsapp_enabled=False,
            created_at=datetime.now(timezone.utc),
            google_id=None,
            last_login=None,
            payment_customer_id=None,
            study_settings=None,
            password="x",
            current_topic=None,
        )
        subscription_payment_service_mock.create_customer.return_value = "cust-created"
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
        subscription_payment_service_mock.create_subscription.return_value = ("active", "abacatepay", expires_at)

        subscription_repository_mock.create.return_value = SubscriptionModel(
            id=fake.uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            status="active",
            started_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            is_active=True,
            gateway="abacatepay",
            plan=None,
        )
        request_dto = SubscriptionRequestDTO(user_id=user_id, plan_id=plan_id)

        result = interactor.create_user_subscription(subscription_request_dto=request_dto)

        subscription_payment_service_mock.create_customer.assert_called_once_with(
            user_id=str(user_id),
            name="New Subscriber",
            email="newsubscriber@example.com",
        )
        user_repository_mock.update_payment_customer_id.assert_called_once_with(
            user_id=str(user_id),
            payment_customer_id="cust-created",
        )
        subscription_payment_service_mock.create_subscription.assert_called_once_with(
            customer_id="cust-created",
            plan_id=plan_id,
        )
        assert result.success is True

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
