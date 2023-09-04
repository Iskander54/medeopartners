from datetime import datetime
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from medeo import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    firstname = db.Column(db.String(20), unique=False, nullable=False)
    lastname = db.Column(db.String(20), unique=False, nullable=False)
    dob = db.Column(db.DateTime, unique=True, nullable=False)
    addresses = db.relationship('Address', backref='account', lazy=True)
    taxreturns = db.relationship('Taxreturn', backref='user',lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    line1 = db.Column(db.String(120), unique=True, nullable=False)
    line2 = db.Column(db.String(120), unique=True, nullable=False)
    zip = db.Column(db.String(6), unique=True, nullable=False)
    city = db.Column(db.String(30), unique=True, nullable=False)
    state = db.Column(db.String(30), unique=True, nullable=False)

class Taxreturn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=False,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    taxdocs = db.relationship('Taxdoc', backref='taxreturn',lazy=True)


class Taxdoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    path = db.Column(db.String(50), unique=True, nullable=False)
    year = db.Column(db.Integer, unique=False,nullable=False)
    taxreturn_id = db.Column(db.Integer, db.ForeignKey('taxreturn.id'),nullable=False)
