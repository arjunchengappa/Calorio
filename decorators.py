from flask import request

from encryption import fernet
from schemas import UserSchema


def require_login(function):
    """
    Checks if a user is logged in using the cookies set on successfull login or signup.
    """
    def wrapper(**kwargs):
        try:
            email, password = request.cookies.get('logged_in').split("$")
            decrypted_password = fernet.decrypt(password).decode()

            user_schema = UserSchema()

            user = user_schema.query_user(email, decrypted_password)

            if not user:
                return {"message": "User not logged in."}, 403

            kwargs['user'] = user
            return function(**kwargs)

        except ValueError:
            return {"message": "User not logged in."}, 403

    wrapper.__name__ = f"{function.__name__}_wrapper"
    return wrapper


def require_admin(function):
    def wrapper(**kwargs):
        try:
            email, password = request.cookies.get('logged_in').split("$")
            user = db_service.query_user(email, password, True)

            if not user:
                return {"message": "User not logged in."}, 403

            if not user.is_admin:
                return {"message": "Access only for Admins"}

            return function(**kwargs)
        except ValueError:
            return {"message": "User not logged in."}, 403

    wrapper.__name__ = f"{function.__name__}_wrapper"
    return wrapper
