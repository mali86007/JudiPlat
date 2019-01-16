from datetime import datetime
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

# 角色-权限关系映射表
roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                             )


class Permission(db.Model):
    """权限数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)        # 权限名称
    roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')      # 相应角色集


class Role(db.Model):
    """角色数据模型"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)            # 角色名称
    users = db.relationship('User', back_populates='role')      # 相应用户集
    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles')        # 相应权限集

    @staticmethod
    def init_role():
        """角色模型初始化"""
        roles_permissions_map = {
            '普通用户': ['浏览', '查询'],
            '有权用户': ['浏览', '查询', '管理', '设置'],
            '系统管理员': ['浏览', '查询', '管理', '设置', '系统管理']
        }

        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:    # 如果没有角色，创建之
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:      # 如果没有相应权限，创建之
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
        db.session.commit()

class User(UserMixin, db.Model):
    """用户数据模型"""
    id = db.Column(db.Integer, primary_key=True)                    # 用户id
    name = db.Column(db.String(64))                                 # 用户姓名
    username = db.Column(db.String(20), unique=True, index=True)    # 账号，唯一
    password_hash = db.Column(db.String(128))                       # 登录密码（哈希值）
    email = db.Column(db.String(128), unique=True, index=True)      # 电子信箱，唯一
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))       # 角色id
    role = db.relationship('Role', back_populates='users')          # 相应角色集
    active = db.Column(db.Boolean, default=True)                    # 在用
    member_since = db.Column(db.DateTime(), default=datetime.now)    # 注册时间
    confirmed = db.Column(db.Boolean, default=False)                # 用户确认状态
    login_date = db.Column(db.DateTime(), default=datetime.now)  # 登陆时间
    last_date = db.Column(db.DateTime(), default=datetime.now)   # 上次离开时间

    def __init__(self, **kwargs):
        """用户模型初始化"""
        super(User, self).__init__(**kwargs)
        # self.set_role()

    def set_role(self):
        """设置角色"""
        if self.role is None:
            if self.email == current_app.config['JUDIPLAT_ADMIN_EMAIL']:
                self.role = Role.query.filter_by(name='系统管理员').first()
            else:
                self.role = Role.query.filter_by(name='普通用户').first()
            db.session.commit()

    def set_password(self, password):
        """密码处理后返回哈希值赋值给密码散列值字段"""
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """将接收到的密码用密码散列值校验"""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """是否系统管理员"""
        return self.role.name == '系统管理员'

    @property
    def is_active(self):
        """是否活动用户"""
        return self.active

    def can(self, permission_name):
        """是否有权"""
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permissions

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser