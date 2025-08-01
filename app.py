from flask import Flask, request, jsonify
import os
import numpy as np
import cv2
import base64
import uuid

app = Flask(__name__)

os.makedirs('people', exist_ok=True)

# Usar detectores mais modernos do OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_cascade_profile = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

def extract_lbp_features(image, radius=3, n_points=24):
    """
    Extrai características LBP (Local Binary Patterns) da imagem
    Muito mais robusto que comparação de pixels simples
    """
    from skimage import feature
    from skimage.color import rgb2gray
    
    if len(image.shape) == 3:
        gray = rgb2gray(image)
    else:
        gray = image
    
    # Calcular LBP
    lbp = feature.local_binary_pattern(gray, n_points, radius, method='uniform')
    
    # Criar histograma
    hist, _ = np.histogram(lbp.ravel(), bins=n_points + 2, range=(0, n_points + 2))
    
    # Normalizar
    hist = hist.astype(np.float32)
    hist /= (hist.sum() + 1e-6)
    
    return hist

def load_and_encode(image_path):
    """
    Carrega uma imagem e extrai características faciais usando LBP
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detectar faces (tentar múltiplos detectores)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))
        
        if len(faces) == 0:
            # Tentar detector de perfil
            faces = face_cascade_profile.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))
        
        if len(faces) == 0:
            print(f"Nenhuma face detectada em {image_path}")
            return None
        
        # Pegar a maior face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Extrair região da face com margem
        margin = int(min(w, h) * 0.2)
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(gray.shape[1], x + w + margin)
        y2 = min(gray.shape[0], y + h + margin)
        
        face_roi = gray[y1:y2, x1:x2]
        
        # Redimensionar para tamanho padrão
        face_roi = cv2.resize(face_roi, (128, 128))
        
        # Normalizar iluminação
        face_roi = cv2.equalizeHist(face_roi)
        
        # Extrair características LBP
        try:
            lbp_features = extract_lbp_features(face_roi)
            return lbp_features
        except ImportError:
            # Fallback para HOG se scikit-image não estiver disponível
            return extract_hog_features(face_roi)
    
    except Exception as e:
        print(f"Erro ao processar imagem {image_path}: {e}")
        return None

def extract_hog_features(image):
    """
    Extrai características HOG (Histogram of Oriented Gradients)
    Fallback caso scikit-image não esteja disponível
    """
    # Redimensionar para tamanho fixo
    image = cv2.resize(image, (64, 128))
    
    # Parâmetros HOG
    win_size = (64, 128)
    block_size = (16, 16)
    block_stride = (8, 8)
    cell_size = (8, 8)
    nbins = 9
    
    hog = cv2.HOGDescriptor(win_size, block_size, block_stride, cell_size, nbins)
    features = hog.compute(image)
    
    if features is not None:
        return features.flatten().astype(np.float32)
    else:
        # Fallback final: características básicas melhoradas
        return extract_basic_features(image)

def extract_basic_features(image):
    """
    Extrai características básicas melhoradas da face
    """
    # Dividir imagem em regiões
    h, w = image.shape
    regions = [
        image[0:h//3, 0:w//3],      # Testa esquerda
        image[0:h//3, w//3:2*w//3], # Testa centro
        image[0:h//3, 2*w//3:w],    # Testa direita
        image[h//3:2*h//3, 0:w//3], # Olho esquerdo
        image[h//3:2*h//3, w//3:2*w//3], # Nariz
        image[h//3:2*h//3, 2*w//3:w],    # Olho direito
        image[2*h//3:h, 0:w//3],    # Boca esquerda
        image[2*h//3:h, w//3:2*w//3],    # Boca centro
        image[2*h//3:h, 2*w//3:w],       # Boca direita
    ]
    
    features = []
    for region in regions:
        if region.size > 0:
            # Estatísticas básicas
            features.extend([
                np.mean(region),
                np.std(region),
                np.min(region),
                np.max(region)
            ])
    
    return np.array(features, dtype=np.float32)

def preprocess_image_for_better_detection(image_path):
    """
    Pré-processa a imagem para melhorar a detecção de faces
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return image_path
        
        # Redimensionar se muito grande (para acelerar processamento)
        height, width = image.shape[:2]
        if width > 1200 or height > 1200:
            scale = min(1200/width, 1200/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height))
        
        # Melhorar contraste e brilho
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        image = cv2.merge([l, a, b])
        image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
        
        # Salvar imagem processada temporariamente
        temp_path = f"temp_processed_{uuid.uuid4().hex}.jpg"
        cv2.imwrite(temp_path, image)
        return temp_path
        
    except Exception as e:
        print(f"Erro no pré-processamento: {e}")
        return image_path

def get_person_encodings(person_id):
    """
    Carrega todos os encodings de uma pessoa específica
    """
    person_folder = os.path.join('people', person_id)
    if not os.path.exists(person_folder):
        return None
    
    encodings = []
    processed_files = []
    
    for filename in os.listdir(person_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join(person_folder, filename)
            
            # Pré-processar imagem
            processed_path = preprocess_image_for_better_detection(image_path)
            
            try:
                encoding = load_and_encode(processed_path)
                if encoding is not None:
                    encodings.append(encoding)
                    processed_files.append(filename)
                else:
                    print(f"Não foi possível extrair encoding de {filename}")
            finally:
                # Limpar arquivo temporário se foi criado
                if processed_path != image_path and os.path.exists(processed_path):
                    os.remove(processed_path)
    
    if encodings:
        print(f"Carregados {len(encodings)} encodings para pessoa {person_id}")
        return encodings
    else:
        print(f"Nenhum encoding válido encontrado para pessoa {person_id}")
        return None

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
            
            # Pré-processar a imagem de teste
            processed_temp_path = preprocess_image_for_better_detection(temp_path)
            
            try:
                target_encoding = load_and_encode(processed_temp_path)
                if target_encoding is None:
                    return jsonify({'match': False, 'error': 'Rosto não detectado na imagem'}), 400
                
                # Calcular similaridades usando diferentes métricas
                similarities = []
                
                for encoding in person_encodings:
                    try:
                        # Distância euclidiana
                        euclidean_dist = np.linalg.norm(target_encoding - encoding)
                        
                        # Correlação de Pearson
                        correlation = np.corrcoef(target_encoding, encoding)[0, 1]
                        if np.isnan(correlation):
                            correlation = 0
                        
                        # Distância de Manhattan
                        manhattan_dist = np.sum(np.abs(target_encoding - encoding))
                        
                        # Similaridade do cosseno manual
                        dot_product = np.dot(target_encoding, encoding)
                        norm1 = np.linalg.norm(target_encoding)
                        norm2 = np.linalg.norm(encoding)
                        cosine_sim = dot_product / (norm1 * norm2 + 1e-6)
                        
                        # Combinar métricas (quanto menor euclidiana e manhattan, melhor)
                        combined_score = (
                            0.3 * (1.0 / (1.0 + euclidean_dist)) +
                            0.3 * abs(correlation) +
                            0.2 * (1.0 / (1.0 + manhattan_dist / 1000)) +
                            0.2 * max(0, cosine_sim)
                        )
                        
                        similarities.append({
                            'euclidean': float(euclidean_dist),
                            'correlation': float(correlation),
                            'manhattan': float(manhattan_dist),
                            'cosine': float(cosine_sim),
                            'combined': float(combined_score)
                        })
                        
                    except Exception as e:
                        print(f"Erro ao comparar encodings: {e}")
                        continue
                
                if not similarities:
                    return jsonify({'match': False, 'error': 'Erro no cálculo de similaridade'}), 400
                
                # Extrair métricas
                combined_scores = [s['combined'] for s in similarities]
                correlations = [s['correlation'] for s in similarities]
                euclidean_distances = [s['euclidean'] for s in similarities]
                
                max_combined = float(max(combined_scores))
                avg_combined = float(np.mean(combined_scores))
                max_correlation = float(max(correlations))
                min_euclidean = float(min(euclidean_distances))
                
                # Critérios de matching mais flexíveis
                # Usar score combinado > 0.4 OU correlação > 0.6
                is_match = bool(max_combined > 0.4 or max_correlation > 0.6)
                
                # Log para debugging
                print(f"Pessoa {person_id}:")
                print(f"  Max Combined Score: {max_combined:.4f}")
                print(f"  Avg Combined Score: {avg_combined:.4f}")
                print(f"  Max Correlation: {max_correlation:.4f}")
                print(f"  Min Euclidean: {min_euclidean:.4f}")
                print(f"  Match: {is_match}")
                
                if is_match:
                    person_folder = os.path.join('people', person_id)
                    saved_filename = f"match_{uuid.uuid4().hex}.jpg"
                    saved_path = os.path.join(person_folder, saved_filename)
                    
                    image_data = base64.b64decode(base64_data)
                    with open(saved_path, 'wb') as f:
                        f.write(image_data)
                
                return jsonify({
                    'match': bool(is_match),
                    'max_combined_score': float(round(max_combined, 4)),
                    'avg_combined_score': float(round(avg_combined, 4)),
                    'max_correlation': float(round(max_correlation, 4)),
                    'min_euclidean_distance': float(round(min_euclidean, 4)),
                    'num_comparisons': len(similarities),
                    'confidence': float(round(max(max_combined, max_correlation), 4))
                })
                
            finally:  
                # Limpar arquivo temporário processado
                if processed_temp_path != temp_path and os.path.exists(processed_temp_path):
                    os.remove(processed_temp_path)
            
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({'match': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
