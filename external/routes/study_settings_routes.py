from flask import (
    Flask,
    Blueprint,
    request,
    Response,
)

from external.controllers import StudySettingsController
from external.utils.middleware import token_required


class StudySettingsRoute:

    def __init__(
        self,
        app: Flask,
        base_route: str,
    ) -> None:

        self.app = app
        self.study_settings_bp = Blueprint('study_settings', __name__, url_prefix=f'{base_route}/study-settings')
        self.study_settings_controller = StudySettingsController()

    def register_routes(
        self,
    ) -> None:

        @self.study_settings_bp.route("", methods=['POST'])
        @token_required
        def create_study_teacher(user_id: str) -> Response:
            return self.study_settings_controller.create_study_teacher(
                user_id=user_id,                
                request=request.json,
            )
        
        self.app.register_blueprint(blueprint=self.study_settings_bp)
