from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

# ################################################################################
# FORMS
# ################################################################################

# --------------------------------------------------------------------------------
# Recupera lemma tramite link
# --------------------------------------------------------------------------------
class RetrieveWordViaLinkForm(FlaskForm):
  
  # link
  link = StringField(
    label = 'Link del servizio on-line', 
    validators = [ 
      DataRequired(message="Il link è obbligatorio."),
    ],
    render_kw = { 
      "style": "width:100%", 
    },
  )

# --------------------------------------------------------------------------------
# Aggiungu lemma
# --------------------------------------------------------------------------------
class AddWordForm(FlaskForm):

  # word
  lemma = StringField(
    label = "Lemma",
    validators = [
      DataRequired(message="Il lemma è obbligatorio"),
    ],
    render_kw = {
      "style": "width:100%", 
    }
  )

  # word definition
  definition = TextAreaField(
    label = "Definizione",
    validators = [
      DataRequired(message="La definizione è obbligatoria."),
    ],
    render_kw = {
      "rows": 15,
      "style": "width:100%", 
    }
  )

# --------------------------------------------------------------------------------
# Cerca lemma
# --------------------------------------------------------------------------------
class SearchWordForm(FlaskForm):

  # word
  search_term = StringField(
    label = "Lemma",
    validators = [
      DataRequired(message="Il lemma è obbligatorio"),
    ],
    render_kw = {
      "style": "width:100%", 
    }
  )



