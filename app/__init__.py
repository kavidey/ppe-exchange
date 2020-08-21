from flask_mail import Mail
from app.app import make_app
import yaml
import os

app, db, migrate, bootstrap, login = make_app(__name__)

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

    server_settings = {
        "PPE_HOSTNAME": config['server']['hostname']
    }
    app.config.update(server_settings)

    mail_settings = {
        "MAIL_SERVER": 'smtp.gmail.com',
        "MAIL_PORT": 465,
        "MAIL_USE_TLS": False,
        "MAIL_USE_SSL": True,
        "MAIL_USERNAME": config['email']['uname'],
        "MAIL_PASSWORD": config['email']['pwd']
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
