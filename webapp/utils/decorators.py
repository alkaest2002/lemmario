from functools import wraps
from flask import redirect, url_for
from flask_login import current_user


def has_role(roles):
  def wrapper(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
      if current_user.role not in roles:
        return redirect(url_for('user.unauthorized'))
      return f(*args, **kwargs)
    return wrapped
  return wrapper
