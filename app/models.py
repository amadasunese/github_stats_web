from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(80))
    email = db.Column(db.String(120))
    profession = db.Column(db.String(80))
    telephone = db.Column(db.String(20))
    profile_photo = db.Column(db.String(255))  # Store the file path here

    def __init__(self, username, password, name=None, email=None, profession=None, telephone=None, profile_photo=None):
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.profession = profession
        self.telephone = telephone
        self.profile_photo = profile_photo

    def __repr__(self):
        return f'<User {self.username}>'

# Define a RegistrationLog model to log user registrations
class RegistrationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_description = db.Column(db.String(255))

    def __init__(self, user_id, event_description):
        self.user_id = user_id
        self.event_description = event_description

# Define a UsageLog model to log user interactions and usage
class UsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    event_description = db.Column(db.String(255))

    def __init__(self, user_id, event_description):
        self.user_id = user_id
        self.event_description = event_description

# Adding History model
class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<History {self.username}>'
