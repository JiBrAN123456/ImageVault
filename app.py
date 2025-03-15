from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from models import db
from auth_routes import auth
from protected_routes import protected


# Load environment variables
load_dotenv()

app = Flask(__name__)

# ✅ Configure Database & JWT
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Secret key for JWT

# ✅ Initialize Extensions
db.init_app(app)
jwt = JWTManager(app)

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
