from functools import wraps
from flask_login import current_user
from flask import abort

# flask role-based access control decorator
def role_required(*roles):
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      if current_user.is_authenticated:
        if current_user.role_id not in roles:
          abort(403) # forbidden
        return f(*args, **kwargs)
      else:
        abort(401) # unauthorized
    return decorated_function
  return decorator
