from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean(), default=False)
    is_verified = db.Column(db.Boolean(), default=False)
    verification_key = db.Column(db.String(128))
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Hospital(db.Model):
    __tablename__ = "hospital"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    contact = db.Column(db.String(140), default="")
    address = db.Column(db.String(140), default="")
    name = db.Column(db.String(140))
    wants = db.relationship('Wants', backref='author1', lazy='dynamic')
    has = db.relationship('Has', backref='author2', lazy='dynamic')
    users = db.relationship('User', backref='author3', lazy='dynamic')

    def __repr__(self):
        return '<Hospital {}>'.format(self.name)

class PPE(db.Model):
    __tablename__ = "ppe"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sku = db.Column(db.String(16), index=True)
    desc = db.Column(db.String(200))
    img = db.Column(db.BLOB())
    wants = db.relationship('Wants', backref='author4', lazy='dynamic')
    has = db.relationship('Has', backref='author5', lazy='dynamic')

    def __repr__(self):
        return '<PPE {}>'.format(self.sku)

class Wants(db.Model):
    __tablename__ = "wants"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    ppe_id = db.Column(db.Integer, db.ForeignKey('ppe.id'))
    count = db.Column(db.Integer)

    def __repr__(self):
        return '<Wants {}>'.format(self.count)

class Has(db.Model):
    __tablename__ = "has"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    ppe_id = db.Column(db.Integer, db.ForeignKey('ppe.id'))
    count = db.Column(db.Integer)

    def __repr__(self):
        return '<Has {}>'.format(self.count)

# EXCHANGE_STATUS
# normal completion: EXCHANGE_COMPLETE = 1
EXCHANGE_COMPLETE = 1
# administrator had to complete: EXCHANGE_COMPLETE_ADMIN = 2
EXCHANGE_COMPLETE_ADMIN = 2
# exchange complete, canceled by a hospital: EXCHANGE_COMPLETE_CANCELED = 3
EXCHANGE_COMPLETE_CANCELED = 3

# exchange has been created, but not verified by parties: EXCHANGE_UNVERIFIED = 11
EXCHANGE_UNVERIFIED = 11
# exchange created, verified by parties, but not complete: EXCHANGE_IN_PROGRESS = 12
EXCHANGE_IN_PROGRESS = 12

class Exchanges(db.Model):
    __tablename__ = "exchanges"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer)
    def __repr__(self):
        return '<Exchanges {}>'.format(self.id)

# HOSPITAL_EXCHANGE_STATUS
# exchange has not been accepted by hospital yet: NOT_ACCEPTED = 1
NOT_ACCEPTED = 1
# exchange has been accepted by hospitals, but not shipped: ACCEPTED_NOT_SHIPPED = 2
ACCEPTED_NOT_SHIPPED = 2
# exchange has been shipped by hospital1, but not received by hospital2: ACCEPTED_SHIPPED = 3
ACCEPTED_SHIPPED = 3
# exchange has been shipped by hospital1, and received by hospital2: ACCEPTED_RECEIVED = 4
ACCEPTED_RECEIVED = 4
# exchange has been canceled by a hospital: CANCELED = 11
CANCELED = 11

# exchange has not been shipped/received by hospital: EQUIPMENT_VERIFIED
class Exchange(db.Model):
    __tablename__ = "exchange"
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchanges.id'))
    hospital1 = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    hospital1_accept = db.Column(db.Integer)
    hospital2 = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    hospital2_accept = db.Column(db.Integer)
    ppe = db.Column(db.Integer, db.ForeignKey('ppe.id'))
    count = db.Column(db.Integer)
    verify_status = db.Column(db.Integer)
    shipping_status = db.Column(db.Integer)
    
    def __repr__(self):
        return '<Has {}>'.format(self.id)