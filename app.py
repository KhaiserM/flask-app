from flask import Flask, request, jsonify
import psycopg2
import boto3
import os

app = Flask(__name__)

# Database Connection
DB_HOST = "flask-db.c123xyz.ap-south-1.rds.amazonaws.com"  # Replace with your RDS endpoint
DB_NAME = "postgres"
DB_USER = "admin"
DB_PASS = "password123"

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

@app.route("/")
def home():
    return "Flask App Running!"

@app.route("/data", methods=["POST"])
def save_data():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO my_table (name, email) VALUES (%s, %s)", (data["name"], data["email"]))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Data saved!"})

@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files['file']
    s3 = boto3.client('s3')
    s3.upload_fileobj(file, "my-flask-app-bucket", file.filename)
    return jsonify({"message": "File uploaded to S3!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
