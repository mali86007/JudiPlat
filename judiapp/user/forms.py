from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

from ..models import User

class NewUserForm(FlaskForm):
    """新增用户窗体"""
    name = StringField('姓名', validators=[DataRequired(), Length(1, 30)])        # 用户真实姓名
    email = StringField('电子邮箱', validators=[DataRequired(), Length(1, 254), Email(message='电子邮箱格式不正确。')])   # 用户电子信箱
    username = StringField('用户账号', validators=[DataRequired(), Length(1, 20), Regexp('^[a-zA-Z0-9]*$', message='用户账号只包含字母和数字。')])  # 用户账号
    password = PasswordField('预置密码', validators=[DataRequired(), Length(6, 32, message='密码长度6-32位'), EqualTo('password2', message='两次输入密码不一致。') ]) # 新增用户是预置的登录密码
    password2 = PasswordField('确认密码', validators=[DataRequired()])                                  # 密码确认
    submit = SubmitField('确定提交')

    def validate_email(self, field):
        """邮箱唯一验证"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('这个信箱已经使用。')

    def validate_username(self, field):
        """账号唯一验证"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('这个账号已经使用。')


class EditUserForm(FlaskForm):
    """编辑用户窗体（角色、是否激活）"""
    name = StringField('姓名', validators=[DataRequired(), Length(1, 30)])        # 用户真实姓名，不可修改
    email = StringField('电子信箱', validators=[DataRequired(), Length(1, 254), Email(message='电子邮箱格式不正确。')])   # 用户电子信箱，需要保持唯一
    username = StringField('用户账号', validators=[DataRequired(), Length(1, 20), Regexp('^[a-zA-Z0-9]*$', message='用户账号只包含字母和数字。')])  # 用户账号，需要保持唯一
    role = StringField('角色', validators=[DataRequired()])            # 用户角色
    active = BooleanField('用户激活', validators=[DataRequired()])     # 用户是否激活
    submit = SubmitField('确定提交')