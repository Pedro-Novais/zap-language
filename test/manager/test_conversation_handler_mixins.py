from unittest.mock import Mock

import pytest

from core.manager.factory.handlers.conversation_handler import CommandHandlerMixin, StudySessionMixin
from core.model.enum import ConversationSessionsState
from core.shared.errors import GlobalIALockError, SessionActiveError, SessionStateInvalidError


class DummyCommandHandler(CommandHandlerMixin):

    def is_command(self, message: str) -> bool:
        return message.startswith("/")


class TestCommandHandlerMixin:

    def test_extract_key_after_command_returns_normalized_key(self) -> None:
        key = DummyCommandHandler._extract_key_after_command("/scenario AeroPorto")
        assert key == "aeroporto"

    def test_extract_key_after_command_returns_none_without_arg(self) -> None:
        key = DummyCommandHandler._extract_key_after_command("/scenario")
        assert key is None

    def test_extract_key_after_command_returns_none_for_short_arg(self) -> None:
        key = DummyCommandHandler._extract_key_after_command("/x a")
        assert key is None


class TestStudySessionMixin:

    def test_check_ia_lock_raises_when_locked(self) -> None:
        redis_service = Mock()
        redis_service.has_lock_global_ia.return_value = True

        with pytest.raises(GlobalIALockError):
            StudySessionMixin._check_ia_lock(
                phone="5511999999999",
                redis_service=redis_service,
            )

    def test_check_ia_lock_passes_when_unlocked(self) -> None:
        redis_service = Mock()
        redis_service.has_lock_global_ia.return_value = False

        StudySessionMixin._check_ia_lock(
            phone="5511999999999",
            redis_service=redis_service,
        )

    def test_verify_session_interrupt_raises_when_practicing(self) -> None:
        session = Mock(status=ConversationSessionsState.PRACTICING)

        with pytest.raises(SessionActiveError):
            StudySessionMixin._verify_session_interrupt(session=session)

    def test_verify_session_interrupt_passes_for_initialized(self) -> None:
        session = Mock(status=ConversationSessionsState.INITIALIZED)

        StudySessionMixin._verify_session_interrupt(session=session)

    def test_verify_session_interrupt_passes_for_awaiting_definition(self) -> None:
        session = Mock(status=ConversationSessionsState.AWAITING_DEFINITION)

        StudySessionMixin._verify_session_interrupt(session=session)

    def test_verify_session_interrupt_raises_for_invalid_state(self) -> None:
        session = Mock(status=ConversationSessionsState.ERROR)

        with pytest.raises(SessionStateInvalidError):
            StudySessionMixin._verify_session_interrupt(session=session)
