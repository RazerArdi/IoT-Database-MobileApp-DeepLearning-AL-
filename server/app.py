from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
import numpy as np
import cv2
import os
from database import add_user, get_user_face_data
from keras.models import load_model

app = Flask(__name__)
CORS(app)

# Muat model
model = load_model('../face_model.h5')

# Muat data wajah dari folder
known_faces = []
known_names = []

if os.path.exists("faces"):
    for file in os.listdir("faces"):
        img = face_recognition.load_image_file(f"faces/{file}")
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_faces.append(encodings[0])
            known_names.append(os.path.splitext(file)[0])

# Endpoint: Pengenalan wajah dari gambar
@app.route('/upload', methods=['POST'])
def recognize_face():
    try:
        file = request.files['image']
        img = face_recognition.load_image_file(file)
        encodings = face_recognition.face_encodings(img)

        if encodings:
            encoding = encodings[0]
            results = face_recognition.compare_faces(known_faces, encoding)
            if True in results:
                name = known_names[results.index(True)]
                return jsonify({"status": "success", "name": name})

        return jsonify({"status": "failed", "message": "Face not recognized"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Endpoint: Tambah pengguna baru
@app.route('/add_user', methods=['POST'])
def add_user_api():
    try:
        data = request.json
        name = data['name']
        face_data = data['face_data']
        add_user(name, face_data)
        return jsonify({"message": "User added successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)