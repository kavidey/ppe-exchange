from flask import Flask, render_template
from flask_mail import Mail, Message
import os
import random
import string
import json

app = Flask(__name__)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['EMAIL_USER'],
    "MAIL_PASSWORD": os.environ['EMAIL_PASSWORD']
}

app.config.update(mail_settings)
mail = Mail(app)

hostname = "localhost:5000"
admin_email = "aninddey@gmail.com"

if __name__ == '__main__':
    auth_key = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(128))
    with open("auth_key.txt", "w") as text_file:
        info = {
            "key": auth_key,
            "admin_email": admin_email
        }
        text_file.write(json.dumps(info))

    url = "http://"+hostname + "/admin_auth?key="+auth_key

    with app.app_context():
        msg = Message(subject="PPE Exchange Admin Setup",
                      sender=app.config.get("MAIL_USERNAME"),
                      recipients=[admin_email],
                      body="Click this link to set the admin password for PPE Exchange \n"+url,
                      html=render_template("reset-password.html", username="Exchange Administrator", link=url))
        mail.send(msg)