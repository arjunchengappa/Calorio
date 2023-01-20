from flask.testing import FlaskClient

from project.schemas import UserItemSchema

user_item_schema = UserItemSchema()


def test_add_new_item_to_diet_success(client: FlaskClient, init_database: None) -> None:
    response = client.post("/login", data={
        "email": "test_user_1@calorio.com",
        "password": "password123"
    })

    assert response.status_code == 200

    expected_response = {
        "user_item": {
            "consumed_date": "2023-01-12",
            "id": 1,
            "item": {
                "calories": 20,
                "consumer_count": 1,
                "id": 1,
                "name": "apples",
            }
        },
        "message": "Updated User Diet"
    }
    response = client.post("/diet", data={
        "item_name": "apples",
        "item_calories": 20,
        "consumed_date": '2023-01-12',
    })
    assert response.status_code == 201
    assert response.json == expected_response


def test_add_existing_item_to_diet_success(client: FlaskClient, init_database: None) -> None:
    expected_response = {
        "user_item": {
            "consumed_date": "2023-01-13",
            "id": 2,
            "item": {
                "calories": 20,
                "consumer_count": 2,
                "id": 1,
                "name": "apples",
            }
        },
        "message": "Updated User Diet"
    }

    response = client.post("/diet", data={
        "item_name": "apples",
        "item_calories": 20,
        "consumed_date": '2023-01-13',
    })
    assert response.status_code == 201
    assert response.json == expected_response


def test_view_complete_diet(client: FlaskClient, init_database: None) -> None:
    response = client.post("/diet", data={
        "item_name": "carrots",
        "item_calories": 30,
        "consumed_date": "2023-01-12"
    })
    assert response.status_code == 201

    expected_response = {
        "items": [
            {"calories": 20, "consumer_count": 2, "id": 1, "name": "apples"},
            {"calories": 30, "consumer_count": 1, "id": 2, "name": "carrots"}
        ],
        "user_items": [
            {
                "consumed_date": "2023-01-12", "id": 1,
                "item": {"calories": 20, "consumer_count": 2, "id": 1, "name": "apples"}
            },
            {
                "consumed_date": "2023-01-12", "id": 3,
                "item": {"calories": 30, "consumer_count": 1, "id": 2, "name": "carrots"}
            },
            {
                "consumed_date": "2023-01-13", "id": 2,
                "item": {"calories": 20, "consumer_count": 2, "id": 1, "name": "apples"}
            },
        ]
    }

    response = client.get("/diet", data={})

    assert response.status_code == 200
    assert response.json == expected_response


def test_view_diet_with_filter(client: FlaskClient, init_database: None) -> None:
    expected_response = {
        "items": [
            {"calories": 20, "consumer_count": 2, "id": 1, "name": "apples"},
            {"calories": 30, "consumer_count": 1, "id": 2, "name": "carrots"}
        ],
        "user_items": [
            {
                "consumed_date": "2023-01-12", "id": 1,
                "item": {"calories": 20, "consumer_count": 2, "id": 1, "name": "apples"}
            },
            {
                "consumed_date": "2023-01-12", "id": 3,
                "item": {"calories": 30, "consumer_count": 1, "id": 2, "name": "carrots"}
            },
        ]
    }

    response = client.get("/diet?filter_date=2023-01-12")

    assert response.status_code == 200
    assert response.json == expected_response


def test_diet_routes_when_not_logged_in(client: FlaskClient, init_database: None) -> None:
    response = client.get("/logout")

    response = client.get("/diet")
    assert response.status_code == 403

    response = client.get("/diet")
    assert response.status_code == 403

    response = client.post("/diet", data={
        "item_name": "carrots",
        "item_calories": 30,
        "consumed_date": "2023-01-12"
    })
    assert response.status_code == 403
