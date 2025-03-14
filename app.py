from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize database
db = SQLAlchemy(app)

@app.route("/")
def home():
    try:
        # Test database connection
        with db.engine.connect() as connection:
            connection.execute("SELECT 1")
        return {"message": "Database connection successful!"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(debug=True)

