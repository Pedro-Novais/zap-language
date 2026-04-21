import os
from functools import wraps

import jwt
from flask import (
    jsonify, 
    make_response, 
    request,
)
from jwt.exceptions import (
    ExpiredSignatureError, 
    InvalidTokenError,
)
from loguru import logger

from core.shared.auth import get_auth_secret_key
from external.container import (
    redis_service,
    user_repository,
)


def token_required(f):
    
    @wraps(f)
    def decorated(*args, **kwargs):
        
        token = request.cookies.get('authToken')
        if not token:
            return jsonify({"error": "Token ausente"}), 401
        
        user_id = None
        try:
            data = jwt.decode(
                token, 
                get_auth_secret_key(), 
                algorithms=['HS256'],
            )
            user_id = data['userId']
            try:
                if redis_service.api_user_cached(user_id=user_id):
                    pass 
                else:
                    user = user_repository.get_user_by_id(user_id=user_id)
                    if not user:
                        return jsonify({"error": "Usuário não encontrado"}), 401
                    
                    redis_service.set_api_user_cached(user_id=user_id)
                    
            except Exception as exc:
                logger.error(f"Unknown error verifying user token: {exc}")

        except (ExpiredSignatureError, InvalidTokenError):
            response = make_response(jsonify({"error": "Sessão expirada"}), 401)
            response.delete_cookie('authToken')
            return response
        
        except Exception as e:
            logger.error(f"Middleware Error: {e}")
            return jsonify({"error": "Erro na autenticação"}), 500

        return f(user_id, *args, **kwargs)
    
    return decorated
