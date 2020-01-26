from flask import render_template, request, url_for, abort, redirect
from flask_login import login_required 
from webapp.database.sqlite import query_db
import re

from .schemas import Pagination
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
    
    # redirect
    return redirect(url_for("main.list_lemma", order_field = "lemma", order_dir = "ASC"))

# --------------------------------------------------------------------------------
# list lemma
# --------------------------------------------------------------------------------
@bp_main.route("/list")
@login_required
def list_lemma():

  # istantiate pydantic model with params
  data = Pagination(**request.args.to_dict())

  # set operator and offset_value
  if data.order_dir == "ASC":
    operator = ">" if data.offset_dir == "next" else "<" 
    if not data.offset_value: data.offset_value = "0"
  else:
    operator = "<" if data.offset_dir == "next" else ">"
    if not data.offset_value: data.offset_value = "{"

  # cache fixed sql queries with parameters
  sql_all = [
    [
        (f"SELECT COUNT(*) as c FROM lemmi", []),
        (f"SELECT COUNT(*) as c FROM lemmi", []),
        (f"SELECT * FROM lemmi ORDER BY {data.offset_field} ASC LIMIT 1", []),
        (f"SELECT * FROM lemmi ORDER BY {data.offset_field} DESC LIMIT 1", []),
        (f"SELECT ROWID,* FROM lemmi WHERE {data.offset_field} {operator} ? ORDER BY {data.order_field} ASC LIMIT ?", [ data.offset_value, PER_PAGE ]),
        (f"SELECT ROWID,* FROM lemmi WHERE {data.offset_field} {operator} ? ORDER BY {data.order_field} DESC LIMIT ?", [ data.offset_value, PER_PAGE ]),
    ],
    [
        (f"SELECT COUNT(*) as c FROM lemmi", []),
        (f"SELECT COUNT(*) as c FROM lemmi WHERE {data.filter_field} LIKE ?", [ f"{data.filter_value}%" ]),
        (f"SELECT * FROM lemmi WHERE {data.filter_field} LIKE ? ORDER BY {data.order_field} ASC LIMIT 1", [ f"{data.filter_value}%" ]),
        (f"SELECT * FROM lemmi WHERE {data.filter_field} LIKE ? ORDER BY {data.order_field} DESC LIMIT 1", [ f"{data.filter_value}%" ]),
        (f"SELECT ROWID,* FROM lemmi WHERE {data.filter_field} LIKE ? AND {data.offset_field} {operator} ? ORDER BY {data.order_field} ASC LIMIT ?", [ f"{data.filter_value}%", data.offset_value, PER_PAGE ]),
        (f"SELECT ROWID,* FROM lemmi WHERE {data.filter_field} LIKE ? AND {data.offset_field} {operator} ? ORDER BY {data.order_field} DESC LIMIT ?", [ f"{data.filter_value}%", data.offset_value, PER_PAGE ]),
    ]
  ]

  # choose sql queries
  sql = sql_all[0] if not data.filter_value else sql_all[1]

  # fetch data from db
  data.words_n_all    = int(query_db(sql[0][0], sql[0][1], one = True)["c"]) 
  data.words_n_filter = int(query_db(sql[1][0], sql[1][1], one = True)["c"])
  
  if data.order_dir == "ASC"  and data.offset_dir == "next": data.words_list = query_db(sql[-2][0], sql[-2][1])
  if data.order_dir == "ASC"  and data.offset_dir == "prev": data.words_list = query_db(sql[-1][0], sql[-1][1])
  if data.order_dir == "DESC" and data.offset_dir == "next": data.words_list = query_db(sql[-1][0], sql[-1][1])
  if data.order_dir == "DESC" and data.offset_dir == "prev": data.words_list = query_db(sql[-2][0], sql[-2][1])

  # if there are words
  if data.words_list:
    
    # reverse words if necessary
    if data.offset_dir == "prev":
      data.words_list = data.words_list[::-1]
     
    # add order_dir specific pagination data
    if data.order_dir == "ASC":
        data.first_rec = query_db(sql[2][0], sql[2][1], one = True)[data.offset_field]
        data.last_rec  = query_db(sql[3][0], sql[3][1], one = True)[data.offset_field]
    else:
        data.first_rec = query_db(sql[3][0], sql[3][1], one = True)[data.offset_field]
        data.last_rec  = query_db(sql[2][0], sql[2][1], one = True)[data.offset_field]

    # add other pagination data relative to words list
    data.prev_rec      = data.words_list[0][data.offset_field]
    data.next_rec      = data.words_list[-1][data.offset_field]
    
  # add final pagination data
  data.is_first_page = data.first_rec == data.prev_rec
  data.is_last_page  = data.last_rec == data.next_rec
  
  # render view
  return render_template("main/index.html", data = data.dict())

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
