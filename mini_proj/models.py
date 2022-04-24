from mini_proj import db
from passlib.hash import pbkdf2_sha256 as sha256

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String,unique=True)
    password = db.Column(db.String)
    google_secret = db.Column(db.String)
    qrcode_uri = db.Column(db.String)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def check_user(cls,email):
        return cls.query.filter_by(email=email).first()

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String, nullable=False)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        db.session.close()

def genearte_hash(password):
    return sha256.hash(password)

def verify_hash(password,hash):
    return sha256.verify(password,hash)
