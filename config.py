import os

# base config
class Config(object):
  MAX_CONTENT_LENGTH = .5 * 1024 * 1024
  WTF_CSRF_SECRET_KEY = os.getenv("BASE_CSRF_KEY")

# dev config
class devConfig(Config):
  ENV = "development"
  DEBUG = True
  SECRET_KEY = os.getenv("DEV_SECRET_KEY")
  CACHE_TYPE = os.getenv("DEV_CACHE_TYPE")

# prod config
class prodConfig(Config):  
  SECRET_KEY = os.getenv("PROD_SECRET_KEY")
  CACHE_TYPE = os.getenv("PROD_CACHE_TYPE")
