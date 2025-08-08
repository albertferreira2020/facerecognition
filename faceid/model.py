import os
import numpy as np
import pickle
from sklearn.metrics.pairwise import cosine_similarity

class FaceModel:
    def __init__(self, model_path="facial_recognition_model.pkl"):
        self.known_face_encodings = []
        self.known_face_metadata = []
        self.model_path = model_path
        self.similarity_threshold = 0.6
        
        if model_path and os.path.exists(model_path):
            self.load_model()
    
    def add_face(self, face_encoding, metadata):
        self.known_face_encodings.append(face_encoding)
        self.known_face_metadata.append(metadata)
        return len(self.known_face_encodings) - 1
    
    def identify_face(self, face_encoding):
        if len(self.known_face_encodings) == 0:
            return None, 0.0
            
        face_encoding_np = np.array([face_encoding])
        encodings_np = np.array(self.known_face_encodings)
        
        similarities = cosine_similarity(face_encoding_np, encodings_np)[0]
        
        best_match_index = np.argmax(similarities)
        best_match_score = similarities[best_match_index]
        
        if best_match_score >= self.similarity_threshold:
            return self.known_face_metadata[best_match_index], best_match_score
        else:
            return None, best_match_score
    
    def save_model(self):
        data = {
            "encodings": self.known_face_encodings,
            "metadata": self.known_face_metadata
        }
        
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            return False
            
    def load_model(self):
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                
            self.known_face_encodings = data["encodings"]
            self.known_face_metadata = data["metadata"]
            return True
        except Exception as e:
            return False

    def clear_model(self):
        self.known_face_encodings = []
        self.known_face_metadata = []

    def get_face_count(self):
        return len(self.known_face_encodings)
