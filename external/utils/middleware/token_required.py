import jwt
import os
from functools import wraps
from flask import (
    jsonify, 
    make_response, 
    request,
)
from jwt.exceptions import (
    ExpiredSignatureError, 
    InvalidTokenError,
)

from external.services import redis_client
from external.repositories import UserRepositoryImpl


user_repository = UserRepositoryImpl()


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
            cache_key = f"user_active:{user_id}"
            try:
                if redis_client.get(cache_key):
                    pass 
                else:
                    user = user_repository.get_user_by_id(user_id=user_id)
                    if not user:
                        return jsonify({"error": "Usuário não encontrado"}), 401
                    
                    redis_client.setex(cache_key, 300, "1")
                    
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
