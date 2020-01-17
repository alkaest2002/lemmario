from flask import render_template, request, url_for, abort
from flask_login import login_required 
from webapp.database.sqlite import query_db
import re

from . import bp_main

# ################################################################################
# GLOBAL CONSTANTS AND VARS
# ################################################################################
PER_PAGE = 10

# ################################################################################
# ROUTES 
# ################################################################################

# --------------------------------------------------------------------------------
# Homepage
# --------------------------------------------------------------------------------
@bp_main.route("/")
@login_required
def index():

  # cache params
  offset_field  = request.args.get("offset_field", "lemma")
  offset_value  = request.args.get("offset_value", "0")
  filter_by = request.args.get("filter_by", None)
  order_dir  = request.args.get("order_dir", "ASC").upper()

  # sanity checks
  if offset_field and offset_field not in ("lemma", "visited"): abort(400)
  if offset_value and not re.sub("\s|'|\-","", offset_value).isalnum(): abort(400)
  if order_dir and order_dir not in ("ASC", "DESC"): abort(400)
  if filter_by:
    for letter in filter_by:
      if letter.upper() not in "ABCDEFGHIJKLMOPQRSTUVWXYZ '-": abort(400)

  # init data object
  data = {
    "words_n_all"    : 0,
    "words_n_filter" : 0,
    "words_list"     : [],
    "first_rec"      : None,
    "last_rec"       : None,
    "prev_rec"       : None,
    "next_rec"       : None,
    "is_first_page"  : None,
    "is_last_page"   : None
  }

  # set operator base on direction
  operator = ">" if order_dir == "ASC" else "<"

  # fixed sql strings with parameters
  sql = [
    (f"SELECT COUNT(*) as c FROM lemmi", [ None ]),
    (f"SELECT COUNT(*) as c FROM lemmi", [ None ]),
    (f"SELECT ROWID,* FROM lemmi WHERE {offset_field} {operator} ? ORDER BY {offset_field} {order_dir} LIMIT ?", [ offset_value, PER_PAGE ]),
    (f"SELECT * FROM lemmi ORDER BY {offset_field} ASC LIMIT 1", [ None ]),
    (f"SELECT * FROM lemmi ORDER BY {offset_field} DESC LIMIT 1", [ None]),
    (f"SELECT COUNT(*) as c FROM lemmi WHERE lemma LIKE ?", [ f"{filter_by}%" ]),
    (f"SELECT ROWID,* FROM lemmi WHERE {offset_field} {operator} ? AND lemma LIKE ? ORDER BY {offset_field} {order_dir} LIMIT ?", \
        [ offset_value, f"{filter_by}%", PER_PAGE]),
    (f"SELECT * FROM lemmi WHERE lemma LIKE ? ORDER BY {offset_field} ASC LIMIT 1", [ f"{filter_by}%" ]),
    (f"SELECT * FROM lemmi WHERE lemma LIKE ? ORDER BY {offset_field} DESC LIMIT 1",[ f"{filter_by}%" ])
  ]
  
  # pop out unused sql
  if filter_by: 
      del sql[1:5] 
  else: 
      del sql[5:]
 
  # fetch data from db
  data["words_n_all"]    = int(query_db(sql[0][0], [ p for p in sql[0][1] if p ],  one = True)["c"]) 
  data["words_n_filter"] = int(query_db(sql[1][0], [ p for p in sql[1][1] if p ], one = True)["c"])
  data["words_list"]     = query_db(sql[2][0], [ p for p in sql[2][1] if p ])
  
  # reverse words list if necessary
  if order_dir == "DESC": data["words_list"] = data["words_list"][::-1]

  # if there are words
  if data["words_list"]:
    
    # add other pagination data
    data["first_rec"] = query_db(sql[3][0], [ p for p in sql[3][1] if p ],one = True)[offset_field]
    data["last_rec"]  = query_db(sql[4][0], [ p for p in sql[4][1] if p ], one = True)[offset_field]
    data["prev_rec"]  = data["words_list"][0][offset_field]
    data["next_rec"]  = data["words_list"][-1][offset_field]

  # add other pagination data
  data["is_first_page"] = data["first_rec"] == data["prev_rec"]
  data["is_last_page"]  = data["last_rec"] == data["next_rec"]
  data["prev_url"]      = url_for("main.index", filter_by = filter_by, offset_field = offset_field, offset_value = data["prev_rec"], order_dir = "DESC")
  data["next_url"]      = url_for("main.index", filter_by = filter_by, offset_field = offset_field, offset_value = data['next_rec'], order_dir = "ASC")
  
  # render view
  return render_template("main/index.html", data = data)

# --------------------------------------------------------------------------------
# View lemma
# --------------------------------------------------------------------------------
@bp_main.route("/consulta/<rowid>")
@login_required
def view_word(rowid):

  # retrieve lemma
  data = query_db("SELECT ROWID,* FROM lemmi WHERE rowid == ?", [ rowid ], one = True)

  # render view
  return render_template("main/view_lemma.html", data = data)

# --------------------------------------------------------------------------------
# Pagina inserimento lemmi 
# --------------------------------------------------------------------------------
@bp_main.route("/opera")
@login_required
def retrieve_links():

  # return view
  return render_template("main/retrieve_links.html")
