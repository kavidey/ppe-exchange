from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap
from flask_mail import Mail

import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'

uname = ""
pwd = ""
try:
    uname = os.environ['EMAIL_USER']
    pwd = os.environ['EMAIL_PASSWORD']
except:
    print("\n[WARNING] You have not entered any email login information. PPE-Exchange wil not be able to send any emails\n")

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": uname,
    "MAIL_PASSWORD": pwd
}

app.config.update(mail_settings)
mail = Mail(app)

'''
import logging
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True
'''

from app import routes, models
