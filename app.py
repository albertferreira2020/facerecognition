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
    Muito mai                # Log detalhado para debugging
                print(f"Pessoa {person_id}:")
                print(f"  Max Correlation: {max_correlation:.4f} (>0.50: {max_correlation > 0.50})")
                print(f"  Min Euclidean: {min_euclidean:.4f} (<8.0: {min_euclidean < 8.0})")
                print(f"  Max Cosine: {max_cosine:.4f} (>0.75: {max_cosine > 0.75})")
                print(f"  Max Combined: {max_combined:.4f} (>0.45: {max_combined > 0.45})")
                print(f"  Avg Correlation: {avg_correlation:.4f} (>0.45: {avg_correlation > 0.45})")
                print(f"  Avg Combined: {avg_combined:.4f} (>0.40: {avg_combined > 0.40})")
                print(f"  Condições básicas passadas: {conditions_passed}/6")
                print(f"  Indicadores fortes passados: {strong_indicators_passed}/4")
                print(f"  High similarity metrics: {high_similarity_passed}/4")
                print(f"  Imagens de referência: {len(person_encodings)}")
                print(f"  Match FINAL: {is_match}")e comparação de pixels simples
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
    Carrega uma imagem e extrai características faciais usando múltiplas técnicas
    Versão melhorada para maior robustez
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Pré-processamento melhorado
        # 1. Melhorar contraste usando CLAHE
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        
        # Detectar faces com múltiplas tentativas
        faces = []
        detection_params = [
            (1.05, 3, (30, 30)),
            (1.1, 4, (40, 40)),
            (1.15, 5, (50, 50)),
            (1.2, 3, (60, 60)),
        ]
        
        for scale_factor, min_neighbors, min_size in detection_params:
            # Detector frontal
            detected = face_cascade.detectMultiScale(
                gray, scale_factor, min_neighbors, minSize=min_size
            )
            if len(detected) > 0:
                faces.extend(detected)
                break  # Usar a primeira detecção bem-sucedida
            
            # Detector de perfil se frontal falhou
            detected = face_cascade_profile.detectMultiScale(
                gray, scale_factor, min_neighbors, minSize=min_size
            )
            if len(detected) > 0:
                faces.extend(detected)
                break
        
        # Se ainda não detectou faces, tentar com imagem original
        if len(faces) == 0:
            gray_original = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_original, 1.1, 4, minSize=(50, 50))
            if len(faces) > 0:
                gray = gray_original
        
        if len(faces) == 0:
            print(f"Nenhuma face detectada em {image_path}")
            return None
        
        # Pegar a maior face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Extrair região da face com margem adaptativa maior
        margin = int(min(w, h) * 0.25)  # Margem de 25% (era 20%)
        x1 = max(0, x - margin)
        y1 = max(0, y - margin)
        x2 = min(gray.shape[1], x + w + margin)
        y2 = min(gray.shape[0], y + h + margin)
        
        face_roi = gray[y1:y2, x1:x2]
        
        # Redimensionar para tamanho padrão maior para preservar mais detalhes
        face_roi = cv2.resize(face_roi, (160, 160))  # Era 128x128
        
        # Normalização de iluminação melhorada
        # Aplicar CLAHE específico para a face
        clahe_face = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
        face_roi = clahe_face.apply(face_roi)
        
        # Suavização leve para reduzir ruído
        face_roi = cv2.GaussianBlur(face_roi, (3, 3), 0)
        
        # Extrair características LBP com parâmetros otimizados
        try:
            # Usar múltiplos raios para capturar diferentes escalas de textura
            lbp_features_r1 = extract_lbp_features(face_roi, radius=1, n_points=8)
            lbp_features_r2 = extract_lbp_features(face_roi, radius=2, n_points=16)
            lbp_features_r3 = extract_lbp_features(face_roi, radius=3, n_points=24)
            
            # Combinar features de diferentes escalas
            combined_features = np.concatenate([lbp_features_r1, lbp_features_r2, lbp_features_r3])
            return combined_features
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
    Versão melhorada com múltiplas técnicas
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
        
        # Múltiplas técnicas de melhoria de imagem
        
        # 1. Melhorar contraste e brilho com CLAHE mais suave
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))  # Menos agressivo
        l = clahe.apply(l)
        image = cv2.merge([l, a, b])
        image = cv2.cvtColor(image, cv2.COLOR_LAB2BGR)
        
        # 2. Redução de ruído bilateral (preserva bordas)
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        # 3. Sharpening muito sutil
        kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])  # Menos agressivo
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # 4. Correção de gamma para melhorar contraste
        gamma = 1.2  # Leve ajuste
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        gamma_corrected = cv2.LUT(sharpened, table)
        
        # Salvar imagem processada temporariamente
        temp_path = f"temp_processed_{uuid.uuid4().hex}.jpg"
        cv2.imwrite(temp_path, gamma_corrected, [cv2.IMWRITE_JPEG_QUALITY, 95])
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

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'face-recognition-api',
        'timestamp': uuid.uuid4().hex[:8]
    })

@app.route('/register', methods=['POST'])
def register_person():
    """
    Cadastra uma nova pessoa com múltiplas imagens de referência
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON inválido'}), 400
        
        if 'person_id' not in data:
            return jsonify({'error': 'person_id é obrigatório'}), 400
        
        if 'image_base64' not in data:
            return jsonify({'error': 'image_base64 é obrigatório'}), 400
        
        person_id = data['person_id']
        images_base64 = data['image_base64']
        
        # Validar se é uma lista
        if not isinstance(images_base64, list):
            return jsonify({'error': 'image_base64 deve ser um array'}), 400
        
        if len(images_base64) == 0:
            return jsonify({'error': 'Pelo menos uma imagem é necessária'}), 400
        
        if len(images_base64) > 10:
            return jsonify({'error': 'Máximo de 10 imagens por pessoa'}), 400
        
        # Validar person_id
        if not person_id or not person_id.strip():
            return jsonify({'error': 'person_id não pode estar vazio'}), 400
        
        # Criar pasta da pessoa
        person_folder = os.path.join('people', person_id)
        os.makedirs(person_folder, exist_ok=True)
        
        saved_images = []
        failed_images = []
        
        for i, image_base64 in enumerate(images_base64):
            try:
                # Decodificar imagem base64
                temp_path, _ = decode_base64_image(image_base64)
                
                if not temp_path:
                    failed_images.append({
                        'index': i,
                        'error': 'Erro ao decodificar imagem base64'
                    })
                    continue
                
                try:
                    # Verificar se a imagem tem uma face válida
                    processed_temp_path = preprocess_image_for_better_detection(temp_path)
                    
                    try:
                        encoding = load_and_encode(processed_temp_path)
                        
                        if encoding is None:
                            failed_images.append({
                                'index': i,
                                'error': 'Nenhuma face detectada na imagem'
                            })
                        else:
                            # Salvar imagem na pasta da pessoa
                            image_filename = f"reference_{i+1}_{uuid.uuid4().hex[:8]}.jpg"
                            image_path = os.path.join(person_folder, image_filename)
                            
                            # Decodificar e salvar imagem original
                            image_base64_clean = image_base64
                            if ',' in image_base64_clean:
                                image_base64_clean = image_base64_clean.split(',')[1]
                            
                            image_data = base64.b64decode(image_base64_clean)
                            with open(image_path, 'wb') as f:
                                f.write(image_data)
                            
                            saved_images.append({
                                'index': i,
                                'filename': image_filename,
                                'path': image_path
                            })
                            
                    finally:
                        # Limpar arquivo temporário processado
                        if processed_temp_path != temp_path and os.path.exists(processed_temp_path):
                            os.remove(processed_temp_path)
                
                finally:
                    # Limpar arquivo temporário original
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
            except Exception as e:
                failed_images.append({
                    'index': i,
                    'error': f'Erro ao processar imagem: {str(e)}'
                })
        
        # Verificar se pelo menos uma imagem foi salva com sucesso
        if len(saved_images) == 0:
            # Se nenhuma imagem foi salva, remover pasta criada
            try:
                if os.path.exists(person_folder) and not os.listdir(person_folder):
                    os.rmdir(person_folder)
            except:
                pass
            
            return jsonify({
                'success': False,
                'error': 'Nenhuma imagem válida foi processada',
                'failed_images': failed_images
            }), 400
        
        # Retornar resultado
        return jsonify({
            'success': True,
            'person_id': person_id,
            'total_images_received': len(images_base64),
            'images_saved': len(saved_images),
            'images_failed': len(failed_images),
            'saved_images': saved_images,
            'failed_images': failed_images if failed_images else None,
            'message': f'Pessoa {person_id} cadastrada com sucesso com {len(saved_images)} imagem(ns) de referência'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erro interno do servidor: {str(e)}'
        }), 500

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
                cosine_sims = [s['cosine'] for s in similarities]
                
                max_combined = float(max(combined_scores))
                avg_combined = float(np.mean(combined_scores))
                max_correlation = float(max(correlations))
                avg_correlation = float(np.mean(correlations))
                min_euclidean = float(min(euclidean_distances))
                max_cosine = float(max(cosine_sims))
                
                # CRITÉRIOS ADAPTATIVOS MELHORADOS - Baseados em dados reais
                # Thresholds ajustados com base na análise das imagens da mesma pessoa
                conditions = [
                    max_correlation > 0.50,        # Correlação moderada (era 0.75)
                    min_euclidean < 8.0,           # Distância euclidiana mais permissiva (era 4.0)
                    max_cosine > 0.75,             # Similaridade cosseno moderada (era 0.80)
                    max_combined > 0.45,           # Score combinado mais baixo (era 0.60)
                    avg_correlation > 0.45,        # Média de correlação mais flexível (era 0.65)
                    avg_combined > 0.40            # Média do score combinado mais baixa (era 0.55)
                ]
                
                conditions_passed = sum(conditions)
                
                # Sistema de decisão inteligente baseado em múltiplos fatores
                strong_indicators = [
                    max_correlation > 0.70,        # Correlação forte (era 0.80)
                    max_cosine > 0.80,             # Cosseno alto (era 0.85)
                    min_euclidean < 5.0,           # Distância euclidiana boa (era 3.0)
                    max_combined > 0.55            # Score combinado bom (era 0.65)
                ]
                
                strong_indicators_passed = sum(strong_indicators)
                
                # Critérios mais inteligentes e adaptativos:
                # 1. Se passou em pelo menos 3 condições básicas (era 4)
                # 2. OU se passou em pelo menos 2 indicadores fortes + 2 condições básicas (era 3)
                # 3. OU se correlação e cosseno são altos (thresholds mais baixos)
                # 4. OU se tem alta similaridade em pelo menos 2 métricas principais
                
                # Critério adicional: alta similaridade em múltiplas métricas
                high_similarity_metrics = [
                    max_correlation > 0.60,
                    max_cosine > 0.78,
                    min_euclidean < 6.0,
                    max_combined > 0.50
                ]
                high_similarity_passed = sum(high_similarity_metrics)
                
                is_match = (
                    conditions_passed >= 3 or  # 3 das 6 condições básicas (mais flexível)
                    (strong_indicators_passed >= 2 and conditions_passed >= 2) or  # 2 fortes + 2 básicas
                    (max_correlation > 0.65 and max_cosine > 0.78) or  # Correlação e cosseno bons
                    high_similarity_passed >= 3  # Alta similaridade em pelo menos 3 métricas
                )
                
                # Ajuste para poucas imagens de referência (ser mais leniente)
                if len(person_encodings) <= 2:
                    # Com apenas 1-2 referências, aceitar critérios ainda mais flexíveis
                    is_match = is_match or (
                        strong_indicators_passed >= 1 and conditions_passed >= 2
                    ) or (
                        high_similarity_passed >= 2  # Apenas 2 métricas altas
                    )
                
                # Log detalhado para debugging
                print(f"Pessoa {person_id}:")
                print(f"  Max Correlation: {max_correlation:.4f} (>0.75: {max_correlation > 0.75})")
                print(f"  Min Euclidean: {min_euclidean:.4f} (<4.0: {min_euclidean < 4.0})")
                print(f"  Max Cosine: {max_cosine:.4f} (>0.80: {max_cosine > 0.80})")
                print(f"  Max Combined: {max_combined:.4f} (>0.60: {max_combined > 0.60})")
                print(f"  Avg Correlation: {avg_correlation:.4f} (>0.65: {avg_correlation > 0.65})")
                print(f"  Avg Combined: {avg_combined:.4f} (>0.55: {avg_combined > 0.55})")
                print(f"  Condições básicas passadas: {conditions_passed}/6")
                print(f"  Indicadores fortes passados: {strong_indicators_passed}/4")
                print(f"  Imagens de referência: {len(person_encodings)}")
                print(f"  Match FINAL: {is_match}")
                
                if is_match:
                    person_folder = os.path.join('people', person_id)
                    saved_filename = f"match_{uuid.uuid4().hex}.jpg"
                    saved_path = os.path.join(person_folder, saved_filename)
                    
                    image_data = base64.b64decode(base64_data)
                    with open(saved_path, 'wb') as f:
                        f.write(image_data)
                
                return jsonify({
                    'match': bool(is_match),
                    'max_correlation': float(round(max_correlation, 4)),
                    'min_euclidean_distance': float(round(min_euclidean, 4)),
                    'max_cosine_similarity': float(round(max_cosine, 4)),
                    'max_combined_score': float(round(max_combined, 4)),
                    'avg_correlation': float(round(avg_correlation, 4)),
                    'avg_combined_score': float(round(avg_combined, 4)),
                    'basic_conditions_passed': conditions_passed,
                    'strong_indicators_passed': strong_indicators_passed,
                    'high_similarity_passed': high_similarity_passed,
                    'total_basic_conditions': 6,
                    'total_strong_indicators': 4,
                    'total_high_similarity_metrics': 4,
                    'num_comparisons': len(similarities),
                    'num_reference_images': len(person_encodings),
                    'confidence_level': 'very_high' if strong_indicators_passed >= 3 else 'high' if strong_indicators_passed >= 2 or high_similarity_passed >= 3 else 'medium' if conditions_passed >= 3 else 'low',
                    'decision_factors': {
                        'basic_threshold_met': conditions_passed >= 3,
                        'strong_indicators_met': strong_indicators_passed >= 2 and conditions_passed >= 2,
                        'excellent_correlation_cosine': max_correlation > 0.65 and max_cosine > 0.78,
                        'high_similarity_met': high_similarity_passed >= 3,
                        'few_references_bonus': len(person_encodings) <= 2 and (strong_indicators_passed >= 1 or high_similarity_passed >= 2)
                    },
                    'thresholds_info': {
                        'basic_correlation_threshold': 0.50,
                        'basic_euclidean_threshold': 8.0,
                        'basic_cosine_threshold': 0.75,
                        'basic_combined_threshold': 0.45,
                        'strong_correlation_threshold': 0.70,
                        'strong_euclidean_threshold': 5.0,
                        'strong_cosine_threshold': 0.80,
                        'strong_combined_threshold': 0.55,
                        'high_similarity_correlation_threshold': 0.60,
                        'high_similarity_euclidean_threshold': 6.0,
                        'high_similarity_cosine_threshold': 0.78,
                        'high_similarity_combined_threshold': 0.50
                    }
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
    app.run(host='0.0.0.0', port=3000)
