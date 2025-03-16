import boto3
import os
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from models import db, Image
import openai

load_dotenv()

image_bp = Blueprint('image', __name__)

# AWS S3 Configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY



# Initialize S3 Client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# ✅ Image Upload API (Stores user info)
@image_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_image():
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # ✅ Secure filename
    filename = secure_filename(file.filename)
    file_extension = filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    try:
        # ✅ Upload file to S3
        s3.upload_fileobj(
            file,
            AWS_BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ACL": "public-read", "ContentType": file.content_type}
        )

        # ✅ Generate file URL
        file_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"

        # ✅ Save Image Record in Database
        new_image = Image(user_id=user_id, image_key=unique_filename, image_url=file_url)
        db.session.add(new_image)
        db.session.commit()

        return jsonify({"message": "Image uploaded successfully", "image_url": file_url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ✅ List User's Uploaded Images
@image_bp.route('/list', methods=['GET'])
@jwt_required()
def list_images():
    user_id = get_jwt_identity()

    try:
        # ✅ Get only images uploaded by the logged-in user
        user_images = Image.query.filter_by(user_id=user_id).all()

        # ✅ Convert to JSON format
        images = [{"image_url": img.image_url, "image_key": img.image_key} for img in user_images]

        return jsonify({"images": images}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ✅ AI Image Analysis API
@image_bp.route("/analyze", methods=["POST"])
@jwt_required()
def analyze_image():
    data = request.get_json()
    image_url = data.get("image_url")

    if not image_url:
        return jsonify({"error": "Image URL is required"}), 400

    try:
        # ✅ Call OpenAI Vision API
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "system", "content": "You are an AI image analyst."},
                {"role": "user", "content": f"Describe the following image in detail: {image_url}"}
            ],
            max_tokens=100
        )

        description = response["choices"][0]["message"]["content"]

        return jsonify({"message": "Image analyzed successfully", "description": description}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500