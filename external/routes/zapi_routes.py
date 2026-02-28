from flask import (
    Flask,
    Blueprint,
    request,
    Response,
    jsonify
)

from worker import process_whatsapp_message 


class ZapiRoute:

    def __init__(
        self,
        app: Flask,
        base_route: str,
    ) -> None:

        self.app = app
        self.zapi_bp = Blueprint('zapi', __name__, url_prefix=f'{base_route}/webhook/zapi')
        
    def register_routes(
        self,
    ) -> None:
        
        @self.zapi_bp.route("", methods=['POST'])
        def receive_message_external() -> Response:
            data = request.json
            if not data or 'text' not in data:
                return jsonify({"status": "ignored"}), 200
                
            if data.get('fromMe', False) is True:
                return jsonify({"status": "ignored_self"}), 200

            phone = data.get('phone', None)
            message = data['text'].get('message', None)

            if phone and message:
                process_whatsapp_message.delay(
                    phone=phone, 
                    message=message,
                )
                return jsonify({"status": "queued"}), 200
            
            return jsonify({"status": "error"}), 400
        

        self.app.register_blueprint(self.zapi_bp)
        