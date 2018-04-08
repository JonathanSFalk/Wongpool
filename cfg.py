import os
from google.appengine.ext import ndb
from update import LastUpdate

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'neraneranera'
    SPRING = False
    LastUpdate = ndb.Key(LastUpdate,1,parent=ndb.Key('Project','Wong')).get(use_cache=False).lu
    def __init__(self):
        self.lu = ndb.Key(LastUpdate,1,parent=ndb.Key('Project','Wong')).get(use_cache=False).lu


