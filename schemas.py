from flask_marshmallow import Marshmallow
from marshmallow import fields

from models import Item, User, UserItem

marsh = Marshmallow()


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
