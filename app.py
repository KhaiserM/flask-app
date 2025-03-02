from flask import Flask, request, jsonify
import boto3
import psycopg2
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Database Connection
DB_HOST = "your-rds-endpoint"
DB_NAME = "postgres"
DB_USER = "admin"
DB_PASS = "password123"

conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS)
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT,
        file_url TEXT
    )
""")
conn.commit()

# S3 Configuration
S3_BUCKET = "my-flask-app-bucket"
S3_REGION = "ap-south-1"
s3 = boto3.client('s3', region_name=S3_REGION)

# API: Upload a file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'username' not in request.form:
        return jsonify({"error": "Missing file or username"}), 400
    
    file = request.files['file']
    username = request.form['username']
    
    filename = secure_filename(file.filename)
    s3.upload_fileobj(file, S3_BUCKET, filename)
    file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"

    cursor.execute("INSERT INTO users (username, file_url) VALUES (%s, %s)", (username, file_url))
    conn.commit()

    return jsonify({"message": "File uploaded", "file_url": file_url})

# API: Get all stored data
@app.route('/users', methods=['GET'])
def get_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return jsonify(users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
