from flask import render_template, request, url_for, abort, redirect
from flask_login import login_required 
from webapp.database.sqlite import query_db
import re

from . import bp_main

# ################################################################################
# GLOBAL CONSTANTS AND VARS
# ################################################################################
PER_PAGE = 10

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
  "offset_field"   : None,
  "offset_dir"     : None,
  "filter_field"   : None,
  "filter_value"   : None,
  "order_dir"      : None
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
    return redirect(url_for("main.list_lemma", offset_field = "lemma", order_dir = "ASC"))

# --------------------------------------------------------------------------------
# list lemma
# --------------------------------------------------------------------------------
@bp_main.route("/list")
@login_required
def list_lemma():

  # cache params
  offset_field = request.args.get("offset_field", 'lemma')
  offset_value = request.args.get("offset_value", None)
  offset_dir   = request.args.get("offset_dir", "next")
  filter_field = request.args.get("filter_field", None)
  filter_value = request.args.get("filter_value", None)
  order_dir = request.args.get("order_dir", "next")

  # sanity check on params
  if any((
    offset_field not in ("lemma","visited"),
    offset_value and not re.sub("\s|'|\-","", offset_value).isalnum(),  
    offset_dir not in ("prev", "next"),
    filter_field and filter_field not in ("lemma",),
    filter_value and not re.sub("\s|'|\-","", filter_value).isalnum(),
    order_dir not in ("ASC", "DESC")
  )): abort(400)

  # set operator and offset_value
  if order_dir == "ASC":
    operator = ">" if offset_dir == "next" else "<" 
    if not offset_value: offset_value = "0"
  else:
    operator = "<" if offset_dir == "next" else ">"
    if not offset_value: offset_value = "{"

  # cache fixed sql queries with parameters
  sql_all = [
    [
        (f"SELECT COUNT(*) as c FROM lemmi", []),
        (f"SELECT COUNT(*) as c FROM lemmi", []),
        (f"SELECT * FROM lemmi ORDER BY {offset_field} ASC LIMIT 1", []),
        (f"SELECT * FROM lemmi ORDER BY {offset_field} DESC LIMIT 1", []),
        (f"SELECT ROWID,* FROM lemmi WHERE {offset_field} {operator} ? ORDER BY {offset_field} ASC LIMIT ?", [ offset_value, PER_PAGE ]),
        (f"SELECT ROWID,* FROM lemmi WHERE {offset_field} {operator} ? ORDER BY {offset_field} DESC LIMIT ?", [ offset_value, PER_PAGE ]),
    ],
    [
        (f"SELECT COUNT(*) as c FROM lemmi", []),
        (f"SELECT COUNT(*) as c FROM lemmi WHERE {filter_field} LIKE ?", [ f"{filter_value}%" ]),
        (f"SELECT * FROM lemmi WHERE {filter_field} LIKE ? ORDER BY {offset_field} ASC LIMIT 1", [ f"{filter_value}%" ]),
        (f"SELECT * FROM lemmi WHERE {filter_field} LIKE ? ORDER BY {offset_field} DESC LIMIT 1", [ f"{filter_value}%" ]),
        (f"SELECT ROWID,* FROM lemmi WHERE {filter_field} LIKE ? AND {offset_field} {operator} ? ORDER BY {offset_field} ASC LIMIT ?", [ f"{filter_value}%", offset_value, PER_PAGE ]),
        (f"SELECT ROWID,* FROM lemmi WHERE {filter_field} LIKE ? AND {offset_field} {operator} ? ORDER BY {offset_field} DESC LIMIT ?", [ f"{filter_value}%", offset_value, PER_PAGE ]),
    ]
  ]

  # choose sql queries
  sql = sql_all[0] if not filter_value else sql_all[1]

  # fetch data from db
  data["words_n_all"]    = int(query_db(sql[0][0], sql[0][1], one = True)["c"]) 
  data["words_n_filter"] = int(query_db(sql[1][0], sql[1][1], one = True)["c"])
  
  if order_dir == "ASC" and offset_dir == "next": data["words_list"]  = query_db(sql[-2][0], sql[-2][1])
  if order_dir == "ASC" and offset_dir == "prev": data["words_list"]  = query_db(sql[-1][0], sql[-1][1])
  if order_dir == "DESC" and offset_dir == "next": data["words_list"] = query_db(sql[-1][0], sql[-1][1])
  if order_dir == "DESC" and offset_dir == "prev": data["words_list"] = query_db(sql[-2][0], sql[-2][1])

  # if there are words
  if data["words_list"]:
    
    # reverse words if necessary
    if offset_dir == "prev":
      data["words_list"] = data["words_list"][::-1]
     
    # add order_dir specific pagination data
    if order_dir == "ASC":
        data["first_rec"] = query_db(sql[2][0], sql[2][1], one = True)[offset_field]
        data["last_rec"]  = query_db(sql[3][0], sql[3][1], one = True)[offset_field]
    else:
        data["first_rec"] = query_db(sql[3][0], sql[3][1], one = True)[offset_field]
        data["last_rec"]  = query_db(sql[2][0], sql[2][1], one = True)[offset_field]

    # add other pagination data
    data["prev_rec"]      = data["words_list"][0][offset_field]
    data["next_rec"]      = data["words_list"][-1][offset_field]
    data["is_first_page"] = data["first_rec"] == data["prev_rec"]
    data["is_last_page"]  = data["last_rec"] == data["next_rec"]
    data["offset_field"]  = offset_field
    data["offset_value"]  = offset_value
    data["offset_dir"]    = offset_dir
    data["filter_field"]  = filter_field
    data["filter_value"]  = filter_value
    data["order_dir"]     = order_dir
  
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
