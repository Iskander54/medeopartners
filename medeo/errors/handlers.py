from flask import Blueprint, render_template,request,g
from flask_babel import _,refresh

errors = Blueprint('errors', __name__, url_prefix='/<lang_code>')

@errors.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@errors.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.lang_code = values.pop('lang_code')


@errors.app_errorhandler(404)
def error_404(error):
    return render_template('errors/404.html'), 404


@errors.app_errorhandler(403)
def error_403(error):
    return render_template('errors/403.html'), 403


@errors.app_errorhandler(500)
def error_500(error):
    return render_template('errors/500.html'), 500