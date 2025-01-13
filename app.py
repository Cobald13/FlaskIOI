from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os
import requests

app = Flask(__name__)
CORS(app)

backendUrl = 'https://pure-chicken-urgently.ngrok-free.app'

# MongoDB Atlas connection string
client = MongoClient("mongodb+srv://Cobald13:Mp5K1Ll5@projektioi.o1jsd.mongodb.net/?retryWrites=true&w=majority&appName=projektIOI")
db = client['IOI']  # Replace with your database name
painters_collection = db['Slikarji']  # Replace with your collection name

# Load the pre-trained model
FILE_ID = "1n8TBfw2Yckn_Xm_r4asvfdXtbHQ6vkt0"
API_KEY = "AIzaSyCI9KszVXQ6usHwf5Fn8RjCW5JfQ4sjkus"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'painting_recognition_model.h5')

def download_model(file_id, path, api_key):
    """Download the model file from Google Drive using the API."""
    if not os.path.exists(path):
        print("Downloading model from Google Drive via API...")
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={api_key}"

        # Perform the request and download the file in chunks
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=32768):
                    if chunk:
                        f.write(chunk)
            print("Model downloaded and saved.")

            # Verify the file format
            if not verify_h5_file(path):
                os.remove(path)  # Delete invalid file
                raise ValueError("Downloaded file is not a valid .h5 file.")
        else:
            raise Exception(f"Failed to download file. HTTP Status Code: {response.status_code}")
    else:
        print("Model already exists.")

def verify_h5_file(path):
    """Check if the file is a valid HDF5 model file."""
    try:
        tf.keras.models.load_model(path)
        return True
    except Exception as e:
        print(f"File verification failed: {e}")
        return False

# Download the model if needed
download_model(FILE_ID, MODEL_PATH, API_KEY)

# Load the model
model = tf.keras.models.load_model(MODEL_PATH)

def verify_h5_file(path):
    try:
        tf.keras.models.load_model(path)
        return True
    except Exception as e:
        print(f"File verification failed: {e}")
        return False

verify_h5_file(MODEL_PATH)

# **CLASS_TO_ID_MAP**
# This mapping links the model's predicted class indices to MongoDB `_id` values for painters
CLASS_TO_ID_MAP = {
    0: "kofetarica",
    1: "poletje",
    2: "fani",
    3: "otroci_druzine_buchler",
    4: "doma",
    5: "nismo_poslednji"
}

PAINTING_TO_PAINTER_MAP = {
    "kofetarica": "kobilca",
    "poletje": "kobilca",
    "fani": "kobilca",
    "nismo_poslednji": "music",
    "doma": "petkovsek",
    "otroci_druzine_buchler": "tominc"
}

# Helper function to process the image
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalize the image
    return img_array

# Routes
@app.route('/painters', methods=['GET'])
def get_painters():
    painters = list(painters_collection.find({}))
    for painter in painters:
        painter['_id'] = str(painter['_id'])  # Convert _id to string
    return jsonify(painters)

@app.route('/painter/<painter_id>', methods=['GET'])
def get_painter(painter_id):
    painter = painters_collection.find_one({"_id": painter_id})
    if painter:
        painter['_id'] = str(painter['_id'])  # Convert _id to string
        return jsonify(painter)
    return jsonify({"error": "Painter not found"}), 404

@app.route('/recognize', methods=['POST'])
def recognize_painting():
    if 'file' not in request.files:
        print("No file found in request")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        print("Empty file selected")
        return jsonify({"error": "No file selected"}), 400

    try:
        # Save the uploaded file temporarily
        file_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(file_path)
        print(f"File saved at {file_path}")

        # Preprocess the image and make predictions
        img_array = preprocess_image(file_path)
        predictions = model.predict(img_array)
        print(f"Predictions Array: {predictions}")

        predicted_class = int(np.argmax(predictions, axis=1)[0])
        print(f"Predicted Class: {predicted_class}")

        # Map predicted class to painting ID
        painting_id = CLASS_TO_ID_MAP.get(predicted_class)
        print(f"Painting ID: {painting_id}")

        if not painting_id:
            print("Painting not recognized")
            return jsonify({"error": "Painting not recognized"}), 404

        # Map painting ID to painter ID
        painter_id = PAINTING_TO_PAINTER_MAP.get(painting_id)
        print(f"Painter ID: {painter_id}")

        if not painter_id:
            print("Painter not found")
            return jsonify({"error": "Painter not found"}), 404

        return jsonify({
            "painterId": painter_id,
            "paintingId": painting_id
        })

    except Exception as e:
        print(f"Error during recognition: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
