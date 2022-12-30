from flask import Flask, request
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from cryptography.fernet import Fernet


# Configuration
db = SQLAlchemy()
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)
marsh = Marshmallow(app)

fernet_key = b'v__sKq22Hrm3BsoJz-WB6VmJrwHcwxLmYX2toWEL7aI='
fernet = Fernet(fernet_key)


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


with app.app_context():
    db.drop_all()
    db.create_all()


# Schema
class UserSchema(marsh.Schema):
    class Meta:
        model = User
    id = fields.Integer()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()


class ItemSchema(marsh.Schema):
    class Meta:
        model = Item

    id = fields.Integer()
    name = fields.Str()
    calories = fields.Integer()
    consumer_count = fields.Integer()
    picture_url = fields.URL()


class UserItemSchema(marsh.Schema):
    class Meta:
        model = UserItem

    id = fields.Integer()
    item = fields.Method("get_item")
    total_calories = fields.Integer()
    quantity = fields.Str()
    weekday = fields.Integer()

    @staticmethod
    def get_item(user_item: UserItem):
        item = Item.query.filter_by(id=user_item.item_id).first()
        item_schema = ItemSchema()
        return item_schema.dump(item)


# Helpers
def validate_user(email, password, is_encrypted=True):
    if is_encrypted:
        password = fernet.decrypt(password).decode()
    user = User.query.filter_by(email=email, password=password).first()
    return user


def get_diet_aggregate(user_items: list) -> dict:
    item_count = len(user_items)
    calorie_count = 0
    for user_item in user_items:
        calorie_count += user_item.total_calories

    return {"item_count": item_count, "calorie_count": calorie_count}


# Wrappers
def require_login(function):
    def wrapper(**kwargs):
        try:
            email, password = request.cookies.get('logged_in').split("$")
            user = validate_user(email, password)
            if not user:
                return {"message": "User not logged in."}, 403
            kwargs['user'] = user
            return function(**kwargs)
        except ValueError:
            return {"message": "User not logged in."}, 403

    wrapper.__name__ = f"{function.__name__}_wrapper"
    return wrapper


# Routing
@app.route('/users')
@require_login
def get_users_list(user):
    if not user or not user.is_admin:
        resp = ({"message": "Unauthorised Attempt"}, 403)
    else:
        query = User.query.all()
        users_schema = UserSchema(many=True)
        resp = ({"users": users_schema.dump(query)}, 200)
    return resp


@app.route('/top-food-items')
def get_top_food_items():
    sort_by = request.args.get('order_by')
    item_schema = ItemSchema(many=True)
    if not sort_by or sort_by == 'consumers':
        query = Item.query.order_by(Item.consumer_count).limit(10)
    elif sort_by == 'calories':
        query = Item.query.order_by(Item.calories).limit(10)
    else:
        return {"message": "Invalid parameter value (order_by)"}, 400
    return item_schema.dump(query)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    email = request.values.get('email')
    if User.query.filter_by(email=email).all():
        return {"message": "Email already in use."}, 400

    user = User(
        first_name=request.values.get('first_name'),
        last_name=request.values.get('last_name'),
        email=email,
        password=request.values.get('password')
    )
    db.session.add(user)
    db.session.commit()

    encrypted_password = fernet.encrypt(user.password.encode())

    return (
        {"message": "Registration successful"},
        201,
        {'Set-Cookie': f'logged_in={user.email}${encrypted_password}'}
    )


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.values.get('email')
        password = request.values.get('password')
        user = validate_user(email, password, is_encrypted=False)
        encrypted_password = fernet.encrypt(password.encode())
        if user:
            user_schema = UserSchema()
            return (
                {
                    "message": "Login Successful.",
                    "user": user_schema.dump(user)
                },
                200,
                {
                    "Set-Cookie": f"logged_in={user.email}${encrypted_password}"
                }
            )
        else:
            return {"message": "Login Unsuccessful."}, 403


@app.route('/logout')
@require_login
def logout(user):
    return {"message": f"{user.email} logged out successfully"}, 200, {"Set-Cookie": "logged_in=$"}


@app.route('/diet')
@require_login
def get_diet(user):
    user_items = UserItem.query.filter_by(user_id=user.id)
    diet = {}
    for weekday in range(1, 8):
        weekday_user_items = user_items.filter_by(weekday=weekday).all()
        diet[f"{weekday}"] = get_diet_aggregate(weekday_user_items)

    return {"diet": diet}, 200


@app.route('/diet/<weekday>', methods=["GET", "POST"])
@require_login
def get_daily_diet(user, weekday):
    if request.method == "POST":
        item_id = request.values.get('item_id')
        if not item_id:
            name = request.values.get('item_name')
            calories = request.values.get('item_calories')
            picture_url = request.values.get('item_picture_url')
            item = Item(name=name, calories=calories, picture_url=picture_url)
            db.session.add(item)
            db.session.commit()
        else:
            item = Item.query.filter_by(id=item_id)

        quantity = int(request.values.get('quantity'))
        user_item = UserItem(
            user_id=user.id,
            item_id=item.id,
            total_calories=item.calories*quantity,
            quantity=quantity,
            weekday=weekday
        )
        db.session.add(user_item)
        db.session.commit()
        item_schema = ItemSchema()
        return {"message": "Diet update successful", "item": item_schema.dump(item)}, 201

    if request.method == "GET":
        user_item_query = UserItem.query.filter_by(user_id=user.id, weekday=weekday)
        user_item_schema = UserItemSchema(many=True)

        item_query = Item.query.order_by(Item.name).all()
        items_schema = ItemSchema(many=True)

        return {
            "items": items_schema.dump(item_query),
            "diet": user_item_schema.dump(user_item_query)
        }


if __name__ == 'main':
    app.run()
