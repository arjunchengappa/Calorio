from flask.testing import FlaskClient

from project.schemas import UserItemSchema
from base64 import b64encode

user_item_schema = UserItemSchema()


def test_add_new_item_to_diet_success(client: FlaskClient, init_database: None) -> None:
    response = client.post("/sign-in", json={
        "email": "test_user_1@calorio.com",
        "password": "password123"
    })

    assert response.status_code == 200

    expected_response = {
        "user_item": {
            "consumed_date": "2023-01-12",
            "calories": 20,
            "id": 1,
            "item": {
                "consumer_count": 1,
                "id": 1,
                "name": "apples",
            }
        },
        "message": "Updated User Diet"
    }
    response = client.post("/diet", json={
        "foodItemName": "apples",
        "foodItemCalories": 20,
        "consumedDate": '2023-01-12',
    }, headers={
        'X-User-Auth': b64encode(b"test_user_1@calorio.com:password123")
    })
    assert response.status_code == 201
    assert response.json == expected_response


def test_add_existing_item_to_diet_success(client: FlaskClient, init_database: None) -> None:
    expected_response = {
        "user_item": {
            "consumed_date": "2023-01-13",
            "calories": 20,
            "id": 2,
            "item": {
                "consumer_count": 2,
                "id": 1,
                "name": "apples",
            }
        },
        "message": "Updated User Diet"
    }

    response = client.post("/diet", json={
        "foodItemName": "apples",
        "foodItemCalories": 20,
        "consumedDate": '2023-01-13',
    }, headers={
        'X-User-Auth': b64encode(b"test_user_1@calorio.com:password123")
    })
    assert response.status_code == 201
    assert response.json == expected_response


def test_view_complete_diet(client: FlaskClient, init_database: None) -> None:
    response = client.post("/diet", json={
        "foodItemName": "carrots",
        "foodItemCalories": 30,
        "consumedDate": '2023-01-12',
    }, headers={
        'X-User-Auth': b64encode(b"test_user_1@calorio.com:password123")
    })
    assert response.status_code == 201

    expected_response = {
        "items": [
            {"consumer_count": 2, "id": 1, "name": "apples"},
            {"consumer_count": 1, "id": 2, "name": "carrots"}
        ],
        "user_items": [
            {
                "consumed_date": "2023-01-12", "id": 1, "calories": 20,
                "item": {"consumer_count": 2, "id": 1, "name": "apples"}
            },
            {
                "consumed_date": "2023-01-12", "id": 3, "calories": 30,
                "item": {"consumer_count": 1, "id": 2, "name": "carrots"}
            },
            {
                "consumed_date": "2023-01-13", "id": 2, "calories": 20,
                "item": {"consumer_count": 2, "id": 1, "name": "apples"}
            },
        ]
    }

    response = client.get("/diet", headers={
        'X-User-Auth': b64encode(b"test_user_1@calorio.com:password123")
    })

    assert response.status_code == 200
    assert response.json == expected_response


def test_view_diet_with_filter(client: FlaskClient, init_database: None) -> None:
    expected_response = {
        "items": [
            {"consumer_count": 2, "id": 1, "name": "apples"},
            {"consumer_count": 1, "id": 2, "name": "carrots"}
        ],
        "user_items": [
            {
                "consumed_date": "2023-01-12", "id": 1,"calories": 20,
                "item": {"consumer_count": 2, "id": 1, "name": "apples"}
            },
            {
                "consumed_date": "2023-01-12", "id": 3, "calories": 30,
                "item": {"consumer_count": 1, "id": 2, "name": "carrots"}
            },
        ]
    }

    response = client.get("/diet?filter_date=2023-01-12", headers={
        'X-User-Auth': b64encode(b"test_user_1@calorio.com:password123")
    })

    assert response.status_code == 200
    assert response.json == expected_response


def test_diet_routes_when_not_logged_in(client: FlaskClient, init_database: None) -> None:
    response = client.get("/diet")
    assert response.status_code == 403

    response = client.post("/diet", data={
        "item_name": "carrots",
        "item_calories": 30,
        "consumed_date": "2023-01-12"
    })
    assert response.status_code == 403
