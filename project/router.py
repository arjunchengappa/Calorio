from datetime import datetime

from flask import Blueprint, request
from marshmallow.exceptions import ValidationError

from project.decorators import require_admin, require_login
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
    return {'top_food_items': item_schema.query_top_items()}


@calorio_blueprint.route("/sign-in", methods=["POST"])
def sign_in():
    """
    Registers a user.
    """
    user_schema = UserSchema()
    first_name = request.json.get('firstName')
    last_name = request.json.get('lastName')
    email = request.json.get('email')
    password = request.json.get('password')

    try:
        if first_name:
            user = user_schema.add_new_user(first_name, last_name, email, password)
        else:
            user = user_schema.query_user(email, password)
    except ValidationError:
        return {"message": "Invalid Input"}, 400
    if user:
        return ({"message": "Sign in successful", "user": user}, 200)
    else:
        return {"message": "Invalid Attempt"}, 403


@calorio_blueprint.route('/diet', methods=['GET', 'POST'])
@require_login
def get_diet(user):
    """
    Displays a brief overview of the users diet.
    """
    user_item_schema = UserItemSchema()
    item_schema = ItemSchema()

    if request.method == 'POST':
        item_name = request.json.get('foodItemName')
        consumed_date = request.json.get('consumedDate')
        item_calories = request.json.get('foodItemCalories')

        consumed_date = datetime.strptime(consumed_date, '%Y-%m-%d')

        item = item_schema.add_or_update_item(name=item_name)
        user_item = user_item_schema.add_user_item(user['id'], item['id'], item_calories, consumed_date)

        return {'message': 'Updated User Diet', 'user_item': user_item}, 201

    if request.method == 'GET':
        filter_date = request.values.get('filter_date')

        if filter_date:
            user_items = user_item_schema.query_user_items_by_date(user['id'], filter_date)
        else:
            user_items = user_item_schema.query_user_items(user['id'])

        items = item_schema.query_all_items()

        return {'user_items': user_items, 'items': items}, 200
