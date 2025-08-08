import os
import base64
import face_recognition
import numpy as np
from .model import FaceModel

class FaceTrainer:
    def __init__(self, detection_model="hog"):
        self.detection_model = detection_model
    
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
                image = face_recognition.load_image_file(image_path)
                face_locations = face_recognition.face_locations(image, model=self.detection_model)
                
                if len(face_locations) == 0:
                    continue
                
                face_encoding = face_recognition.face_encodings(image, face_locations)[0]
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
            
            image = face_recognition.load_image_file(temp_path)
            face_locations = face_recognition.face_locations(image, model=self.detection_model)
            
            os.remove(temp_path)
            
            if len(face_locations) == 0:
                return False, 0.0
            
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
            metadata, similarity = face_model.identify_face(face_encoding)
            
            if metadata and metadata.get("person_id") == person_id:
                return True, similarity
            
            return False, similarity
            
        except Exception as e:
            return False, 0.0
