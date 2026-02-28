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
                os.getenv("TOKEN_SECRET_KEY"), 
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
                    
            except Exception as redis_err:
                print(f"Redis Error: {redis_err}")

        except (ExpiredSignatureError, InvalidTokenError):
            response = make_response(jsonify({"error": "Sessão expirada"}), 401)
            response.delete_cookie('authToken')
            return response
        
        except Exception as e:
            print(f"Middleware Error: {e}")
            return jsonify({"error": "Erro na autenticação"}), 500

        return f(user_id, *args, **kwargs)
    
    return decorated
