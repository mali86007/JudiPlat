import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig:
    """基础设置类"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'a secret string')             # 密钥
    DEBUG_TB_INTERCEPT_REDIRETS = False                                 # 调试，默认False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'data.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JUDIPLAT_LOCALES = ['zh_Hans_CN', 'en_US']
    JUDIPLAT_ITEM_PER_PAGE = 20


class DevelopmentConfig(BaseConfig):
    """开发设置类"""
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'judiapp/data-dev.db')  # 开发数据库路径


class ProductionConfig(BaseConfig):
    """生产设置类"""
    # SQLALCHEMY_DATABASE_URI = os.path('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))    # 生产数据库路径（从路径中获取？）
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))      # 生产数据库路径（从配置文件中获取）


class TestingConfig(BaseConfig):
    """测试设置类"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'               # 测试数据库（内存）


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
