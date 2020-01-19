from flask import render_template, request, url_for, abort, redirect
from flask_login import login_required 
from webapp.database.sqlite import query_db
import re

from . import bp_main

# ################################################################################
# GLOBAL CONSTANTS AND VARS
# ################################################################################
PER_PAGE = 4

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
  "is_last_page"   : None,
  "prev_url"       : None,
  "next_url"       : None,
}


# ################################################################################
# ROUTES 
# ################################################################################

# --------------------------------------------------------------------------------
# Homepage
# --------------------------------------------------------------------------------
@bp_main.route("/")
@login_required
def index():
    # redirect
    return redirect(url_for("main.list", offset_field = "lemma", offset_value = None, order_dir = "ASC"))

@bp_main.route("/list/offset_field/<offset_field>/order_dir/<order_dir>")
@login_required
def list(offset_field, order_dir):

  # cache params
  offset_value = request.args.get("offset_value", None)
  offset_dir = request.args.get("offset_dir", "next")

  # sanity checks
  if offset_field not in ("lemma","visited"): abort(400)
  if offset_value and not re.sub("\s|'|\-","", offset_value).isalnum(): abort(400)
  if offset_dir not in ("prev", "next"): abort(400)
  if order_dir not in ("ASC", "DESC"): abort(400)

  # set operator base on offset_dir and order_dir
  if order_dir == "ASC":
    operator = ">" if offset_dir == "next" else "<" 
    if not offset_value: offset_value = "0"

  if order_dir == "DESC": 
    operator = "<" if offset_dir == "next" else ">"
    if not offset_value: offset_value = "zz"

  # fixed sql queries with parameters
  sql = [
        (f"SELECT COUNT(*) as c FROM lemmi",),
        (f"SELECT * FROM lemmi ORDER BY {offset_field} ASC LIMIT 1",),
        (f"SELECT * FROM lemmi ORDER BY {offset_field} DESC LIMIT 1",),
        (f"SELECT ROWID,* FROM lemmi WHERE {offset_field} {operator} ? ORDER BY {offset_field} ASC LIMIT ?", [ offset_value, PER_PAGE ]),
        (f"SELECT ROWID,* FROM lemmi WHERE {offset_field} {operator} ? ORDER BY {offset_field} DESC LIMIT ?", [ offset_value, PER_PAGE ]),
    ]

  # fetch data from db
  data["words_n_all"]    = int(query_db(sql[0][0], one = True)["c"]) 
  data["words_n_filter"] = data["words_n_all"]
  
  if order_dir == "ASC" and offset_dir == "next": data["words_list"]  = query_db(sql[-2][0], sql[-1][1])
  if order_dir == "ASC" and offset_dir == "prev": data["words_list"]  = query_db(sql[-1][0], sql[-1][1])
  if order_dir == "DESC" and offset_dir == "next": data["words_list"] = query_db(sql[-1][0], sql[-1][1])
  if order_dir == "DESC" and offset_dir == "prev": data["words_list"] = query_db(sql[-2][0], sql[-1][1])

  if offset_dir == "prev":
    data["words_list"] = data["words_list"][::-1]

  # if there are words
  if data["words_list"]:
     
    # add other pagination data
    if order_dir == "ASC":
        data["first_rec"] = query_db(sql[1][0], one = True)[offset_field]
        data["last_rec"]  = query_db(sql[2][0], one = True)[offset_field]
    else:
        data["first_rec"] = query_db(sql[2][0], one = True)[offset_field]
        data["last_rec"]  = query_db(sql[1][0], one = True)[offset_field]

    data["prev_rec"]      = data["words_list"][0][offset_field]
    data["next_rec"]      = data["words_list"][-1][offset_field]
    data["is_first_page"] = data["first_rec"] == data["prev_rec"]
    data["is_last_page"]  = data["last_rec"] == data["next_rec"]
    data["prev_url"]      = url_for("main.list", offset_field = offset_field, offset_value = data["prev_rec"], offset_dir = "prev", order_dir = order_dir)
    data["next_url"]      = url_for("main.list", offset_field = offset_field, offset_value = data['next_rec'], offset_dir = "next", order_dir = order_dir)
  
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
