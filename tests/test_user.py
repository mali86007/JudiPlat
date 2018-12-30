from flask import url_for

# from judiapp.extensions import db
# from judiapp.models import User
from tests.base import BaseTestCase


class UserTestCase(BaseTestCase):
    """用户模块测试"""
    def test_index_page(self):
        """测试用户登录、未登录主页"""
        # 测试未登录主页
        response = self.client.get(url_for('main.index'))
        data = response.get_data(as_text=True)
        self.assertIn('尚未登录', data)
        # 测试用户登陆后主页
        self.login()
        response = self.client.get(url_for('main.index'))
        data = response.get_data(as_text=True)
        self.assertNotIn('尚未登录', data)
        self.assertIn('Malj', data)



