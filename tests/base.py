import unittest
from flask import url_for

from judiapp import create_app
from judiapp.extensions import db
from judiapp.models import User


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')                 # 进入测试模式
        self.context = app.test_request_context()   # 获得测试请求上下文对象
        self.context.push()                         # 推送请求上下文
        self.client = app.test_client()             # 创建测试客户端对象
        self.runner = app.test_cli_runner()

        # 建立数据库，创建用户
        db.create_all()
        user = User(name='Malj', username='malimali', email='malj007@tom.com', role='manager', active=True, confirmed=True)
        user.set_password('mlj')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = 'malimali'
            password = 'mlj'

        return self.client.post(url_for('auth.login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('user.logout'), follow_redirects=True)
