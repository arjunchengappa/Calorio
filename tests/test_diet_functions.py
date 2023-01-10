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
        "item": {
            "calories": 20,
            "consumer_count": 1,
            "id": 1,
            "name": "apples",
            "picture_url": "www.google.com"
        },
        "message": "Diet update successful"
    }
    response = client.post("/diet/1", data={
        "item_name": "apples",
        "item_calories": 20,
        "item_picture_url": "www.google.com",
        "quantity": 1,
    })
    assert response.status_code == 201
    assert response.json == expected_response


def test_add_existing_item_to_diet_success(client: FlaskClient, init_database: None) -> None:
    expected_response = {
        "item": {
            "calories": 20,
            "consumer_count": 2,
            "id": 1,
            "name": "apples",
            "picture_url": "www.google.com"
        },
        "message": "Diet update successful"
    }

    response = client.post("/diet/2", data={
        "item_id": 1,
        "quantity": 2
    })
    assert response.status_code == 201
    assert response.json == expected_response


def test_view_complete_diet(client: FlaskClient, init_database: None) -> None:
    response = client.post("/diet/2", data={
        "item_name": "carrots",
        "item_calories": 30,
        "item_picture_url": "www.google.com",
        "quantity": 3,
    })
    assert response.status_code == 201

    expected_response = {
        "diet": [
            {
                "id": 1,
                "item": {"calories": 20, "consumer_count": 2, "id": 1, "name": "apples",
                         "picture_url": "www.google.com"},
                "quantity": "1",
                "total_calories": 20,
                "weekday": 1
            },
            {
                "id": 2,
                "item": {"calories": 20, "consumer_count": 2, "id": 1, "name": "apples",
                         "picture_url": "www.google.com"},
                "quantity": "2",
                "total_calories": 40,
                "weekday": 2
            },
            {
                "id": 3,
                "item": {"calories": 30, "consumer_count": 1, "id": 2, "name": "carrots",
                         "picture_url": "www.google.com"},
                "quantity": "3",
                "total_calories": 90,
                "weekday": 2
            },
        ]
    }
    response = client.get("/diet", data={})

    assert response.status_code == 200
    assert response.json == expected_response


def test_view_diet_on_weekday(client: FlaskClient, init_database: None) -> None:
    expected_response = {
        "diet": [
            {
                "id": 2,
                "item": {"calories": 20, "consumer_count": 2, "id": 1, "name": "apples",
                         "picture_url": "www.google.com"},
                "quantity": "2",
                "total_calories": 40,
                "weekday": 2
            },
            {
                "id": 3,
                "item": {"calories": 30, "consumer_count": 1, "id": 2, "name": "carrots",
                         "picture_url": "www.google.com"},
                "quantity": "3",
                "total_calories": 90,
                "weekday": 2
            },
        ],
        'items': [
            {'calories': 20, 'consumer_count': 2, 'id': 1, 'name': 'apples',
             'picture_url': 'www.google.com'},
            {'calories': 30, 'consumer_count': 1, 'id': 2, 'name': 'carrots',
             'picture_url': 'www.google.com'}
        ],
    }
    response = client.get("/diet/2", data={})

    assert response.status_code == 200
    assert response.json == expected_response


def test_diet_routes_when_not_logged_in(client: FlaskClient, init_database: None) -> None:
    response = client.get("/logout")

    response = client.get("/diet")
    assert response.status_code == 403

    response = client.get("/diet/1")
    assert response.status_code == 403

    response = client.post("/diet/2", data={
        "item_id": 1,
        "quantity": 2
    })
    assert response.status_code == 403
