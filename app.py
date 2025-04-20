from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
from PIL import Image
import numpy as np
import io
import os

app = Flask(__name__)
CORS(app)

# Secret Key
SECRET_KEY = "b2a83fdc5d934e198ac94ee3e46d45d0"

# Load YOLOv8 model
model = YOLO("best.pt")
class_names = model.names  

CLASS_TO_CATEGORY_ID = {
    0: 6,  
    1: 4,  
    2: 5,  
    3: 2,  
    4: 6,  
    5: 7,  
    6: 1,  
    7: 1,  
}


@app.route('/')
def index():
    return "🚀 YOLOv8 API with secret key authentication is running!"

@app.route('/predict', methods=['POST'])
def predict():
    # Verify Secret Key
    client_key = request.form.get('secret_key')
    if client_key != SECRET_KEY:
        return jsonify({"error": "Unauthorized. Invalid secret key."}), 403

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    img = Image.open(io.BytesIO(file.read())).convert("RGB")
    img = np.array(img)

    # Run prediction
    results = model(img)

    best_detection = None
    best_confidence = 0.0

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            if confidence > best_confidence:
                best_confidence = confidence
                best_detection = class_id

    if best_detection is not None:
        class_name = class_names.get(best_detection, "unknown")
        category_id = CLASS_TO_CATEGORY_ID.get(best_detection)

        return jsonify({
            "class_id": category_id,
            "class_name": class_name,
            "confidence": round(best_confidence, 4)

        })
    else:
        return jsonify({"class_id": None, "message": "No object detected"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
