from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from judiapp.extensions import db


class User(db.Model, UserMixin):
    """用户数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)    #
    password_hash = db.column(db.String(20))
    # password_hash = db.Column(db.String(128))
    # locale = db.Column(db.String(20))
    # items = db.relationship('Item', back_populates='author', cascade='all')

    def set_password(self, password):
        """密码处理后返回哈希值赋值给密码散列值字段"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """将接收到的密码用密码散列值校验"""
        return check_password_hash(self.password_hash, password)



