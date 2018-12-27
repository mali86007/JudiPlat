from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user

from judiapp.user.forms import LoginForm
from judiapp.models import User
from . import main_bp
from judiapp.utils import redirect_back

@main_bp.route('/')
def index():
    # return redirect(url_for('.index'))
    # return render_template('starter.html')      # 采用adminLTE基模板
    return render_template('main/index.html')      # 采用原有的bootstrap基模板

@main_bp.route('/about')
def about():
    flash('关于我自己', 'info')
    return render_template('main/about.html')

@main_bp.route('/settings')
def settings():
    return render_template('main/settings.html')