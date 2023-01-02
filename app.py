from flask import Flask
from models import db
from schemas import marsh
from router import calorio

# Configuration
app = Flask(__name__)
app.register_blueprint(calorio)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
marsh.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()


if __name__ == 'main':
    app.run()
