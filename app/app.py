from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap

# HACK
def make_app(name):
	app = Flask(name)
	app.config.from_object(Config)
	db = SQLAlchemy(app)
	migrate = Migrate(app, db)
	bootstrap = Bootstrap(app)
	login = LoginManager(app)
	login.login_view = 'login'
	return app, db, migrate, bootstrap, login