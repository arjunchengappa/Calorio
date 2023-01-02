from validators import validate_user
from flask import request

def require_login(function):
    """
    Checks if a user is logged in using the cookies set on successfull login or signup.
    """
    def wrapper(**kwargs):
        try:
            email, password = request.cookies.get('logged_in').split("$")
            user = validate_user(email, password.encode())
            if not user:
                return {"message": "User not logged in."}, 403
            kwargs['user'] = user
            return function(**kwargs)
        except ValueError:
            return {"message": "User not logged in."}, 403

    wrapper.__name__ = f"{function.__name__}_wrapper"
    return wrapper