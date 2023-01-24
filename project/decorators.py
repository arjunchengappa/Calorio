from cryptography.fernet import InvalidToken
from flask import request
from base64 import b64decode

from project.encryption import fernet
from project.schemas import UserSchema

user_schema = UserSchema()


def require_login(function):
    """
    Checks if a user is logged in using the cookies set on successfull login or signup.
    """
    def wrapper(**kwargs):
        try:
            auth = request.headers.get('X-User-Auth').encode()
            email, password = b64decode(auth).decode().split(':')

            user = user_schema.query_user(email, password)

            if not user:
                return {"message": "User not logged in."}, 403

            kwargs['user'] = user
            return function(**kwargs)

        except (ValueError, InvalidToken):
            return {"message": "User not logged in."}, 403

    wrapper.__name__ = f"{function.__name__}_wrapper"
    return wrapper


def require_admin(function):
    def wrapper(**kwargs):
        try:
            auth = request.headers.get('X-User-Auth').encode()
            email, password = b64decode(auth).decode().split(':')

            user = user_schema.query_user(email, password)

            if not user:
                return {"message": "User not logged in."}, 403

            if not user.is_admin:
                return {"message": "Access only for Admins"}

            return function(**kwargs)
        except ValueError:
            return {"message": "User not logged in."}, 403

    wrapper.__name__ = f"{function.__name__}_wrapper"
    return wrapper
