from models import db
from router import calorio
from schemas import marsh

def setup_app(app):
    app.register_blueprint(calorio)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    db.init_app(app)
    marsh.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()