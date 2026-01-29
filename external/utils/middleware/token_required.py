import jwt
import os
from functools import wraps
from flask import request, abort
from dotenv import load_dotenv
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def token_required(f):
    
    @wraps(f)
    def decorated(*args, **kwargs):
        load_dotenv()
        user_id = None
        token = request.cookies.get('authToken')

        if not token:
            return abort(401)
        
        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
            user_id = data['userId']

        except ExpiredSignatureError:
            return abort(401)
        
        except InvalidTokenError:
            return abort(401)

        except Exception:
            return abort(401)
    
        return f(user_id, *args, **kwargs)
    
    return decorated