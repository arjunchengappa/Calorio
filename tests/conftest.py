from flask import Flask
from flask.testing import FlaskClient
from pytest import fixture

from project import create_app, db
from project.models import User


@fixture(scope="module")
def app() -> Flask:
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@fixture(scope="module")
def client(app: Flask) -> FlaskClient:
    with app.test_client() as testing_client:
        # Establish an application context
        with app.app_context():
            yield testing_client


@fixture(scope="module")
def init_database(client: FlaskClient) -> None:
    db.create_all()

    user = User(
        email="test_user_1@calorio.com",
        password="password123",
    )
    db.session.add(user)
    db.session.commit()

    yield

    db.drop_all()
