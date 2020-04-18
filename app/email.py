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

def send_hospital_exchange_creation(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="A new PPE exchange " + exchange_id + "was created for your hospital."
    text2="and verify your hospital's participation in the exchange."
    msg = Message(subject="PPE Exchange - New Exchange Created",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange_creation.html", username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_exchange_own_verified(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="Thank you for verifying your participation in PPE exchange " + exchange_id + "."
    text2="to see the latest updates on this exchange."
    msg = Message(subject="PPE Exchange - Exchange Participation Verified",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange_creation.html", username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_exchange_partner_verified(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="A partner hospital in PPE exchange " + exchange_id + "has verified their participation."
    text2="to see the latest updates on this exchange, and once all partners have verified to indicate that you have shipped and received your PPE."
    msg = Message(subject="PPE Exchange - Partner Participation Verified",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange.html", text=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_exchange_all_verified(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="All partner hospitals (including yours) in PPE exchange " + exchange_id + "have verified their participation."
    text2="to see the latest updates on this exchange, and to indicate that you have shipped and received your PPE."
    msg = Message(subject="PPE Exchange - Partner Participation Verified",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange.html", text=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_exchange_own_shipped(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="Thank you for confirming a shipment for PPE exchange" + exchange_id+"." 
    text2="to see the latest updates on this exchange."
    msg = Message(subject="PPE Exchange - Exchange Shipping Verification",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body = " ",
                    html=render_template("email_exchange.html", text1=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_exchange_partner_shipped(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="A hospital partner in the PPE exchange " + exchange_id + "has shipped PPE to your hospital."
    text2="once the shipment has arrived to confirm your receipt of the exchange shipment."
    msg = Message(subject="PPE Exchange - Exchange Partner Shipped",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange.html", text1=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_exchange_own_received(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="Thank you for confirming receipt of a shipment for PPE exchange" + exchange_id+"." 
    text2="to see the latest updates on this exchange."
    msg = Message(subject="PPE Exchange - Exchange Receipt Verification",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange.html", text1=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_exchange_partner_received(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="A hospital partner in the PPE exchange " + exchange_id + "has received PPE from your hospital."
    text2="to see the latest updates on this exchange."
    msg = Message(subject="PPE Exchange - Exchange Partner Received",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange.html", text1=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_exchange_all_received(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="All partner hospitals (including yours) in PPE exchange " + exchange_id + "have received their expected PPE."
    text2="to see that this exchange is now complete."
    msg = Message(subject="PPE Exchange - Exchange Complete",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange.html", text=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_admin_canceled(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="The PPE Exchange administrator has canceled PPE exchange " + exchange_id + "."
    text2="to see that this exchange has been canceled."
    msg = Message(subject="PPE Exchange - Exchange Canceled by Administrator",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange.html", text=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)

def send_hospital_hospital_canceled(username, hostname, email, exchange_id):
    url = "http://"+hostname + "/exchanges"
    text1="A partner hospital has canceled PPE exchange " + exchange_id + "."
    text2="to see that this exchange has been canceled. Please stay tuned for a new exchange to be created shortly."
    msg = Message(subject="PPE Exchange - Exchange Canceled by Hosptial Partner",
                    sender=app.config.get("MAIL_USERNAME"),
                    recipients=[email],
                    body=" ",
                    html=render_template("email_exchange.html", text=text1, text2=text2, username=username, link=url, linking=True, id=exchange_id))
    mail.send(msg)
