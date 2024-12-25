from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
import base64
import numpy as np
import cv2
import os
import mysql.connector
from keras.models import load_model

app = Flask(__name__)
CORS(app)  # Mengaktifkan CORS untuk semua rute

# **1. Muat Model untuk Pengenalan Wajah**
model = load_model('face_model.h5')

# **2. Koneksi Database MySQL**
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='HomeSecurity',
            user='root',
            password=''  # Sesuaikan password MySQL Anda
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# **3. Muat Data Wajah yang Dikenal dari Folder**
known_faces = []
known_names = []

if os.path.exists("faces"):
    for file in os.listdir("faces"):
        img = face_recognition.load_image_file(f"faces/{file}")
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_faces.append(encodings[0])
            known_names.append(os.path.splitext(file)[0])

# **4. Endpoint: Pengenalan Wajah dari Gambar yang Diunggah**
@app.route('/upload', methods=['POST'])
def recognize_face():
    try:
        file = request.files['image']  # Ambil file gambar
        img = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(img)

        if len(encodings) > 0:
            encoding = encodings[0]
            results = face_recognition.compare_faces(known_faces, encoding)
            if True in results:
                name = known_names[results.index(True)]
                return jsonify({"status": "success", "name": name})

        return jsonify({"status": "failed", "message": "Face not recognized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# **5. Endpoint: Pengenalan Wajah dari ESP32**
@app.route('/detect', methods=['POST'])
def detect_face():
    try:
        # Ambil gambar dari data POST
        img_data = request.data
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Proses gambar untuk prediksi
        face = cv2.resize(image, (224, 224))  # Ukuran input model
        face = np.expand_dims(face, axis=0) / 255.0
        result = model.predict(face)

        # Ambang batas (contoh: 0.5 untuk deteksi wajah)
        if result[0][0] > 0.5:
            return jsonify({"status": "recognized"})
        else:
            return jsonify({"status": "not recognized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# **6. Endpoint: Tambah Data Pengguna Baru ke Database**
@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        data = request.json
        name = data['name']
        face_data = data['face_data']  # Base64 string

        # Konversi Base64 ke binary
        face_binary = np.frombuffer(base64.b64decode(face_data), np.uint8)
        connection = connect_to_db()

        if connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO Users (name, face_data) VALUES (%s, %s)",
                (name, face_binary)
            )
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({"message": "User added successfully!"})
        return jsonify({"message": "Failed to connect to database!"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)