import os
import click
# import unittest
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError

from .main import main_bp
from .auth import auth_bp
from .user import user_bp
from .extensions import bootstrap, db, login_manager, csrf, ckeditor, mail, moment, migrate
from .models import User
from .settings import config

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    """工厂函数，生成实例"""
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')  # 默认为开发版本

    app = Flask('judiapp')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_errors(app)
    register_shell_context(app)
    # register_template_context(app)
    # register_request_handlers(app)
    return app


def register_extensions(app):
    """注册扩展模块"""
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    migrate.init_app(app, db)
    # toolbar.init_app(app)


def register_blueprints(app):
    """注册蓝本"""
    app.register_blueprint(user_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)


def register_shell_context(app):
    """注册命令行上下文"""
    @app.shell_context_processor
    def make_shell_context():       # 启动shell时自动导入数据库实例和模型
        return dict(db=db, User=User)


def register_errors(app):
    """注册错误模块"""
    @app.errorhandler(400)
    def bad_request(e):
        """错误请求400"""
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        """网页未发现404"""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        """内部服务器端错误500"""
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        """句柄跨域攻击错误"""
        return render_template('errors/400.html', description=e.description), 400

def register_commands(app):
    """注册命令行"""
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='数据库删除后重建。')
    def initdb(drop):
        """初始化数据库"""
        if drop:
            click.confirm('这个操作将删除数据库，确认码？', abort=True)
            db.drop_all()
            click.echo('数据库已删除。')
        db.create_all()
        click.echo('数据库已初始化。')

    @app.cli.command()
    def init():
        """初始化系统"""
        click.echo('数据库正初始化...')
        db.create_all()

        click.echo('角色-权限正初始化...')
        # Role.init_role()

        click.echo('系统初始化完成。')

    @app.cli.command()
    @click.option('--user', default=10, help='用户数量，默认10个。')
    def forge(user ):
        """生成虚拟数据"""

        from .fakes import fake_admin, fake_user

        db.drop_all()
        db.create_all()

        click.echo('角色-权限正初始化......')
        # Role.init_role()
        click.echo('系统管理员初始化...')
        fake_admin()
        click.echo('生成用户 %d ...' % user)
        fake_user(user)
        click.echo('虚拟数据已生成。')

    @app.cli.command()
    @click.option('--count', default=2, help="测试模式：默认'count=2'")
    def test(count):
        """运行单元测试"""
        import unittest
        test_suite = unittest.TestLoader().discover(('tests'))
        unittest.TextTestRunner(verbosity=count).run(test_suite)
