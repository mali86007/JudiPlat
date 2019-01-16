from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, current_app

from .forms import NewUserForm, EditUserForm
from . import user_bp
from ..models import User, AnonymousUser
from ..utils import redirect_back, generate_token, validate_token
from ..extensions import db
from ..main.emails import send_confirm_email


@user_bp.route('/new_user', methods=['GET', 'POST'])
def new_user():
    """新增用户"""
    form = NewUserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        user = User(name=name, email=email, username=username, role_id=1, member_since=datetime.now())
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