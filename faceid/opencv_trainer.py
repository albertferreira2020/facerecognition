import cv2
import numpy as np
import os
import base64
from .model import FaceModel

class OpenCVFaceTrainer:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    def extract_face_encoding(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None
            
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face_roi, (100, 100))
        
        return face_resized.flatten()
    
    def train_person(self, person_id, dataset_path="dataset"):
        person_path = os.path.join(dataset_path, person_id)
        
        if not os.path.exists(person_path):
            return False
            
        face_model = FaceModel(f"{person_id}_model.pkl")
        face_model.clear_model()
        
        for image_file in os.listdir(person_path):
            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            image_path = os.path.join(person_path, image_file)
            
            try:
                image = cv2.imread(image_path)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                face_encoding = self.extract_face_encoding(image_rgb)
                
                if face_encoding is not None:
                    metadata = {"person_id": person_id}
                    face_model.add_face(face_encoding, metadata)
                
            except Exception as e:
                continue
        
        return face_model.save_model()
    
    def save_base64_images(self, person_id, images_base64, dataset_path="dataset"):
        person_path = os.path.join(dataset_path, person_id)
        os.makedirs(person_path, exist_ok=True)
        
        existing_count = len([f for f in os.listdir(person_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]) if os.path.exists(person_path) else 0
        saved_images = []
        
        for i, img_base64 in enumerate(images_base64):
            try:
                image_data = base64.b64decode(img_base64)
                image_filename = f"{person_id}_{existing_count + i + 1}.jpg"
                image_path = os.path.join(person_path, image_filename)
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                saved_images.append(image_path)
                
            except Exception as e:
                continue
        
        return saved_images
    
    def verify_face(self, person_id, image_base64):
        try:
            face_model = FaceModel(f"{person_id}_model.pkl")
            
            if face_model.get_face_count() == 0:
                return False, 0.0
            
            image_data = base64.b64decode(image_base64)
            temp_path = f"temp_{person_id}.jpg"
            
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            image = cv2.imread(temp_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            os.remove(temp_path)
            
            face_encoding = self.extract_face_encoding(image_rgb)
            
            if face_encoding is None:
                return False, 0.0
            
            metadata, similarity = face_model.identify_face(face_encoding)
            
            if metadata and metadata.get("person_id") == person_id:
                return True, similarity
            
            return False, similarity
            
        except Exception as e:
            return False, 0.0
