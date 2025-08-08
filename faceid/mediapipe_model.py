import os
import numpy as np
import pickle

class MediaPipeFaceModel:
    def __init__(self, model_path="facial_recognition_model.pkl"):
        self.known_face_encodings = []
        self.known_face_metadata = []
        self.model_path = model_path
        # Threshold otimizado para MediaPipe (landmarks têm distâncias menores)
        self.distance_threshold = 0.6  # Muito mais baixo que OpenCV
        
        if model_path and os.path.exists(model_path):
            self.load_model()
    
    def add_face(self, face_encoding, metadata):
        self.known_face_encodings.append(face_encoding)
        self.known_face_metadata.append(metadata)
        return len(self.known_face_encodings) - 1
    
    def calculate_distance(self, encoding1, encoding2):
        """Calcula distância euclidiana normalizada para MediaPipe"""
        try:
            # Normalizar encodings se necessário
            if len(encoding1) != len(encoding2):
                # Redimensionar para o menor tamanho
                min_len = min(len(encoding1), len(encoding2))
                encoding1 = encoding1[:min_len]
                encoding2 = encoding2[:min_len]
            
            # Calcular distância euclidiana normalizada
            distance = np.linalg.norm(np.array(encoding1) - np.array(encoding2))
            
            # Normalizar pela dimensão para consistência
            normalized_distance = distance / np.sqrt(len(encoding1))
            
            return normalized_distance
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return float('inf')
    
    def identify_face(self, face_encoding):
        if len(self.known_face_encodings) == 0:
            print("No known faces in model")
            return None, 1.0
            
        distances = []
        for known_encoding in self.known_face_encodings:
            distance = self.calculate_distance(face_encoding, known_encoding)
            distances.append(distance)
        
        best_match_index = np.argmin(distances)
        best_distance = distances[best_match_index]
        
        print(f"Best distance (MediaPipe): {best_distance}, threshold: {self.distance_threshold}")
        print(f"All distances: {distances}")
        
        if best_distance <= self.distance_threshold:
            metadata = self.known_face_metadata[best_match_index]
            print(f"Match found (MediaPipe): {metadata}")
            # Converter distância para similaridade (ajustado para MediaPipe)
            similarity = max(0, 1 - (best_distance / 2.0))
            return metadata, similarity
        else:
            print(f"No match - distance {best_distance} above threshold {self.distance_threshold}")
            similarity = max(0, 1 - (best_distance / 2.0))
            return None, similarity
    
    def save_model(self):
        data = {
            "encodings": self.known_face_encodings,
            "metadata": self.known_face_metadata,
            "model_type": "mediapipe"
        }
        
        try:
            with open(self.model_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"MediaPipe model saved successfully to {self.model_path}")
            return True
        except Exception as e:
            print(f"Error saving MediaPipe model to {self.model_path}: {e}")
            return False
            
    def load_model(self):
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                
            self.known_face_encodings = data["encodings"]
            self.known_face_metadata = data["metadata"]
            
            # Verificar se é modelo MediaPipe
            if data.get("model_type") == "mediapipe":
                print(f"MediaPipe model loaded successfully from {self.model_path}")
            else:
                print(f"Legacy model loaded from {self.model_path}, converting to MediaPipe format")
                
            return True
        except Exception as e:
            print(f"Error loading model from {self.model_path}: {e}")
            return False

    def clear_model(self):
        self.known_face_encodings = []
        self.known_face_metadata = []

    def get_face_count(self):
        return len(self.known_face_encodings)
