from datetime import datetime
from flask import render_template, flash, redirect, url_for, Blueprint, request, current_app
from flask_login import login_user, logout_user, login_required, current_user

from .forms import LoginForm, NewUserForm, ForgetPasswordForm, ResetPasswordForm, EditUserForm
from . import user_bp
from ..models import User, AnonymousUser
from ..utils import redirect_back, generate_token, validate_token
from ..extensions import db
from ..settings import Operations
from ..main.emails import send_confirm_email, send_reset_password_email


@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))      # 有权用户，返回主页

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
    return render_template('user/login.html', form=form)

@user_bp.route('/logout')
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

@user_bp.route('/new_user', methods=['GET', 'POST'])
def new_user():
    """新增用户"""
    form = NewUserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        user = User(name=name, email=email, username=username, member_since=datetime.now())
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # 生成并向邮箱发送验证令牌
        token = generate_token(user=user, operation='confirm')
        send_confirm_email(user=user, token=token)
        flash('确认邮件已发送，请到您的邮箱查收。', 'info')
        return redirect(url_for('user.login'))
    return render_template('user/new_user.html', form=form)


@user_bp.route('/list_user', methods=['GET', 'POST'])
def list_user():
    """用户列表"""
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.username.desc()).paginate(page, per_page=current_app.config['JUDIPLAT_ITEM_PER_PAGE'])
    users = pagination.items
    return render_template('user/list_user.html', pagination=pagination, users=users)


@user_bp.route('/<int:user_id>/edit_user', methods=['GET', 'POST'])
def edit_user(user_id):
    """编辑用户"""
    form = EditUserForm()
    user = User.query.get_or_404(user_id)

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data.lower()
        user.username = form.username.data
        user.role = form.role.data
        user.active = form.active.data
        db.session.commit()
        flash('修改了这条用户数据。', 'success')
        return redirect(url_for('user.list_user', form=form))

    form.name.data = user.name
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role
    form.active.data = user.active
    return render_template('user/edit_user.html', form=form)


@user_bp.route('/<int:user_id>/delete_user', methods=['POST'])
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    # flash('删除了一条用户数据。', 'success')
    return redirect(url_for('user.list_user'))


@user_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    """确认令牌"""
    if current_user.confirmed:
        return redirect(url_for('main.index'))      # 已确认用户重定向到主页

    if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
        flash('用户通过验证。', 'success')
        return redirect(url_for('main.index'))      # 通过确认，重定向到主页
    else:
        flash('无效令牌或超期。', 'danger')
        return redirect(url_for('.resend_confirm_email'))   # 未通过验证，重定向到”重复发送验证邮件“


@user_bp.route('/resend-confirm-email')
@login_required
def resend_confirm_email():
    """重新发送验证邮件"""
    if current_user.confirmed:
        return redirect(url_for('main.index'))      # 已确认用户，重定向到主页
    # 未确认用户，重新生成令牌、发送验证邮件，并重定向到主页
    token = generate_token(user=current_user, operation=Operations.CONFIRM)
    send_confirm_email(user=current_user, token=token)
    flash('发送新的验证邮件，请检查您的邮箱。', 'info')
    return redirect(url_for('main.index'))


@user_bp.route('/forget-password', methods=['GET', 'POST'])
def forget_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ForgetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
            send_reset_password_email(user=user, token=token)
            flash('Password reset email sent, check your inbox.', 'info')
            return redirect(url_for('.login'))
        flash('Invalid email.', 'warning')
        return redirect(url_for('.forget_password'))
    return render_template('user/reset_password.html', form=form)


@user_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None:
            return redirect(url_for('main.index'))
        if validate_token(user=user, token=token, operation=Operations.RESET_PASSWORD,
                          new_password=form.password.data):
            flash('Password updated.', 'success')
            return redirect(url_for('.login'))
        else:
            flash('Invalid or expired link.', 'danger')
            return redirect(url_for('.forget_password'))
    return render_template('user/reset_password.html', form=form)