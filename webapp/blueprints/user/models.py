import os
from werkzeug.security import check_password_hash, generate_password_hash
from webapp.extensions.login_ext import login_manager
from webapp.database.sqlite import query_db

# ################################################################################
# USER CLASS
# ################################################################################
class User():

  def __repr__(self):
    return f"user model: {self.id}, {self.username}, {self.role}"

  def __init__(self, **kwargs):
      
    # add props
    self.id = os.getenv("BASE_USERID")    
    self.username = os.getenv("BASE_USER")
    self.password = os.getenv("BASE_USER_PASSWORD")
    self.role = "editor"
    self.is_active = True
    self.is_anonymous = False
    self.is_authenticated = True
        
  def save(self):
    pass

  def check_pass(self, password):
    # check pass
    return check_password_hash(self.password, password)

  def get_id(self):
    # return id
    return self.id

  @login_manager.user_loader
  def load_user(id):
    if id != "1": return None
    return User()
