import cv2
import numpy as np
import os
import base64
from PIL import Image
import io
import mediapipe as mp
from .mediapipe_model import MediaPipeFaceModel

class MediaPipeFaceTrainer:
    def __init__(self):
        # Inicializar MediaPipe
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Configurar detecção de rostos (otimizada para qualidade)
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 1 para melhor qualidade (0 para velocidade)
            min_detection_confidence=0.7
        )
        
        # Configurar face mesh para landmarks faciais
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
    
    def crop_face_from_base64(self, image_base64, padding=50):
        """Extrai e cropa o rosto de uma imagem base64 usando MediaPipe"""
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            image_rgb = np.array(image.convert('RGB'))
            
            # Processar com MediaPipe
            results = self.face_detection.process(image_rgb)
            
            if not results.detections:
                return None
            
            # Usar a primeira detecção
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            
            height, width = image_rgb.shape[:2]
            
            # Converter coordenadas relativas para absolutas
            x = int(bbox.xmin * width)
            y = int(bbox.ymin * height)
            w = int(bbox.width * width)
            h = int(bbox.height * height)
            
            # Calcular centro do rosto
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # Usar a maior dimensão para criar um quadrado
            face_size = max(w, h)
            
            # Adicionar padding
            square_size = face_size + (2 * padding)
            half_square = square_size // 2
            
            # Calcular coordenadas do quadrado centrado no rosto
            x1 = max(0, face_center_x - half_square)
            y1 = max(0, face_center_y - half_square)
            x2 = min(width, face_center_x + half_square)
            y2 = min(height, face_center_y + half_square)
            
            # Ajustar para garantir que seja quadrado
            actual_width = x2 - x1
            actual_height = y2 - y1
            
            if actual_width != actual_height:
                # Usar a menor dimensão para manter dentro da imagem
                min_size = min(actual_width, actual_height)
                
                # Recentrar
                half_min = min_size // 2
                x1 = face_center_x - half_min
                y1 = face_center_y - half_min
                x2 = face_center_x + half_min
                y2 = face_center_y + half_min
                
                # Garantir que está dentro dos limites
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(width, x2)
                y2 = min(height, y2)
            
            # Cropar o rosto
            cropped_face = image_rgb[y1:y2, x1:x2]
            
            # Converter de volta para PIL Image
            cropped_pil = Image.fromarray(cropped_face)
            
            # Redimensionar para tamanho padrão (quadrado)
            standard_size = 180
            cropped_pil = cropped_pil.resize((standard_size, standard_size), Image.Resampling.LANCZOS)
            
            # Converter para base64
            buffer = io.BytesIO()
            cropped_pil.save(buffer, format='JPEG', quality=95)
            cropped_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            print(f"Face cropped (MediaPipe): original face {w}x{h} -> square {standard_size}x{standard_size}")
            
            return cropped_base64
            
        except Exception as e:
            print(f"Error cropping face with MediaPipe: {e}")
            return None
    
    def extract_face_landmarks(self, image):
        """Extrai landmarks faciais usando MediaPipe Face Mesh"""
        try:
            results = self.face_mesh.process(image)
            
            if not results.multi_face_landmarks:
                return None
            
            # Usar os landmarks do primeiro rosto detectado
            face_landmarks = results.multi_face_landmarks[0]
            
            # Extrair coordenadas dos landmarks importantes
            height, width = image.shape[:2]
            landmarks = []
            
            # Selecionar landmarks chave para reconhecimento facial
            # Estes são pontos importantes do rosto para identificação
            key_landmarks = [
                # Contorno do rosto
                10, 151, 9, 175, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
                # Olhos
                33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246,
                # Nariz
                1, 2, 5, 4, 6, 168, 8, 9, 10, 151, 195, 197, 196, 3, 51, 48, 115, 131, 134, 102,
                # Boca
                11, 12, 13, 14, 15, 16, 17, 18, 200, 199, 175, 0, 269, 270, 267, 271, 272, 408, 415, 310, 311, 312, 13, 82, 81, 80, 78
            ]
            
            for idx in key_landmarks:
                if idx < len(face_landmarks.landmark):
                    landmark = face_landmarks.landmark[idx]
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    landmarks.extend([x, y])
            
            # Se não conseguimos landmarks suficientes, usar coordenadas normalizadas
            if len(landmarks) < 100:
                landmarks = []
                for landmark in face_landmarks.landmark:
                    landmarks.extend([landmark.x, landmark.y, landmark.z])
            
            return np.array(landmarks, dtype=np.float32)
            
        except Exception as e:
            print(f"Error extracting face landmarks: {e}")
            return None
    
    def extract_face_encoding(self, image):
        """Extrai encoding facial usando MediaPipe"""
        try:
            # Primeiro tentar com landmarks do Face Mesh
            landmarks = self.extract_face_landmarks(image)
            
            if landmarks is not None:
                # Normalizar os landmarks
                landmarks = landmarks / np.linalg.norm(landmarks)
                return landmarks
            
            # Fallback: usar detecção simples + HOG-like features
            results = self.face_detection.process(image)
            
            if not results.detections:
                return None
            
            detection = results.detections[0]
            bbox = detection.location_data.relative_bounding_box
            
            height, width = image.shape[:2]
            
            x = int(bbox.xmin * width)
            y = int(bbox.ymin * height)
            w = int(bbox.width * width)
            h = int(bbox.height * height)
            
            # Extrair ROI do rosto
            face_roi = image[y:y+h, x:x+w]
            
            if face_roi.size == 0:
                return None
            
            # Converter para grayscale e redimensionar
            gray = cv2.cvtColor(face_roi, cv2.COLOR_RGB2GRAY)
            face_resized = cv2.resize(gray, (64, 64))
            
            # Calcular HOG features para melhor representação
            # Dividir a face em células e calcular gradientes
            features = []
            cell_size = 8
            for i in range(0, 64, cell_size):
                for j in range(0, 64, cell_size):
                    cell = face_resized[i:i+cell_size, j:j+cell_size]
                    
                    # Calcular gradientes
                    gx = cv2.Sobel(cell.astype(np.float32), cv2.CV_32F, 1, 0, ksize=3)
                    gy = cv2.Sobel(cell.astype(np.float32), cv2.CV_32F, 0, 1, ksize=3)
                    
                    # Magnitude e direção
                    mag = np.sqrt(gx**2 + gy**2)
                    angle = np.arctan2(gy, gx)
                    
                    # Estatísticas da célula
                    features.extend([
                        np.mean(cell),
                        np.std(cell),
                        np.mean(mag),
                        np.std(mag),
                        np.mean(angle),
                        np.std(angle)
                    ])
            
            return np.array(features, dtype=np.float32)
            
        except Exception as e:
            print(f"Error extracting face encoding: {e}")
            return None
    
    def train_person(self, person_id, dataset_path="dataset"):
        person_path = os.path.join(dataset_path, person_id)
        
        if not os.path.exists(person_path):
            print(f"Person folder does not exist: {person_path}")
            return False
            
        face_model = MediaPipeFaceModel(f"{person_id}_model.pkl")
        face_model.clear_model()
        
        print(f"Training person {person_id} from folder: {person_path} (MediaPipe)")
        
        faces_added = 0
        
        for image_file in os.listdir(person_path):
            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
                
            image_path = os.path.join(person_path, image_file)
            
            try:
                image = cv2.imread(image_path)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                face_encoding = self.extract_face_encoding(image_rgb)
                
                if face_encoding is not None:
                    metadata = {"person_id": person_id, "image_file": image_file}
                    face_model.add_face(face_encoding, metadata)
                    faces_added += 1
                    
                    print(f"   Added face from {image_file} for person {person_id} (MediaPipe)")
                else:
                    print(f"   No face detected in {image_file}")
                
            except Exception as e:
                print(f"   Error processing {image_file}: {e}")
                continue
        
        print(f"Total faces added for {person_id}: {faces_added}")
        
        if faces_added > 0:
            success = face_model.save_model()
            print(f"Model saved for {person_id}: {success}")
            return success
        else:
            print(f"No faces to save for {person_id}")
            return False
    
    def save_base64_images(self, person_id, images_base64, dataset_path="dataset"):
        person_path = os.path.join(dataset_path, person_id)
        os.makedirs(person_path, exist_ok=True)
        
        existing_count = len([f for f in os.listdir(person_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]) if os.path.exists(person_path) else 0
        saved_images = []
        
        for i, img_base64 in enumerate(images_base64):
            try:
                # Cropar o rosto antes de salvar
                cropped_base64 = self.crop_face_from_base64(img_base64)
                
                if cropped_base64 is None:
                    print(f"No face detected in image {i+1}, skipping...")
                    continue
                
                # Usar a imagem cropada
                image_data = base64.b64decode(cropped_base64)
                image_filename = f"{person_id}_{existing_count + i + 1}_cropped.jpg"
                image_path = os.path.join(person_path, image_filename)
                
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                saved_images.append(image_path)
                print(f"Saved cropped face (MediaPipe): {image_filename}")
                
            except Exception as e:
                print(f"Error processing image {i+1}: {e}")
                continue
        
        return saved_images
    
    def verify_face(self, person_id, image_base64):
        try:
            model_path = f"{person_id}_model.pkl"
            print(f"Loading model for person {person_id}: {model_path} (MediaPipe)")
            
            if not os.path.exists(model_path):
                print(f"Model file does not exist: {model_path}")
                return False, 0.0
                
            face_model = MediaPipeFaceModel(model_path)
            
            if face_model.get_face_count() == 0:
                print(f"No faces in model for person_id: {person_id}")
                return False, 0.0
            
            print(f"Model loaded with {face_model.get_face_count()} faces")
            print(f"Model threshold: {face_model.distance_threshold}")
            
            # Processar imagem de verificação
            try:
                image_data = base64.b64decode(image_base64)
                temp_path = f"temp_{person_id}_verify.jpg"
                
                with open(temp_path, 'wb') as f:
                    f.write(image_data)
                
                # Carregar imagem
                test_img = cv2.imread(temp_path)
                if test_img is None:
                    print(f"Failed to load temporary image")
                    return False, 0.0
                
                height, width = test_img.shape[:2]
                
                if width <= 200 and height <= 200:
                    print(f"Image appears to be pre-cropped ({width}x{height}), using directly")
                    image_rgb = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)
                else:
                    print(f"Image is large ({width}x{height}), attempting to crop face")
                    # Cropar o rosto da imagem
                    cropped_base64 = self.crop_face_from_base64(image_base64)
                    
                    if cropped_base64 is None:
                        print(f"No face detected in verification image for person_id: {person_id}")
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                        return False, 0.0
                    
                    # Usar a imagem cropada
                    image_data = base64.b64decode(cropped_base64)
                    
                    with open(temp_path, 'wb') as f:
                        f.write(image_data)
                    
                    test_img = cv2.imread(temp_path)
                    image_rgb = cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB)
                
                face_encoding = self.extract_face_encoding(image_rgb)
                
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                if face_encoding is None:
                    print(f"No face detected in processed image for person_id: {person_id}")
                    return False, 0.0
                
            except Exception as e:
                print(f"Error processing image: {e}")
                return False, 0.0
            
            # Verificar contra todos os modelos (mesmo algoritmo do OpenCV)
            all_models = [f for f in os.listdir('.') if f.endswith('_model.pkl')]
            print(f"Found {len(all_models)} models to compare against")
            
            distances_by_person = {}
            
            # Testar contra todos os modelos
            for model_file in all_models:
                test_person_id = model_file.replace('_model.pkl', '')
                test_model = MediaPipeFaceModel(model_file)
                
                if test_model.get_face_count() == 0:
                    continue
                
                # Calcular menor distância para este modelo
                min_distance = float('inf')
                for known_encoding in test_model.known_face_encodings:
                    distance = test_model.calculate_distance(face_encoding, known_encoding)
                    min_distance = min(min_distance, distance)
                
                distances_by_person[test_person_id] = min_distance
                print(f"Distance to {test_person_id}: {min_distance}")
            
            if not distances_by_person:
                print("No models to compare against")
                return False, 0.0
            
            # Encontrar a menor distância geral
            best_person_id = min(distances_by_person, key=distances_by_person.get)
            best_distance = distances_by_person[best_person_id]
            
            print(f"Best match: {best_person_id} with distance {best_distance}")
            print(f"Requested person: {person_id}")
            print(f"Threshold: {face_model.distance_threshold}")
            
            # Mesma lógica de verificação do OpenCV, mas com threshold ajustado para MediaPipe
            # MediaPipe tende a ter distâncias menores, então ajustamos o threshold
            adjusted_threshold = face_model.distance_threshold * 0.8  # Mais rigoroso
            
            if len(distances_by_person) == 1:
                if best_person_id == person_id and best_distance <= adjusted_threshold:
                    print(f"MATCH (single model, MediaPipe): Person {person_id} verified")
                    similarity = max(0, 1 - (best_distance / 20000))  # Ajustado para MediaPipe
                    return True, similarity
                else:
                    print(f"NO MATCH (single model, MediaPipe): distance {best_distance} > threshold {adjusted_threshold}")
                    similarity = max(0, 1 - (best_distance / 20000))
                    return False, similarity
            
            # Para múltiplos modelos
            sorted_distances = sorted(distances_by_person.items(), key=lambda x: x[1])
            
            if len(sorted_distances) >= 2:
                second_best_distance = sorted_distances[1][1]
                margin = (second_best_distance - best_distance) / second_best_distance if second_best_distance > 0 else 0
                
                print(f"Best: {best_distance}, Second best: {second_best_distance}, Margin: {margin:.2%}")
                
                # Critérios ainda mais rigorosos para MediaPipe devido à maior precisão
                if (best_person_id == person_id and 
                    best_distance <= adjusted_threshold and margin >= 0.25):  # 25% de margem
                    
                    print(f"MATCH (MediaPipe): Person {person_id} verified with margin {margin:.2%}")
                    similarity = max(0, 1 - (best_distance / 20000))
                    return True, similarity
                else:
                    print(f"NO MATCH (MediaPipe): Best match was {best_person_id}, margin {margin:.2%}, distance {best_distance}")
                    similarity = max(0, 1 - (best_distance / 20000))
                    return False, similarity
            else:
                # Fallback
                if best_person_id == person_id and best_distance <= adjusted_threshold:
                    print(f"MATCH (fallback, MediaPipe): Person {person_id} verified")
                    similarity = max(0, 1 - (best_distance / 20000))
                    return True, similarity
                else:
                    print(f"NO MATCH (fallback, MediaPipe): distance too high")
                    similarity = max(0, 1 - (best_distance / 20000))
                    return False, similarity
            
        except Exception as e:
            print(f"Error in verify_face for {person_id} (MediaPipe): {e}")
            return False, 0.0
