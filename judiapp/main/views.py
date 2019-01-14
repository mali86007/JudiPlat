from flask import render_template, flash, redirect, url_for

from . import main_bp
from judiapp.utils import redirect_back

@main_bp.route('/')
def index():
    # return redirect(url_for('.index'))
    # return render_template('starter.html')      # 采用adminLTE基模板
    return render_template('main/index.html')      # 采用原有的bootstrap基模板

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/settings')
def settings():
    return render_template('main/settings.html')