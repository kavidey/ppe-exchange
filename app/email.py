from flask_mail import Message
from flask import render_template
from app import mail
from app import app

def send_user_verification(username, auth_key, hostname, email):
    url = "http://"+hostname + "/verify?key="+auth_key

    msg = Message(subject="PPE Exchange User Verification",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body="Click this link to set the admin password for PPE Exchange \n"+url,
                    html=render_template("email_verify_user.html", username=username, link=url))
    mail.send(msg)