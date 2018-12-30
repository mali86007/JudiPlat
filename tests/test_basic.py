from flask import current_app, abort

from tests.base import BaseTestCase


class BasicTestCase(BaseTestCase):

    def test_app_exist(self):
        """测试程序实例是否存在"""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """测试程序实例是否运行在测试模式"""
        self.assertTrue(current_app.config['TESTING'])

    def test_404_error(self):
        """测试404错误页面"""
        response = self.client.get('/foo')          # 访问一个未定义的URL
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('404 Error', data)

    def test_500_page(self):
        """测试500错误页面"""
        @current_app.route('/500')
        def internal_server_error_for_test():   # 创建500错误响应
            abort(500)

        response = self.client.get('/500')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn('500 Error', data)

        """
        def test_form_validation(self):        
            response = self.client.post('/', data=dict(name=' ', body='Hello, this page!'), follow_redirects=True)
            data = response.get_data(as_text=True)
            self.assertIn('无效的用户名或者密码。', data)
        """
