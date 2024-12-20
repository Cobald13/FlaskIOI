from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# MongoDB Atlas connection string
client = MongoClient("mongodb+srv://Cobald13:Mp5K1Ll5@projektioi.o1jsd.mongodb.net/?retryWrites=true&w=majority&appName=projektIOI")
db = client['IOI']  # Replace with your database name
painters_collection = db['Slikarji']  # Replace with your collection name

# Load the pre-trained model
MODEL_PATH = 'painting_recognition_model.h5'
model = tf.keras.models.load_model(MODEL_PATH)

# **CLASS_TO_ID_MAP**
# This mapping links the model's predicted class indices to MongoDB `_id` values for painters
CLASS_TO_ID_MAP = {
    0: "kobilca",   # Class index 0 corresponds to Ivana Kobilca
    1: "kobilca",    # Add corresponding mappings for other painters
    2: "kobilca"    # Example mapping for Rihard Jakopič
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
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Save the uploaded file temporarily
        file_path = os.path.join('temp', file.filename)
        os.makedirs('temp', exist_ok=True)
        file.save(file_path)

        # Preprocess the image and make predictions
        img_array = preprocess_image(file_path)
        predictions = model.predict(img_array)
        predicted_class = int(np.argmax(predictions, axis=1)[0])  # Convert np.int64 to Python int

        # Log predictions for debugging
        print(f"Predictions: {predictions}")
        print(f"Predicted class: {predicted_class}")

        # Map the predicted class to the painter's `_id`
        painter_id = CLASS_TO_ID_MAP.get(predicted_class)
        if not painter_id:
            return jsonify({"error": "Painter not recognized"}), 404

        # Query the database using the `_id`
        painter = painters_collection.find_one({"_id": painter_id})
        if painter:
            painter['_id'] = str(painter['_id'])  # Convert _id to string
            return jsonify(painter)

        return jsonify({"error": "Painter not found in database"}), 404

    except Exception as e:
        print(f"Error during recognition: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)