from flask import Blueprint, request

from decorators import require_admin, require_login
from encryption import fernet
from helpers import DatabaseService, get_diet_aggregate
from models import Item, User, UserItem, db
from schemas import ItemSchema, UserItemSchema, UserSchema
from validators import validate_password

calorio = Blueprint('calorio', __name__, template_folder='templates')
db_serice = DatabaseService()


# Routing
@calorio.route("/")
def index():
    return {"message": "Welcome to Calorio"}, 200


@calorio.route('/users')
@require_admin
def get_users_list(user):
    """
    Accessible only by admin users. Lists all users in the database
    """
    if not user or not user.is_admin:
        resp = ({"message": "Unauthorised Attempt"}, 403)
    else:
        query = db_serice.query_all_users()
        users_schema = UserSchema(many=True)
        resp = ({"users": users_schema.dump(query)}, 200)
    return resp


@calorio.route('/top-food-items')
def get_top_food_items():
    """
    Accessible by everyone, even if not logged in. Displays the top food items in the
    database.
    """
    item_schema = ItemSchema(many=True)
    query = db_serice.query_top_items()
    return item_schema.dump(query)


@calorio.route("/signup", methods=["POST"])
def signup():
    """
    Registers a user.
    """
    first_name = request.values.get('first_name')
    last_name = request.values.get('last_name')
    email = request.values.get('email')
    password = request.values.get('password')

    if db_serice.query_user(email):
        return {"message": "Email already in use."}, 400

    password = request.values.get('password')
    if not validate_password(password):
        return {"message": "Invalid Password"}, 400

    user = db_serice.add_new_user(first_name, last_name, email, password)

    encrypted_password = fernet.encrypt(user.password.encode())
    user_schema = UserSchema()

    return (
        {"message": "Registration successful", "user": user_schema.dump(user)},
        201,
        {'Set-Cookie': f'logged_in={user.email}${encrypted_password.decode()}'}
    )


@calorio.route('/login', methods=["POST"])
def login():
    """
    Logs in a user. Sets a cookie in browser to identify user.
    """
    email = request.values.get('email')
    password = request.values.get('password')

    user = db_serice.query_user(email, password, False)

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


@calorio.route('/logout')
@require_login
def logout(user):
    """
    Logs out a user. Resets the cookie that was set while logging in.
    """
    return {"message": f"{user.email} logged out successfully"}, 200, {"Set-Cookie": "logged_in=$"}


@calorio.route('/diet')
@require_login
def get_diet(user):
    """
    Displays a brief overview of the users diet.
    """
    user_items = db_serice.query_user_items(user_id=user.id)
    diet = {}
    for weekday in range(1, 8):
        weekday_user_items = user_items.filter_by(weekday=weekday).all()
        diet[f"{weekday}"] = get_diet_aggregate(weekday_user_items)

    return {"diet": diet}, 200


@calorio.route('/diet/<weekday>', methods=["GET", "POST"])
@require_login
def get_daily_diet(user, weekday):
    """
    Returns a detailed diet of the user on a particular day.
    """
    if request.method == "POST":
        item_id = request.values.get('item_id')
        quantity = int(request.values.get('quantity'))
        if not item_id:
            name = request.values.get('item_name')
            calories = request.values.get('item_calories')
            picture_url = request.values.get('item_picture_url')
            item = db_serice.add_new_item(name, calories, picture_url)
        else:
            item = db_serice.query_item_by_id(item_id)

        user_item = db_serice.add_user_item(user.id, item.id, calories, quantity, weekday)
        item_schema = ItemSchema()
        return {"message": "Diet update successful", "item": item_schema.dump(item)}, 201

    if request.method == "GET":
        user_item_query = db_serice.query_user_items(user.id, weekday)
        user_item_schema = UserItemSchema(many=True)

        item_query = db_serice.query_all_items()
        items_schema = ItemSchema(many=True)

        return {
            "items": items_schema.dump(item_query),
            "diet": user_item_schema.dump(user_item_query)
        }
