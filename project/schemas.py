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

        if not validate_password(password):
            raise ValidationError("Invalid Input")

        user = User(
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

    def query_all_items(self):
        query = Item.query.filter_by()
        return self.dump(query, many=True)

    def query_top_items(self):
        query = Item.query.order_by(Item.consumer_count.desc()).limit(10)
        return self.dump(query, many=True)

    def add_or_update_item(self, name, calories):
        item = Item.query.filter_by(name=name).first()
        if item:
            item.consumer_count += 1
            db.session.commit()
            return self.dump(item)
        else:
            item = Item(name=name, calories=calories, consumer_count=1)
            db.session.add(item)
            db.session.commit()
            return self.dump(item)


class UserItemSchema(marsh.Schema):
    class Meta:
        model = UserItem

    id = fields.Integer()
    item = fields.Method("get_item")
    consumed_date = fields.Date()

    @staticmethod
    def get_item(user_item: UserItem):
        item = Item.query.filter_by(id=user_item.item_id).first()
        item_schema = ItemSchema()
        return item_schema.dump(item)

    def query_user_items(self, user_id):
        query = UserItem.query.filter_by(user_id=user_id).order_by(UserItem.consumed_date)
        return self.dump(query, many=True)

    def query_user_items_by_date(self, user_id, filter_date):
        query = UserItem.query.filter_by(user_id=user_id, consumed_date=filter_date)
        return self.dump(query, many=True)

    def add_user_item(self, user_id, item_id, consumed_date):
        user_item = UserItem(
            user_id=user_id,
            item_id=item_id,
            consumed_date=consumed_date
        )
        db.session.add(user_item)
        db.session.commit()
        return self.dump(user_item)
