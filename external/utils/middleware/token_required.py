import jwt
import os
from functools import wraps
from flask import jsonify, make_response, request, abort
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def token_required(f):
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('authToken', None)
        if not token:
            return jsonify({"error": "Token ausente"}), 401
        
        try:
            data = jwt.decode(
                jwt=token, 
                key=os.getenv("TOKEN_SECRET_KEY"), 
                algorithms=['HS256'],
            )
            user_id = data['userId']

        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, Exception) as e:
            response = make_response(jsonify({"error": "Sessão inválida", "reason": str(e)}), 401)
            response.delete_cookie('authToken')
            return response
    
        return f(user_id, *args, **kwargs)
    
    return decorated