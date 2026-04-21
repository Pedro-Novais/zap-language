import os
from datetime import datetime, timedelta, timezone

import jwt


def get_auth_secret_key() -> str:
    secret_key = os.getenv("SECRET_KEY") or os.getenv("TOKEN_SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY or TOKEN_SECRET_KEY must be configured")
    return secret_key


def generate_auth_token(
    user_id: str,
) -> str:

    now = datetime.now(tz=timezone.utc)
    payload = {
        "userId": str(user_id),
        "exp": int((now + timedelta(days=7)).timestamp()),
        "iat": int(now.timestamp()),
    }
    return jwt.encode(
        payload=payload,
        key=get_auth_secret_key(),
        algorithm="HS256",
    )