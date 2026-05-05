from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .study_settings_controller import StudySettingsController
    from .user_controller import UserController
    from .subscription_controller import SubscriptionController
    from .scenario_controller import ScenarioController
    from .auth_controller import AuthController

__all__ = [
    "StudySettingsController",
    "UserController",
    "SubscriptionController",
    "ScenarioController",
    "AuthController",
]


def __getattr__(name: str):
    if name == "StudySettingsController":
        return import_module(".study_settings_controller", __name__).StudySettingsController
    if name == "UserController":
        return import_module(".user_controller", __name__).UserController
    if name == "SubscriptionController":
        return import_module(".subscription_controller", __name__).SubscriptionController
    if name == "ScenarioController":
        return import_module(".scenario_controller", __name__).ScenarioController
    if name == "AuthController":
        return import_module(".auth_controller", __name__).AuthController
    raise AttributeError(f"module {__name__} has no attribute {name}")
