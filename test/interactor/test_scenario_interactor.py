from datetime import datetime
from uuid import UUID

import pytest
from faker import Faker

from core.interactor.scenario.scenario_interactor import ScenarioInteractor
from core.interactor.scenario.dto import CreateScenarioDTO, UpdateScenarioDTO
from core.interface.repository import ScenarioRepository
from core.model import ScenarioModel
from core.shared.errors import (
    MissingRequiredFieldError,
    ScenarioKeyAlreadyExistsError,
    ScenarioNotFoundError,
    ScenarioPermissionDeniedError,
)

fake = Faker()


def make_scenario(
    creator_id: str = None,
    key: str = "test-key",
) -> ScenarioModel:
    return ScenarioModel(
        id=fake.uuid4(),
        creator_id=creator_id or fake.uuid4(),
        key=key,
        name="Test Scenario",
        description="A test scenario",
        ai_role_definition="You are a teacher",
        user_role_definition="You are a student",
        is_public=False,
        created_at=datetime.now(),
    )


class TestCreateScenario:

    @pytest.fixture
    def interactor(self, scenario_repository_mock: ScenarioRepository):
        return ScenarioInteractor(scenario_repository=scenario_repository_mock)

    def test_should_create_scenario_successfully(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        user_id = str(fake.uuid4())
        dto = CreateScenarioDTO(
            creator_id=user_id,
            key="my-scenario",
            name="My Scenario",
            description="A scenario description",
            ai_role_definition="AI role",
            user_role_definition="User role",
            is_public=True,
        )
        expected_scenario = make_scenario(creator_id=user_id, key=dto.key)

        scenario_repository_mock.get_by_key_and_creator_id.return_value = None
        scenario_repository_mock.create.return_value = expected_scenario

        result = interactor.create_scenario(dto=dto)

        scenario_repository_mock.get_by_key_and_creator_id.assert_called_once_with(
            key=dto.key,
            creator_id=dto.creator_id,
        )
        scenario_repository_mock.create.assert_called_once_with(
            creator_id=dto.creator_id,
            key=dto.key,
            name=dto.name,
            description=dto.description,
            ai_role_definition=dto.ai_role_definition,
            user_role_definition=dto.user_role_definition,
            is_public=dto.is_public,
        )
        assert result == expected_scenario

    def test_should_raise_when_key_already_exists(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        dto = CreateScenarioDTO(
            creator_id=str(fake.uuid4()),
            key="existing-key",
            name="Name",
            description="Desc",
            ai_role_definition="AI",
            user_role_definition="User",
        )
        scenario_repository_mock.get_by_key_and_creator_id.return_value = make_scenario(
            key=dto.key,
        )

        with pytest.raises(ScenarioKeyAlreadyExistsError):
            interactor.create_scenario(dto=dto)

        scenario_repository_mock.create.assert_not_called()


class TestListUserScenarios:

    @pytest.fixture
    def interactor(self, scenario_repository_mock: ScenarioRepository):
        return ScenarioInteractor(scenario_repository=scenario_repository_mock)

    def test_should_list_user_scenarios(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        user_id = str(fake.uuid4())
        expected_scenarios = [
            make_scenario(creator_id=user_id, key="key-1"),
            make_scenario(creator_id=user_id, key="key-2"),
        ]
        scenario_repository_mock.list_by_creator_id.return_value = expected_scenarios

        result = interactor.list_user_scenarios(user_id=user_id)

        scenario_repository_mock.list_by_creator_id.assert_called_once_with(creator_id=user_id)
        assert result == expected_scenarios


class TestUpdateScenario:

    @pytest.fixture
    def interactor(self, scenario_repository_mock: ScenarioRepository):
        return ScenarioInteractor(scenario_repository=scenario_repository_mock)

    def test_should_update_scenario_successfully(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        user_id = str(fake.uuid4())
        scenario_id = str(fake.uuid4())
        existing_scenario = make_scenario(creator_id=user_id, key="old-key")
        updated_scenario = make_scenario(creator_id=user_id, key="new-key")

        dto = UpdateScenarioDTO(
            scenario_id=scenario_id,
            name="Updated Name",
            key="new-key",
        )

        scenario_repository_mock.get_by_id.return_value = existing_scenario
        scenario_repository_mock.get_by_key.return_value = None
        scenario_repository_mock.update.return_value = updated_scenario

        result = interactor.update_scenario(user_id=user_id, dto=dto)

        scenario_repository_mock.get_by_id.assert_called_once_with(scenario_id=scenario_id)
        scenario_repository_mock.update.assert_called_once_with(
            scenario_id=dto.scenario_id,
            key=dto.key,
            name=dto.name,
            description=dto.description,
            ai_role_definition=dto.ai_role_definition,
            user_role_definition=dto.user_role_definition,
            is_public=dto.is_public,
        )
        assert result == updated_scenario

    def test_should_not_check_key_uniqueness_when_key_unchanged(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        user_id = str(fake.uuid4())
        existing_scenario = make_scenario(creator_id=user_id, key="same-key")

        dto = UpdateScenarioDTO(
            scenario_id=str(fake.uuid4()),
            key="same-key",
            name="New Name",
        )

        scenario_repository_mock.get_by_id.return_value = existing_scenario
        scenario_repository_mock.update.return_value = existing_scenario

        interactor.update_scenario(user_id=user_id, dto=dto)

        # key comparison should short-circuit without hitting get_by_key
        scenario_repository_mock.get_by_key.assert_not_called()

    def test_should_raise_when_scenario_not_found(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        scenario_repository_mock.get_by_id.return_value = None

        with pytest.raises(ScenarioNotFoundError):
            interactor.update_scenario(
                user_id=str(fake.uuid4()),
                dto=UpdateScenarioDTO(
                    scenario_id=str(fake.uuid4()),
                    name="Name",
                ),
            )

        scenario_repository_mock.update.assert_not_called()

    def test_should_raise_when_user_is_not_the_creator(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        other_user_id = str(fake.uuid4())
        existing_scenario = make_scenario(creator_id=str(fake.uuid4()))
        scenario_repository_mock.get_by_id.return_value = existing_scenario

        with pytest.raises(ScenarioPermissionDeniedError):
            interactor.update_scenario(
                user_id=other_user_id,
                dto=UpdateScenarioDTO(
                    scenario_id=str(fake.uuid4()),
                    name="Name",
                ),
            )

        scenario_repository_mock.update.assert_not_called()

    def test_should_raise_when_payload_is_empty(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        user_id = str(fake.uuid4())
        existing_scenario = make_scenario(creator_id=user_id)
        scenario_repository_mock.get_by_id.return_value = existing_scenario

        with pytest.raises(MissingRequiredFieldError):
            interactor.update_scenario(
                user_id=user_id,
                dto=UpdateScenarioDTO(scenario_id=str(fake.uuid4())),
            )

        scenario_repository_mock.update.assert_not_called()

    def test_should_raise_when_new_key_already_taken(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        user_id = str(fake.uuid4())
        existing_scenario = make_scenario(creator_id=user_id, key="current-key")

        scenario_repository_mock.get_by_id.return_value = existing_scenario
        scenario_repository_mock.get_by_key.return_value = make_scenario(key="taken-key")

        with pytest.raises(ScenarioKeyAlreadyExistsError):
            interactor.update_scenario(
                user_id=user_id,
                dto=UpdateScenarioDTO(
                    scenario_id=str(fake.uuid4()),
                    key="taken-key",
                ),
            )

        scenario_repository_mock.update.assert_not_called()


class TestDeleteScenario:

    @pytest.fixture
    def interactor(self, scenario_repository_mock: ScenarioRepository):
        return ScenarioInteractor(scenario_repository=scenario_repository_mock)

    def test_should_delete_scenario_successfully(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        user_id = str(fake.uuid4())
        scenario_id = str(fake.uuid4())
        existing_scenario = make_scenario(creator_id=user_id)

        scenario_repository_mock.get_by_id.return_value = existing_scenario

        interactor.delete_scenario(user_id=user_id, scenario_id=scenario_id)

        scenario_repository_mock.get_by_id.assert_called_once_with(scenario_id=scenario_id)
        scenario_repository_mock.delete.assert_called_once_with(scenario_id=scenario_id)

    def test_should_raise_when_scenario_not_found(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        scenario_repository_mock.get_by_id.return_value = None

        with pytest.raises(ScenarioNotFoundError):
            interactor.delete_scenario(
                user_id=str(fake.uuid4()),
                scenario_id=str(fake.uuid4()),
            )

        scenario_repository_mock.delete.assert_not_called()

    def test_should_raise_when_user_is_not_the_creator(
        self,
        interactor: ScenarioInteractor,
        scenario_repository_mock: ScenarioRepository,
    ) -> None:

        other_user_id = str(fake.uuid4())
        existing_scenario = make_scenario(creator_id=str(fake.uuid4()))
        scenario_repository_mock.get_by_id.return_value = existing_scenario

        with pytest.raises(ScenarioPermissionDeniedError):
            interactor.delete_scenario(
                user_id=other_user_id,
                scenario_id=str(fake.uuid4()),
            )

        scenario_repository_mock.delete.assert_not_called()
