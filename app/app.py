from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event


from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_bootstrap import Bootstrap

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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