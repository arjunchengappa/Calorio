from marshmallow import fields
from marshmallow.exceptions import ValidationError

from project import db, marsh
from project.models import Item, User, UserItem
from project.validators import validate_password


# Schema
class UserSchema(marsh.Schema):
    class Meta:
        model = User
        load_instance = True
    id = fields.Integer()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()

    def query_all_users(self):
        query = User.query.all()
        return self.dump(query, many=True)

    def query_user(self, email, password):
        query = User.query.filter_by(email=email, password=password).first()
        return self.dump(query)

    def query_user_by_email(self, email):
        query = User.query.filter_by(email=email).first()
        return self.dump(query)

    def add_new_user(self, first_name, last_name, email, password):
        error = self.validate({
            "email": email,
            "first_name": first_name,
            "last_name": last_name
        })

        if error or not validate_password(password):
            raise ValidationError("Invalid Input")

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return self.dump(user)


class ItemSchema(marsh.Schema):
    class Meta:
        model = Item

    id = fields.Integer()
    name = fields.Str()
    calories = fields.Integer()
    consumer_count = fields.Integer()
    picture_url = fields.URL()

    def query_all_items(self):
        query = Item.query.filter_by()
        return self.dump(query, many=True)

    def query_top_items(self):
        query = Item.query.order_by(Item.consumer_count).limit(10)
        return self.dump(query, many=True)

    def query_and_increment_item_by_id(self, item_id):
        item = Item.query.filter_by(id=item_id).first()
        item.consumer_count += 1
        db.session.commit()
        return self.dump(item)

    def add_new_item(self, name, calories, picture_url):
        item = Item(name=name, calories=calories, picture_url=picture_url, consumer_count=1)
        db.session.add(item)
        db.session.commit()
        return self.dump(item)


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

    def query_user_items(self, user_id):
        query = UserItem.query.filter_by(user_id=user_id).order_by(UserItem.weekday)
        return self.dump(query, many=True)

    def query_user_items_by_weekday(self, user_id, weekday):
        query = UserItem.query.filter_by(user_id=user_id, weekday=weekday)
        return self.dump(query, many=True)

    def add_user_item(self, user_id, item_id, calories, quantity, weekday):
        user_item = UserItem(
            user_id=user_id,
            item_id=item_id,
            total_calories=calories*quantity,
            quantity=quantity,
            weekday=weekday
        )
        db.session.add(user_item)
        db.session.commit()
        return self.dump(user_item)
