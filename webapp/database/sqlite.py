import sqlite3
import os.path
from contextlib import closing

from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "lemmario.sqlite")

# shape result as dict
def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

# get db instance
def get_db():

  # attach db to global
  if "db" not in g:
    g.db = sqlite3.connect(db_path)
    g.db.row_factory = dict_factory

  # return db
  return g.db

# perform query
def query_db(query, args=(), one=False):
  # query and close cursor
  with closing(get_db().cursor().execute(query, args)) as cur:
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv

# tear down db on closing
def close_db(e=None):

  # close connection
  db = g.pop('db', None)
  if db is not None:
      db.close()
