import json
from typing import Dict, Union

from loguru import logger

from flask import (
    Flask,
    Blueprint,
    request,
    Response,
    jsonify
)

from external.controllers.zapi_controller import ZapiController
from external.services.redis_client import redis_client
from external.utils.create_payload import create_payload_to_queue

from core.manager.key import RedisKeyManager


class ZapiRoute:

    def __init__(
        self,
        app: Flask,
        base_route: str,
    ) -> None:

        self.app = app
        self.zapi_bp = Blueprint('zapi', __name__, url_prefix=f'{base_route}/webhook/zapi')
        
        self.zapi_controller = ZapiController()

    def register_routes(
        self,
    ) -> None:
        
        @self.zapi_bp.route("/local", methods=['POST'])
        def receive_message_local() -> Response:
            data = request.json
            if not data or 'text' not in data:
                return jsonify({"status": "ignored"}), 200
                
            if data.get('fromMe', False) is True:
                return jsonify({"status": "ignored_self"}), 200

            phone = data.get('phone', None)
            message = data['text'].get('message', None)

            if phone and message:
                response = self.zapi_controller.receive_message(
                    message=message,
                )
                return jsonify({"status": "queued", "id": 1, "response": response}), 200
            
            return jsonify({"status": "error"}), 400
        
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
                self.add_message_to_queue(
                    phone=phone, 
                    message_text=message,
                )
                return jsonify({"status": "queued"}), 200
            
            return jsonify({"status": "error"}), 400
        

        self.app.register_blueprint(self.zapi_bp)
        
    def add_message_to_queue(
        self, 
        phone: str, 
        message_text: str,
    ) -> None:

        logger.info(f"📥 Recebida mensagem de {phone} via ZAPI. Adicionando à fila de processamento.")
        payload = create_payload_to_queue(
            phone=phone, 
            message_text=message_text,
        )
        try:
            redis_client.lpush(RedisKeyManager.queue_whatasapp_messages(), json.dumps(payload))
        except Exception as e:
            pass
