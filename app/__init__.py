from flask_mail import Mail
from app.app import make_app

import os

app, db, migrate, bootstrap, login = make_app(__name__)

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
