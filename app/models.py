from app import login
from google.appengine.ext import ndb
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin,ndb.Model):
    id = ndb.IntegerProperty()
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    password_hash = ndb.StringProperty()
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Add me to the Database

u=User.query(User.id == 1).fetch(1)
if len(u)==0:
    poolboss = User(id=1,username="jf", email="jonathansfalk@gmail.com")
    poolboss.set_password("wong")
    poolboss.put()

@login.user_loader
def load_user(id):
    intid=int(id)
    return User.query(User.id == intid).get()
