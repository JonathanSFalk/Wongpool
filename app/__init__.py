from flask import Flask
from flask_bootstrap import Bootstrap
from cfg import Config
#from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

#login = LoginManager(app)
#login.login_view = 'login'
bootstrap=Bootstrap(app)

from app import routes




