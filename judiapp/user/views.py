from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from .forms import LoginForm
from . import user_bp
from ..models import User, AnonymousUser
from ..utils import redirect_back

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))      # 有权用户，返回主页

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.username == form.username.data and user.validate_password(form.password.data):
            flash('登录成功。', 'info')
            login_user(user, form.remember.data)
            return redirect_back()
        flash('无效的用户名或者密码。', 'warning')
    return render_template('user/login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    """退出登录"""
    logout_user()
    flash('安全退出。', 'info')
    return redirect_back()
