from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    calories = db.Column(db.Integer)
    consumer_count = db.Column(db.Integer, default=0)
    picture_url = db.Column(db.String(100))


class UserItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.String)
    total_calories = db.Column(db.Integer, default=0)
    weekday = db.Column(db.Integer)


class CalorieGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    per_day_limit = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    