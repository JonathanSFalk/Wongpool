import os
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'neraneranera'

local_dev = True
fromdt = ""
todt = ""
