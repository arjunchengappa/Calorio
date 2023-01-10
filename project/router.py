from flask import Blueprint, request
from marshmallow.exceptions import ValidationError

from project.decorators import require_admin, require_login
from project.encryption import fernet
from project.schemas import ItemSchema, UserItemSchema, UserSchema

calorio_blueprint = Blueprint('calorio', __name__, template_folder='templates')


# Routing
@calorio_blueprint.route("/")
def index():
    return {"message": "Welcome to Calorio"}, 200


@calorio_blueprint.route('/users')
@require_admin
def get_users_list(user):
    """
    Accessible only by admin users. Lists all users in the database
    """
    if not user or not user.is_admin:
        resp = ({"message": "Unauthorised Attempt"}, 403)
    else:
        users_schema = UserSchema(many=True)
        resp = ({"users": users_schema.query_all_users()}, 200)
    return resp


@calorio_blueprint.route('/top-food-items')
def get_top_food_items():
    """
    Accessible by everyone, even if not logged in. Displays the top food items in the
    database.
    """
    item_schema = ItemSchema(many=True)
    return item_schema.query_top_items()


@calorio_blueprint.route("/signup", methods=["POST"])
def signup():
    """
    Registers a user.
    """
    user_schema = UserSchema()
    first_name = request.values.get('first_name')
    last_name = request.values.get('last_name')
    email = request.values.get('email')
    password = request.values.get('password')

    if user_schema.query_user_by_email(email):
        return {"message": "Email already in use."}, 400

    try:
        user = user_schema.add_new_user(first_name, last_name, email, password)
    except ValidationError:
        return {"message": "Invalid Input"}, 400

    encrypted_password = fernet.encrypt(password.encode())

    return (
        {"message": "Registration successful", "user": user},
        201,
        {'Set-Cookie': f'logged_in={email}${encrypted_password.decode()}'}
    )


@calorio_blueprint.route('/login', methods=["POST"])
def login():
    """
    Logs in a user. Sets a cookie in browser to identify user.
    """
    user_schema = UserSchema()
    email = request.values.get('email')
    password = request.values.get('password')

    user = user_schema.query_user(email, password)

    encrypted_password = fernet.encrypt(password.encode())

    if user:
        return (
            {
                "message": "Login Successful.",
                "user": user
            },
            200,
            {
                "Set-Cookie": f"logged_in={email}${encrypted_password.decode()}"
            }
        )
    else:
        return {"message": "Login Unsuccessful."}, 403


@calorio_blueprint.route('/logout')
@require_login
def logout(user):
    """
    Logs out a user. Resets the cookie that was set while logging in.
    """
    return {"message": f"{user['email']} logged out successfully"}, 200, {"Set-Cookie": "logged_in=$"}


@calorio_blueprint.route('/diet')
@require_login
def get_diet(user):
    """
    Displays a brief overview of the users diet.
    """
    user_item_schema = UserItemSchema(many=True)
    user_items = user_item_schema.query_user_items(user_id=user["id"])
    return {"diet": user_items}, 200


@calorio_blueprint.route('/diet/<weekday>', methods=["GET", "POST"])
@require_login
def get_daily_diet(user, weekday):
    """
    Returns a detailed diet of the user on a particular day.
    """
    if request.method == "POST":
        item_schema = ItemSchema()

        item_id = request.values.get('item_id')
        quantity = int(request.values.get('quantity'))

        if not item_id:
            name = request.values.get('item_name')
            calories = request.values.get('item_calories')
            picture_url = request.values.get('item_picture_url')
            item = item_schema.add_new_item(name, calories, picture_url)
        else:
            item = item_schema.query_and_increment_item_by_id(item_id)

        user_item_schema = UserItemSchema()
        user_item_schema.add_user_item(user["id"], item["id"], item["calories"],
                                       quantity, weekday)
        return {"message": "Diet update successful", "item": item}, 201

    if request.method == "GET":
        user_item_schema = UserItemSchema(many=True)
        user_items = user_item_schema.query_user_items_by_weekday(user["id"], weekday)

        item_schema = ItemSchema(many=True)
        all_items = item_schema.query_all_items()

        return {
            "diet": user_items,
            "items": all_items,
        }
