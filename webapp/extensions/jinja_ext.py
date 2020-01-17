from base64 import b64encode

def format_datetime(value, format="%d %b %Y %I:%M %p"):    
  if value is None: return ""
  return value.strftime(format)

def btoa(value):
  if value is None: return ""
  return b64encode(bytes(value, 'utf-8')).decode("utf-8")

# attacher
def attach_jinja(app):
  app.jinja_env.filters['to_data_time'] = format_datetime
  app.jinja_env.filters['b64_encode'] = btoa
