from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self):
        self.id = 0
        self.username = ""
        self.email=""
        self.password_hash=""
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Make me the only user
poolboss = User()
poolboss.id=1
poolboss.username="jf"
poolboss.email="jonathansfalk@gmail.com"
poolboss.set_password("wong")

@login.user_loader
def load_user(id):
    intid=int(id)
    if intid==1:
        return poolboss
    else:
        return None
