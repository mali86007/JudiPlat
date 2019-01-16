import os
import random

from faker import Faker
from flask import current_app
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import User, Role

fake = Faker('zh_CN')


def fake_admin():
    role = Role.query.filter_by(name='系统管理员').first()
    if role is None:
        role.id = 3
    admin = User(name='Malj',
                 username='malimali',
                 email='malj007@tom.com',
                 role_id=role.id,
                 active=True,
                 member_since=fake.date_time_this_year(),
                 confirmed=True)
    admin.set_password('mlj')
    db.session.add(admin)
    db.session.commit()


def fake_user(count=30):
    for i in range(count):
        user = User(name=fake.name(),
                    confirmed=False,
                    username=fake.user_name(),
                    email=fake.email(),
                    role_id=random.randint(1,2),
                    active=True,
                    member_since=fake.date_this_decade())
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

