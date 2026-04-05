import pytest
from faker import Faker

from core.interactor.plan.plan_interactor import PlanInteractor
from core.interface.repository import PlanRepository
from core.model import PlanModel

fake = Faker()


class TestPlanInteractor:

    @pytest.fixture
    def interactor(self, plan_repository_mock: PlanRepository):
        return PlanInteractor(plan_repository=plan_repository_mock)

    def test_get_all_plans_success(
        self,
        interactor: PlanInteractor,
        plan_repository_mock: PlanRepository,
    ) -> None:
        plans = [
            PlanModel(
                id=fake.uuid4(),
                name="Basico",
                slug="basico-monthly",
                description="Plano inicial",
                price=2990,
                currency="BRL",
                billing_cycle="monthly",
                stripe_price_id="price_123",
                message_limit=300,
                features=["grammar-check"],
                is_active=True,
                trial_days=7,
            ),
            PlanModel(
                id=fake.uuid4(),
                name="Premium",
                slug="premium-monthly",
                description="Plano completo",
                price=7990,
                currency="BRL",
                billing_cycle="monthly",
                stripe_price_id="price_456",
                message_limit=2000,
                features=["grammar-check", "voice-support"],
                is_active=True,
                trial_days=14,
            ),
        ]
        plan_repository_mock.get_all.return_value = plans

        result = interactor.get_all_plans()

        plan_repository_mock.get_all.assert_called_once_with()
        assert result == plans

    def test_get_all_plans_empty(
        self,
        interactor: PlanInteractor,
        plan_repository_mock: PlanRepository,
    ) -> None:
        plan_repository_mock.get_all.return_value = []

        result = interactor.get_all_plans()

        plan_repository_mock.get_all.assert_called_once_with()
        assert result == []
