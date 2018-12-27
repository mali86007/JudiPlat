from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


class User(UserMixin, db.Model):
    """用户类数据模型"""
    id = db.Column(db.Integer, primary_key=True)                    # 用户id
    name = db.Column(db.String(64))                                 # 用户姓名
    username = db.Column(db.String(20), unique=True, index=True)    # 账号，唯一
    password_hash = db.Column(db.String(128))                       # 登录密码（哈希值）
    email = db.Column(db.String(128), unique=True, index=True)      # 电子信箱，唯一
    role = db.Column(db.String(20), default='user')                 # 角色
    active = db.Column(db.Boolean, default=True)                    # 在用
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)    # 注册时间
    confirmed = db.Column(db.Boolean, default=False)                # 用户确认状态
    login_date = db.Column(db.DateTime(), default=datetime.utcnow)  # 登陆时间
    last_date = db.Column(db.DateTime(), default=datetime.utcnow)   # 上次离开时间

    def set_password(self, password):
        """密码处理后返回哈希值赋值给密码散列值字段"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """将接收到的密码用密码散列值校验"""
        return check_password_hash(self.password_hash, password)

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser