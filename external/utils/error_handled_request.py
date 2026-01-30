from typing import Tuple

from flask import (
    Flask,
    jsonify,
)
from core.shared import ApplicationError

def register_error_handlers(
        app: Flask,
    ) -> None:

    @app.errorhandler(ApplicationError)
    def handle_application_error(
        error: ApplicationError,
    ) -> Tuple[dict, int]:
        
        response = jsonify({"messageError": error.message_error})
        if error.extra:
            response.json.update(error.extra)
            
        return response, error.status_code
