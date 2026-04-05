import os
from functools import wraps

import jwt
from flask import jsonify, make_response, request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from loguru import logger

from external.container import user_repository


def admin_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.cookies.get('authToken')
        if not token:
            return jsonify({"error": "Token ausente"}), 401

        try:
            data = jwt.decode(
                token,
                os.getenv("TOKEN_SECRET_KEY"),
                algorithms=['HS256'],
            )
            user_id = data['userId']

            user = user_repository.get_user_by_id(user_id=user_id)
            if not user:
                return jsonify({"error": "Usuário não encontrado"}), 401

            if not user.is_admin:
                return jsonify({"error": "Acesso restrito a administradores"}), 403

        except (ExpiredSignatureError, InvalidTokenError):
            response = make_response(jsonify({"error": "Sessão expirada"}), 401)
            response.delete_cookie('authToken')
            return response

        except Exception as e:
            logger.error(f"admin_required Middleware Error: {e}")
            return jsonify({"error": "Erro na autenticação"}), 500

        return f(user_id, *args, **kwargs)

    return decorated
