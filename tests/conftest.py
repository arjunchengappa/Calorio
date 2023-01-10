from flask import Flask
from flask.testing import FlaskClient
from pytest import fixture

from project import create_app, db
from project.models import User


@fixture
def app() -> Flask:
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    yield app


@fixture
def client(app: Flask) -> FlaskClient:
    with app.test_client() as testing_client:
        # Establish an application context
        with app.app_context():
            yield testing_client


@fixture
def new_user(app: Flask) -> User:
    user = User(
        email="test_user_1@calorio.com",
        password="password123",
        first_name="test",
        last_name="user_1"
    )
    yield user


@fixture
def init_database(client: FlaskClient, new_user) -> None:
    db.create_all()
    db.session.add(new_user)
    db.session.commit()

    yield

    db.drop_all()
