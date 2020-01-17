from flask import Blueprint

bp_opera = Blueprint(
    'opera',
    __name__,
    template_folder = 'templates',
    static_folder = 'static'
)

from . import routes
