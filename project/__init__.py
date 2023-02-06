from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
marsh = Marshmallow()


def create_app(config_file: str = '../config.json') -> Flask:
    app = Flask(__name__)

    register_blueprints(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

    db.init_app(app)
    migrate = Migrate(app, db)
    migrate.init_app(app, db)

    marsh.init_app(app)
    CORS(app)

    return app


def register_blueprints(app: Flask):
    from project.router import calorio_blueprint

    app.register_blueprint(calorio_blueprint)
