from encryption import fernet
from models import Item, User, UserItem, db


def get_diet_aggregate(user_items: list) -> dict:
    """
    Returns the total number of distinct items and the total calories of the given list of
    items.
    """
    item_count = len(user_items)
    calorie_count = 0
    for user_item in user_items:
        calorie_count += user_item.total_calories

    return {"item_count": item_count, "calorie_count": calorie_count}


class DatabaseService:
    def query_all_users():
        return User.query.all()

    def query_top_items():
        return Item.query.order_by(Item.consumer_count).limit(10)

    def add_new_user(first_name, last_name, email, password):
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return user

    def query_user(email, password="", is_password_encrypted=True):
        if not password:
            return User.query.filter_by(email=email).first()

        if is_password_encrypted:
            password = fernet.decrypt(password).decode()

        return User.query.filter_by(email=email, password=password).first()

    def query_user_items(user_id, weekday=0):
        if not weekday:
            return UserItem.query.filter_by(user_id=user_id)

        return UserItem.query.filter_by(user_id=user_id, weekday=weekday)

    def add_new_item(name, calories, picture_url):
        item = Item(name=name, calories=calories, picture_url=picture_url)
        db.session.add(item)
        db.session.commit()
        return item

    def query_item_by_id(item_id):
        return Item.query.filter_by(item_id=item_id).first()

    def add_user_item(user_id, item_id, calories, quantity, weekday):
        user_item = UserItem(
            user_id=user_id,
            item_id=item_id,
            total_calories=calories*quantity,
            quantity=quantity,
            weekday=weekday
        )
        db.session.add(user_item)
        db.session.commit()
        return user_item

    def query_all_items():
        return Item.query.filtry_by().all()
