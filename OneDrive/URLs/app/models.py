from datetime import datetime
from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique = True, nullable = False)
    email = db.Column(db.String(150), unique = True, nullable = False)
    password = db.Column(db.String(200), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    is_admin = db.Column(db.Boolean, default = False)
    links = db.relationship('Link', backref = 'user', lazy = True)

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(500), nullable = False)
    short_url = db.Column(db.String(100), nullable = False, unique = True)
    clicks = db.Column(db.Integer, default = 0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    clicks_info = db.relationship('Click', backref='link', lazy=True)

class Click(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(200))
    country = db.Column(db.String(100))
    link_id = db.Column(db.Integer, db.ForeignKey('link.id'), nullable=False)