from flask import Flask
from dotenv import load_dotenv

# load environmental variables
load_dotenv()

# init app
app = Flask(__name__)

# config app
from config import devConfig
app.config.from_object(devConfig)

# import extensions
from webapp.extensions.login_ext import attach_login_manager
from webapp.extensions.jinja_ext import attach_jinja
from webapp.extensions.blueprints_ext import attach_blueprints
from webapp.extensions.database_ext import attach_db

# app factory function
def create_app():
         
  # attach login manager
  attach_login_manager(app)

  # attach jinja
  attach_jinja(app)

  # attach blueprints
  attach_blueprints(app)

  # attach db
  attach_db(app)

  # return app
  return app
