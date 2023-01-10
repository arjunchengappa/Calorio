from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
marsh = Marshmallow()


def create_app(config_filename: str = 'config.py') -> Flask:
    app = Flask(__name__)
    # app.config.from_pyfile(config_filename)

    register_blueprints(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    db.init_app(app)
    marsh.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()

    return app


def register_blueprints(app: Flask):
    from project.router import calorio_blueprint

    app.register_blueprint(calorio_blueprint)
