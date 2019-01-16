import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'


class BaseConfig:
    """基础设置类"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'a secret string')             # 密钥
    DEBUG_TB_INTERCEPT_REDIRETS = False                                 # 调试，默认False，关闭DebugToolbar拦截重定向
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'data.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('JudiPlat Admin', MAIL_USERNAME)
    MAIL_SUBJECT_PREFIX = '[JudiPlat]'
    JUDIPLAT_ADMIN_EMAIL = os.getenv('MAIL_USERNAME', 'malj007@sina.com')

    JUDIPLAT_LOCALES = ['zh_Hans_CN', 'en_US']
    JUDIPLAT_ITEM_PER_PAGE = 15


class DevelopmentConfig(BaseConfig):
    """开发设置类"""
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'judiapp/data-dev.db')  # 开发数据库路径


class ProductionConfig(BaseConfig):
    """生产设置类"""
    # SQLALCHEMY_DATABASE_URI = os.path('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))    # 生产数据库路径（从路径中获取？）
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))      # 生产数据库路径（从配置文件中获取）


class TestingConfig(BaseConfig):
    """测试设置类"""
    TESTING = True                                       # 测试模式
    WTF_CSRF_ENABLED = False                             # CSRF令牌取消
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'               # 测试数据库（内存）


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
