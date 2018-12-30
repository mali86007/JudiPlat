"""
from flask import render_template, current_app


@current_app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400


@current_app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@current_app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@current_app.errorhandler(413)
def request_entity_too_large(e):
    return render_template('errors/413.html'), 413

@current_app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

"""
