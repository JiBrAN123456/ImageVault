from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True , default= lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique = True , nullable = False)
    password_hash = db.Column(db.String(256), nullable = False)
    created_at = db.Column(db.DateTime, default= datetime.utcnow)


    
    def set_password(self, password):
        if password:  # ✅ Prevents setting NULL passwords
            self.password_hash = generate_password_hash(password)
        else:
            raise ValueError("Password cannot be empty")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Image(db.Model):
    id = db.Column(db.String(36), primary_key = True , default= lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable = False)
    filename = db.Column(db.String(255), nullable = False)
    s3_url = db.Column(db.String(500), nullable = False)
    uploaded_at = db.Column(db.DateTime, default =datetime.utcnow)

    user = db.relationship('User', backref=db.backref('images', lazy = True))

