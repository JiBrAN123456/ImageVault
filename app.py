from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from models import db
from auth_routes import auth
from protected_routes import protected
from config import blacklist

# Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Configure Database & JWT
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Secret key for JWT
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # No expiry for now
app.config['JWT_BLACKLIST_ENABLED'] = True  # ✅ Enable Blacklisting
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ["access", "refresh"]

# ✅ Initialize Extensions
db.init_app(app)
jwt = JWTManager(app)


blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist 



# ✅ Register Blueprints

app.register_blueprint(protected, url_prefix='/api/protected')
app.register_blueprint(auth, url_prefix='/api/auth')


# ✅ Create Tables
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return {"message": "Flask backend with PostgreSQL is running!"}

if __name__ == "__main__":
    app.run(debug=True)
