from flask import render_template
from werkzeug.exceptions import HTTPException

from webapp.blueprints.main import bp_main
from webapp.blueprints.user import bp_user
from webapp.blueprints.opera import bp_opera

# simple generic error class
class GenericError:
  def __init__(self):
    self.code = 500
    self.description = "Errore generico del server. Segnala il problema al webmaster."

# attacher
def attach_blueprints(app):

  #-----------------------------------------------------------------------------
  # register routes
  #-----------------------------------------------------------------------------
  app.register_blueprint(bp_main, url_prefix='/')
  app.register_blueprint(bp_user, url_prefix='/user')
  app.register_blueprint(bp_opera, url_prefix='/opera')
  
  #-----------------------------------------------------------------------------
  # errors handler
  #-----------------------------------------------------------------------------
  #@app.errorhandler(Exception)
  #def page_error(error):
  #  print(error)
  #  if not isinstance(error, HTTPException): 
  #    error = GenericError()
  #  return render_template('error.html', error=error), error.code
