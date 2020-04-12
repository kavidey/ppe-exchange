from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'

'''
import logging
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.disabled = True
'''

from app import routes, models

#from controllers import auth
# app.register_blueprint(auth.bp)
 
bootstrap = Bootstrap(app)

