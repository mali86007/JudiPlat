import os
import random

from faker import Faker
from flask import current_app
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import User

fake = Faker('zh_CN')


def fake_admin():
    admin = User(name='Malj',
                 username='malimali',
                 email='malj007@tom.com',
                 role='manager',
                 active=True,
                 member_since=fake.date_time_this_year(),
                 confirmed=True)
    admin.set_password('mlj')
    db.session.add(admin)
    db.session.commit()


def fake_user(count=3):
    for i in range(count):
        user = User(name=fake.name(),
                    confirmed=False,
                    username=fake.user_name(),
                    email=fake.email(),
                    role='user',
                    active=True,
                    member_since=fake.date_this_decade())
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

