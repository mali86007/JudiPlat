from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from judiapp.user.forms import LoginForm
from . import user_bp
from judiapp.models import User
from judiapp.utils import redirect_back

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        if username == 'admin' and password == 'mlj':
            login_user(u, remember)
            flash('欢迎进来。', 'info')
            return redirect_back()
        flash('用户名或者密码无效。', 'warning')
        """
        admin = User.query.first()
        if admin:
            if username == admin.username and admin.validate_password(password):
                login_user(admin, remember)
                flash('欢迎回来。', 'info')
                return redirect_back()
            flash('无效的用户名或密码。', 'warning')
        else:
            flash('没有这个用户。', 'warning')
        """
    return render_template('user/login.html', form=form)

@login_required
@user_bp.route('/logout')
def logout():
    """退出登录"""
    logout_user()
    flash('安全退出。', 'info')
    return redirect_back()