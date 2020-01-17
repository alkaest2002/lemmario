from flask import Blueprint

bp_user = Blueprint(
    'user',
    __name__,
    template_folder = 'templates',
    static_folder = 'static'
)

from . import routes
