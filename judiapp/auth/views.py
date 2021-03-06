from datetime import datetime
from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required, confirm_login, \
    login_fresh

from .forms import LoginForm, ForgetPasswordForm, ResetPasswordForm, ChangePasswordForm
from . import auth_bp
from ..models import User, AnonymousUser
from ..utils import redirect_back, generate_token, validate_token
from ..extensions import db
from ..settings import Operations
from ..main.emails import send_confirm_email, send_reset_password_email


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # 有权用户，返回主页

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.username == form.username.data and user.validate_password(form.password.data):
            # 用户登录时间存入
            user.login_date = datetime.now()
            db.session.commit()
            flash('登录成功。', 'info')
            login_user(user, form.remember.data)
            return redirect_back()
        flash('无效的用户名或者密码。', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/re-authenticate', methods=['GET', 'POST'])
@login_required
def re_authenticate():
    """重新登录"""
    if login_fresh():
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit() and current_user.validate_password(form.password.data):
        confirm_login()
        return redirect_back()
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """退出登录"""
    # 存入退出时间
    if current_user.is_authenticated:
        current_user.last_date = datetime.now()
        db.session.commit()

    logout_user()
    flash('安全退出。', 'info')
    return redirect_back()


@auth_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    """确认令牌"""
    if current_user.confirmed:
        return redirect(url_for('main.index'))  # 已确认用户重定向到主页

    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('用户通过验证。', 'success')
        return redirect(url_for('main.index'))  # 通过确认，重定向到主页
    else:
        flash('无效令牌或超期。', 'danger')
        return redirect(url_for('.resend_confirm_email'))  # 未通过验证，重定向到”重复发送验证邮件“


@auth_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    """重新发送验证邮件"""
    if current_user.confirmed:
        return redirect(url_for('main.index'))  # 已确认用户，重定向到主页
    # 未确认用户，重新生成令牌、发送验证邮件，并重定向到主页
    token = generate_token(user=current_user, operation=Operations.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('发送新的验证邮件，请检查您的邮箱。', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    """处理忘记密码"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # 有权用户，重定向主页

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:  # 由此用户，生成令牌、发出重置密码确认邮件，返回登录页面
            token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
            send_reset_password_email(user=user, token=token)
            flash('发送重置密码邮件，请到邮箱查收。', 'info')
            return redirect(url_for('.login'))
        flash('无效邮箱。', 'warning')
        return redirect(url_for('.forget_password'))  # 无效邮箱，重定向重置密码
    return render_template('auth/reset_password.html', form=form)  # 表单验证未通过，返回重置密码界面

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # 有权用户，重定向到主页

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            return redirect(url_for('main.index'))  # 无此用户，重定向到主页
        if validate_token(user=user, token=token, operation=Operations.RESET_PASSWORD,
                          new_password=form.password.data):
            flash('密码已更新。', 'success')
            return redirect(url_for('.login'))  # 验证令牌通过，重定向到登录
        else:
            flash('无效或过期链接。', 'danger')
            return redirect(url_for('.forget_password'))  # 令牌未通过验证，重定向到忘记密码
    return render_template('auth/reset_password.html', form=form)  # 表单未通过验证，返回重置密码界面


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    """用户变更密码"""
    form = ChangePasswordForm()
    # 表单验证通过，且原密码验证通过，变更新密码，数据库确认，重定向到主页
    if form.validate_on_submit() and current_user.validate_password(form.old_password.data):
        current_user.set_password(form.password.data)
        db.session.commit()
        flash('密码已变更。', 'success')
        return redirect(url_for('main.index', username=current_user.username))
    return render_template('auth/change_password.html', form=form)  # 表单验证或原密码验证未通过，返回变更密码页面


@auth_bp.route('/change-email', methods=['GET', 'POST'])
@fresh_login_required
def change_email_request():
    """变更邮箱"""
    # form = ChangeEmailForm()
    form = ForgetPasswordForm()  # 借用相同的窗体
    # 表单验证通过，生成令牌、发送确认邮件，重定向到主页
    if form.validate_on_submit():
        token = generate_token(user=current_user, operation=Operations.CHANGE_EMAIL, new_email=form.email.data.lower())
        send_confirm_email(to=form.email.data, user=current_user, token=token)
        flash('确认邮件发出，请在您的邮箱查收。', 'info')
        return redirect(url_for('.index', username=current_user.username))
    return render_template('auth/change_email.html', form=form)  # 表单未通过，返回变更邮箱页面

@auth_bp.route('/change-email')
@auth_bp.route('/change-email/<token>')
@login_required
def change_email(token):
    """变更邮箱（带令牌）"""
    # 令牌验证通过，重定向到主页；否则返回’变更邮箱‘
    if validate_token(user=current_user, token=token, operation=Operations.CHANGE_EMAIL):
        flash('邮箱已变更。', 'success')
        return redirect(url_for('main.index', username=current_user.username))
    else:
        flash('无效或过期令牌。', 'warning')
        return redirect(url_for('.change_email_request'))