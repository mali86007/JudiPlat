import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler

import click
from flask import Flask, render_template, request
from flask_login import current_user
from flask_sqlalchemy import get_debug_queries
from flask_wtf.csrf import CSRFError

from judiapp.user.views import user_bp
from judiapp.extensions import bootstrap, db, login_manager, csrf, ckeditor, mail, moment, migrate
from judiapp.models import User
from judiapp.settings import config

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')  # 默认为开发版本

    app = Flask('judiapp')
    app.config.from_object(config[config_name])

    # register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    # register_commands(app)
    register_errors(app)
    # register_shell_context(app)
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
    # toolbar.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    """注册蓝本"""
    app.register_blueprint(user_bp)


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