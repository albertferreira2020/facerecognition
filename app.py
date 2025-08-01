from flask import Flask, request, jsonify
import os
import numpy as np
import cv2
import base64
import uuid

app = Flask(__name__)

os.makedirs('people', exist_ok=True)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def load_and_encode(image_path):
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) == 0:
            return None
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (100, 100))
        face_roi = face_roi.flatten().astype(np.float32)
        face_roi = face_roi / 255.0
        return face_roi
    except:
        return None

def get_person_encodings(person_id):
    person_folder = os.path.join('people', person_id)
    if not os.path.exists(person_folder):
        return None
    encodings = []
    for filename in os.listdir(person_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join(person_folder, filename)
            encoding = load_and_encode(image_path)
            if encoding is not None:
                encodings.append(encoding)
    return encodings if encodings else None

def decode_base64_image(base64_string):
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        image_data = base64.b64decode(base64_string)
        temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
        with open(temp_filename, 'wb') as f:
            f.write(image_data)
        return temp_filename, base64_string
    except:
        return None, None

@app.route('/verify', methods=['POST'])
def verify():
    try:
        data = request.get_json()
        if not data or 'person_id' not in data or 'image_base64' not in data:
            return jsonify({'match': False, 'error': 'person_id e image_base64 obrigatórios'}), 400
        
        person_id = data['person_id']
        temp_path, base64_data = decode_base64_image(data['image_base64'])
        
        if not temp_path:
            return jsonify({'match': False, 'error': 'Erro ao decodificar imagem'}), 400
        
        try:
            person_encodings = get_person_encodings(person_id)
            if person_encodings is None:
                return jsonify({'match': False, 'error': 'Pessoa não encontrada'}), 404
            
            target_encoding = load_and_encode(temp_path)
            if target_encoding is None:
                return jsonify({'match': False, 'error': 'Rosto não detectado'}), 400
            
            similarities = []
            for encoding in person_encodings:
                correlation = np.corrcoef(encoding, target_encoding)[0, 1]
                if not np.isnan(correlation):
                    similarities.append(correlation)
            
            if not similarities:
                return jsonify({'match': False, 'error': 'Erro no cálculo'}), 400
            
            avg_similarity = sum(similarities) / len(similarities)
            is_match = avg_similarity > 0.7
            
            if is_match:
                person_folder = os.path.join('people', person_id)
                saved_filename = f"match_{uuid.uuid4().hex}.jpg"
                saved_path = os.path.join(person_folder, saved_filename)
                
                image_data = base64.b64decode(base64_data)
                with open(saved_path, 'wb') as f:
                    f.write(image_data)
            
            return jsonify({
                'match': is_match,
                'similarity': round(float(avg_similarity), 4)
            })
            
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({'match': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
