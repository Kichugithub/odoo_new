import jwt
import os
from functools import wraps
from odoo.http import request
from dotenv import load_dotenv

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "default_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"status": "error", "message": "Missing or invalid Authorization header"}

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            uid = payload.get('user_id')
            uid = uid.get('uid')

            if not uid:
                return {"status": "error", "message": "Invalid token payload: user_id missing"}

            # Update Odoo environment for this user (instead of request.uid = uid)
            request.update_env(user=uid)

        except jwt.ExpiredSignatureError:
            return {"status": "error", "message": "Token has expired"}
        except jwt.InvalidTokenError:
            return {"status": "error", "message": "Invalid token"}

        return func(*args, **kwargs)

    return wrapper
