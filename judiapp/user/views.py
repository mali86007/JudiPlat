from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user

from judiapp.user.forms import LoginForm
from judiapp.models import User
from judiapp.utils import redirect_back

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    # return redirect(url_for('.index'))
    # return render_template('starter.html')      # 采用adminLTE基模板
    return render_template('index.html')      # 采用原有的bootstrap基模板

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('starter'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
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

@user_bp.route('/about')
def about():
    flash('关于我自己', 'info')
    return render_template('about.html')

@user_bp.route('/settings')
def settings():
    return render_template('settings.html')