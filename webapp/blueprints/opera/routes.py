import time
import re

import requests
from bs4 import BeautifulSoup

from flask import render_template, request, url_for, flash, redirect, abort
from flask_login import login_required 

from webapp.database.sqlite import get_db, query_db
from webapp.utils.utilityfn import is_safe_url

from . import bp_opera
from .forms import *  

# ################################################################################
# GLOBAL CONSTANTS AND VARS 
# ################################################################################

MSG_ERROR   = "<b>Ooops!</b> Si è verificato un errore."
MSG_SUCCESS = "<b>Hurray!</b> Lemma correttamente salvato."

# ################################################################################
# ROUTES 
# ################################################################################

# --------------------------------------------------------------------------------
# Recupera lemma via Treccani
# --------------------------------------------------------------------------------
@bp_opera.route("/recupera/treccani", methods=("get", "post"))
@login_required
def retrieve_word_treccani():
  
  # init form
  form = RetrieveWordViaLinkForm()
  
  # on validate form
  if form.validate_on_submit():

    try:
     
      # get url content
      page = requests.get(form.data["link"])
      
      # parse content
      soup = BeautifulSoup(page.content, "html.parser")

      # extract lemma and lemma def
      lemma = soup.find("span", class_="lemma").get_text().strip()
      definition = soup.find("div", class_ = "module-article-full_content").get_text().strip()
      definition = re.sub('\s+', ' ', definition)

      # redirect
      return redirect(url_for("opera.add_word", lemma = lemma, definition = definition))

    except Exception as e:
      
      # notify user
      flash(f"{MSG_ERROR} {str(e)}","error")

  # render view
  return render_template("opera/retrieve_link.html", form = form, provider = "Treccani")

# --------------------------------------------------------------------------------
# Recupera lemma via De Mauro
# --------------------------------------------------------------------------------
@bp_opera.route("/recupera/demauro", methods=("get","post"))
@login_required
def retrieve_word_demauro():

  # init form
  form = RetrieveWordViaLinkForm()
  
  # on validate form
  if form.validate_on_submit():

    try:
      
      # get url content
      page = requests.get(form.data["link"])
      
      # parse content
      soup = BeautifulSoup(page.content, "html.parser")

      # extract lemma and lemma def
      chunk = soup.find("article", id = "lemma")
      lemma = chunk.find("h1", class_ = "hentry__title").get_text().strip()
      definition = lemma + " " + chunk.find("section", id = "descrizione").get_text().strip()
      definition = re.sub('\s+', ' ', definition)
      
      # redirect
      return redirect(url_for("opera.add_word", lemma = lemma, definition = definition))

    except Exception as e:
      
      # notify user
      flash(f"{MSG_ERROR} {str(e)}", "error")

  # render view
  return render_template("opera/retrieve_link.html", form = form, provider = "De Mauro")

# --------------------------------------------------------------------------------
# Recupera lemma via Olivetti
# --------------------------------------------------------------------------------
@bp_opera.route("/recupera/olivetti", methods=("get","post"))
@login_required
def retrieve_word_olivetti():

  # init form
  form = RetrieveWordViaLinkForm()
  
  # on validate form
  if form.validate_on_submit():

    try:
     
      # get url content
      page = requests.get(form.data["link"])
      
      # parse content
      soup = BeautifulSoup(page.content, "html.parser")

      # extract lemma and lemma def
      chunk = soup.find("div", id = "myth1")
      lemma = chunk.find("span", class_ = "lemma").get_text().strip()
      definition = lemma + " " + " ".join([ f" {i}. " + bit.get_text().strip() for i, bit in enumerate(chunk.find_all("span", class_ = "italiano"),1) ])
      definition = re.sub('\s+', ' ', definition).strip()
      
      # redirect
      return redirect(url_for("opera.add_word", lemma = lemma, definition = definition))

    except Exception as e:
      
      # notify user
      flash(f"{MSG_ERROR} {str(e)}", "error")

  # render view
  return render_template("opera/retrieve_link.html", form = form, provider = "Olivetti")

# --------------------------------------------------------------------------------
# Inserisci lemma nel database
# --------------------------------------------------------------------------------
@bp_opera.route("/inserisci", methods=("post", "get"))
@login_required
def add_word():
  
  # cache param
  lemma = request.args.get("lemma")
  definition = request.args.get("definition")
  
  # iy4jnit form
  form = AddWordForm(request.form, data = { "lemma" : lemma, "definition" : definition })
   
  # on validate form
  if form.validate_on_submit():

    try:

      # cache form data
      data = form.data

      # set time data
      timestamp = int(time.time())
      
      # write data to sqlite
      cur = get_db().cursor()
      cur.execute("INSERT INTO lemmi VALUES(?,?,?,?,?,?)" , [ data["lemma"], data["lemma"][0].upper(),"", data["definition"], timestamp , timestamp ])
      cur.execute("INSERT INTO lemmi_search VALUES(?,?)", [ data["lemma"], data["definition"] ]) 
      get_db().commit()

      # redirect
      return redirect(url_for("main.retrieve_links"))

    except Exception as e:
      
      # notify user
      flash(f"{MSG_ERROR} {str(e)}","error")

    # render view
  return render_template("opera/add.html", form = form)

# --------------------------------------------------------------------------------
# Aggiorna lemma nel database
# --------------------------------------------------------------------------------
@bp_opera.route("/aggiorna/<rowid>", methods=("post", "get"))
@login_required
def update_word(rowid):
  
  # cache param
  next_url = request.args.get("next", url_for("main.index"))

  # try to find lemma
  lemma_data = query_db("SELECT lemma, definition FROM lemmi WHERE rowid = ?", [ rowid ], one = True)

  # no lemma no party
  if not lemma_data: return abort(404)
  
  # init form
  form = AddWordForm(request.form, data = { "lemma": lemma_data["lemma"], "definition": lemma_data["definition"] })
   
  # on validate form
  if form.validate_on_submit():

    # cache form data
    data = form.data

    try:
      
      # set time data
      timestamp = int(time.time())
      
      # write data to sqlite
      cur = get_db().cursor()
      cur.execute("UPDATE lemmi SET lemma = ?, definition = ?, modified = ? WHERE rowid = ?", \
          [ data["lemma"], data["definition"], timestamp , rowid  ] )
      cur.execute("UPDATE lemmi_search SET lemma = ?, definition = ? WHERE rowid = ?", [ data["lemma"], data["definition"], rowid ])
      get_db().commit()

      # redirect
      if is_safe_url(next_url): 
        return redirect(next_url)
      return redirect(url_for("main.index"))

    except Exception as e:
      
      # notify user
      flash(f"{MSG_ERROR} {str(e)}","error")

    # render view
  return render_template("opera/add.html", form = form)

# --------------------------------------------------------------------------------
# Cerca lemma nel database
# --------------------------------------------------------------------------------
@bp_opera.route("/cancella/<rowid>", methods=("post", "get"))
@login_required
def delete_word(rowid):

  # delete word
  cur = get_db().cursor()
  cur.execute("DELETE FROM lemmi WHERE rowid = ?", [ rowid  ] )
  cur.execute("DELETE FROM lemmi_search WHERE rowid = ?", [ rowid ])
  get_db().commit()

  # redirect
  return redirect(url_for("main.index"))

# --------------------------------------------------------------------------------
# Cerca lemma nel database
# --------------------------------------------------------------------------------
@bp_opera.route("/cerca", methods=("post", "get"))
@login_required
def search_word():
  
  # init var
  words_list = []

  # init form
  form = SearchWordForm()
   
  # on validate form
  if form.validate_on_submit():

    # cache form data
    data = form.data
    
    # fetch data
    words_list = query_db("SELECT lemma, HIGHLIGHT(lemmi_search, 1, '<span class=""highlight"">', '</span>') AS definition FROM lemmi_search WHERE definition MATCH ? ORDER BY rank LIMIT 50", [ f"{data['search_term']}*"])
  
  # render view
  return render_template("opera/search.html", form = form, words_list = words_list )
