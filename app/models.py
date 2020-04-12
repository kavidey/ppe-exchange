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
    is_admin = db.Column(db.Boolean())
    hospitals = db.relationship('Hospital', backref='author3', lazy='dynamic')

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
    contact = db.Column(db.String(140))
    name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    wants = db.relationship('Wants', backref='author1', lazy='dynamic')
    has = db.relationship('Has', backref='author2', lazy='dynamic')

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