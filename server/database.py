import mysql.connector
from mysql.connector import Error
import base64

# Fungsi untuk koneksi ke database
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='HomeSecurity',
            user='root',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Fungsi untuk menambahkan data pengguna
def add_user(name, face_data):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO TrainingDataset (name, face_data) VALUES (%s, %s)", (name, face_data))
            connection.commit()
        except Error as e:
            print(f"Error adding user: {e}")
        finally:
            cursor.close()
            connection.close()

# Fungsi untuk mengambil data pengguna
def get_user_face_data(name):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT face_data FROM TrainingDataset WHERE name = %s", (name,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"Error retrieving user data: {e}")
        finally:
            cursor.close()
            connection.close()
