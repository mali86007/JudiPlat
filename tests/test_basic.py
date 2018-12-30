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
        """测试404错误"""
        response = self.client.get('/foo')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('404 Error', data)

    def test_500_page(self):
        # create route to abort the request with the 500 Error
        @current_app.route('/500')
        def internal_server_error_for_test():
            abort(500)

        response = self.client.get('/500')
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 500)
        self.assertIn('500 Error', data)
        self.assertIn('Go Back', data)