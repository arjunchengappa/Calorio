from flask.testing import FlaskClient

from project.models import User
from project.schemas import UserSchema

user_schema = UserSchema()


def test_new_user_signup_success(client: FlaskClient) -> None:
    response = client.post("/sign-in", json={
        "email": "test_user@calorio.com",
        "password": "password123",
    })

    # Test if database entry is is as expected
    user = User.query.filter().first()
    assert user_schema.dump(user) == response.json["user"]

    # Test if response is as expected
    assert response.status_code == 200
    assert response.json == {
        "message": "Sign in successful",
        "user": {
            "email": "test_user@calorio.com",
            "id": 1,
        }
    }


def test_user_signup_failure(client: FlaskClient) -> None:
    invalid_payload = {
        "email": "test_user_2@calorio.com",
        "password": "pas",
    }
    response = client.post("/sign-in", json=invalid_payload)
    assert response.status_code == 400
    assert response.json == {"message": "Invalid Input"}
