import os
import face_recognition
from keras.models import load_model
import mysql.connector

# **1. Fungsi untuk Memuat Model TensorFlow**
def load_face_model(model_path='face_model.h5'):
    try:
        model = load_model(model_path)
        print(f"Model loaded successfully from {model_path}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# **2. Fungsi untuk Koneksi ke Database MySQL**
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

# **3. Fungsi untuk Memuat Data Wajah yang Dikenal**
def load_known_faces(folder_path="faces"):
    known_faces = []
    known_names = []
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            img = face_recognition.load_image_file(f"{folder_path}/{file}")
            encodings = face_recognition.face_encodings(img)
            if encodings:
                known_faces.append(encodings[0])
                known_names.append(os.path.splitext(file)[0])
    return known_faces, known_names
