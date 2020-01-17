import os
import datetime
from flask import request, render_template, flash, redirect, url_for 
from flask_login import login_user, login_required, logout_user 
from webapp.database.sqlite import query_db
from webapp.utils.decorators import has_role

from . import bp_user
from .models import User 
from .forms import *

# ################################################################################
# ROUTES
# ################################################################################

# -----------------------------------------------------------------
# UNAUTHORIZED
# -----------------------------------------------------------------
@bp_user.route("/unauthorized")
def unauthorized():

  # render view
  return render_template('user/unauthorized.html')

# -----------------------------------------------------------------
# LOGIN
# -----------------------------------------------------------------
@bp_user.route("/login", methods=("get", "post"))
@has_role(["guest"])
def login():

    # init form
    form = LoginForm()

    # on validate
    if form.validate_on_submit():

      # cache form data
      form_data = form.data
      
      # no user found
      if form_data["username"] != os.getenv("BASE_USER"):
          
        # flash error
        flash("<b>Oops!</b> Username non presente nel server.", "danger")
        
        # redirect to login
        return redirect(url_for('user.login'))
       
      # istantiate user
      user = User()
      
      # if password is invalid
      if not user.check_pass(form_data["password"]):
          
          # flash error
          flash("<b>Oops!</b> Credenziali non valide.", "danger")
          
          # redirect to login
          return redirect(url_for('user.login'))
      
      # login user
      login_user(user, remember=True, duration=datetime.timedelta(days=60))
      
      # redirect to home
      return redirect(url_for('main.index'))

    # render view
    now = datetime.datetime.now()
    return render_template("user/login.html", form = form, current_year =  now.year)

# -----------------------------------------------------------------
# LOGOUT
# -----------------------------------------------------------------
@bp_user.route("/logout")
@login_required
def logout():
    
  # logout user
  logout_user()
  
  # redirect to login page
  return redirect(url_for('user.login'))
