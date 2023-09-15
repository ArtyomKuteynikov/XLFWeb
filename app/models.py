# models.py

from flask_login import UserMixin
from . import db
from sqlalchemy.sql import func


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    org_name = db.Column(db.String(1000))
    login = db.Column(db.String(100))
    password = db.Column(db.String(1000))
    name = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    email = db.Column(db.String(100))
    show = db.Column(db.Integer, default=1)
    status = db.Column(db.String(100), default="active")
    role = db.Column(db.Integer)
    registered = db.Column(db.DateTime)


class Codes(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    phone = db.Column(db.String(100))
    code = db.Column(db.String(10))


class Shops(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    user_id = db.Column(db.Integer)
    address = db.Column(db.String(1000))
    name = db.Column(db.String(1000))
    phone = db.Column(db.String(100))
    email = db.Column(db.String(100))
    ident = db.Column(db.LargeBinary(length=(16 * 1024)))
    subscr = db.Column(db.LargeBinary(length=(16 * 1024)))
    show = db.Column(db.Integer, default=1)
    registered = db.Column(db.DateTime)
    end = db.Column(db.DateTime)


class Payments(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer)
    manager_id = db.Column(db.Integer)
    registered = db.Column(db.DateTime)
    amount = db.Column(db.REAL, default=0)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    show = db.Column(db.Integer, default=1)
    comment = db.Column(db.String(10000))
