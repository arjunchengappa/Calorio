from flask.testing import FlaskClient

from project.encryption import fernet
from project.models import User
from project.schemas import UserSchema

user_schema = UserSchema()


def verify_user_cookie(user: User, cookie: str):
    cookie_email, cookie_password = cookie[10:].split("$")
    assert user.email == cookie_email
    assert user.password == fernet.decrypt(cookie_password).decode()


def test_new_user_signup_success(client: FlaskClient) -> None:
    response = client.post("/signup", data={
        "email": "test_user@calorio.com",
        "password": "password123",
        "first_name": "test",
        "last_name": "user",
    })

    # Test if database entry is is as expected
    user = User.query.filter().first()
    assert user_schema.dump(user) == response.json["user"]

    # Test if response is as expected
    assert response.status_code == 201
    assert response.json == {
        "message": "Registration successful",
        "user": {
            "email": "test_user@calorio.com",
            "first_name": "test",
            "id": 1,
            "last_name": "user"
        }
    }

    # Verify if cookie is set properly
    verify_user_cookie(user, response.headers["Set-Cookie"])


def test_user_login_success(client: FlaskClient, init_database: None, new_user: User) -> None:
    response = client.post("/login", data={
        "email": new_user.email,
        "password": new_user.password
    })

    assert response.status_code == 200
    assert response.json == {
        "message": "Login Successful.",
        "user": {
            "email": "test_user_1@calorio.com",
            "first_name": "test",
            "id": 1,
            "last_name": "user_1"
        }
    }
    verify_user_cookie(new_user, response.headers["Set-Cookie"])


def test_user_login_failure(client: FlaskClient) -> None:
    response = client.post("/login", data={
        "email": "unknown@email.com",
        "password": "randompassword"
    })

    assert response.status_code == 403
    assert response.json == {"message": "Login Unsuccessful."}


def test_user_signup_failure(client: FlaskClient) -> None:
    invalid_payload = {
        "email": "test_user#calorio.com",
        "password": "password123",
        "first_name": "test",
        "last_name": "user",
    }
    response = client.post("/signup", data=invalid_payload)
    assert response.status_code == 400
    assert response.json == {"message": "Invalid Input"}

    invalid_payload.update({
        "email": "test_user@calorio.com",
        "password": "abc"
    })
    response = client.post("/signup", data=invalid_payload)
    assert response.status_code == 400
    assert response.json == {"message": "Invalid Input"}
