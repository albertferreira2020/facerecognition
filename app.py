from flask import Flask, request, jsonify
import os
import numpy as np
import cv2
from werkzeug.utils import secure_filename
import base64
import uuid

app = Flask(__name__)

# Configurações
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
BASE_FOLDER = 'people'  # Pasta onde ficam as pastas das pessoas

# Criar pastas se não existirem
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(BASE_FOLDER, exist_ok=True)

# Inicializar detector de faces do OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_and_encode(image_path):
    """Carrega uma imagem e extrai features do rosto usando OpenCV"""
    try:
        # Carregar imagem
        image = cv2.imread(image_path)
        if image is None:
            return None
            
        # Converter para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detectar faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None
            
        # Pegar a primeira face detectada
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        
        # Redimensionar para tamanho padrão
        face_roi = cv2.resize(face_roi, (100, 100))
        
        # Normalizar
        face_roi = face_roi.flatten().astype(np.float32)
        face_roi = face_roi / 255.0
        
        return face_roi
        
    except Exception as e:
        print(f"Erro ao processar imagem {image_path}: {e}")
        return None

def get_person_encodings(person_id):
    """Carrega todos os encodings de uma pessoa específica"""
    person_folder = os.path.join(BASE_FOLDER, person_id)
    
    if not os.path.exists(person_folder):
        return None
    
    encodings = []
    for filename in os.listdir(person_folder):
        if allowed_file(filename):
            image_path = os.path.join(person_folder, filename)
            encoding = load_and_encode(image_path)
            if encoding is not None:
                encodings.append(encoding)
    
    return encodings if encodings else None

def decode_base64_image(base64_string):
    """Decodifica imagem base64 e salva temporariamente"""
    try:
        # Remove header se existir (data:image/jpeg;base64,)
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decodifica base64
        image_data = base64.b64decode(base64_string)
        
        # Gera nome único
        temp_filename = f"temp_{uuid.uuid4().hex}.jpg"
        temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
        
        # Salva arquivo
        with open(temp_path, 'wb') as f:
            f.write(image_data)
            
        return temp_path
        
    except Exception as e:
        print(f"Erro ao decodificar base64: {e}")
        return None

@app.route('/verify', methods=['POST'])
def verify():
    """
    Endpoint para verificar match facial com pessoa específica
    Aceita:
    1. Form data: person_id + arquivo image
    2. JSON: person_id + image_base64
    """
    try:
        person_id = None
        temp_path = None
        
        # Verificar se é JSON ou form data
        if request.is_json:
            # Requisição JSON com base64
            data = request.get_json()
            
            if not data or 'person_id' not in data:
                return jsonify({
                    'error': 'person_id é obrigatório',
                    'match': False
                }), 400
                
            person_id = data['person_id']
            
            if 'image_base64' not in data:
                return jsonify({
                    'error': 'image_base64 é obrigatório',
                    'match': False
                }), 400
                
            # Decodificar base64
            temp_path = decode_base64_image(data['image_base64'])
            
            if not temp_path:
                return jsonify({
                    'error': 'Erro ao decodificar imagem base64',
                    'match': False
                }), 400
                
        else:
            # Requisição form data com arquivo
            if 'person_id' not in request.form:
                return jsonify({
                    'error': 'person_id é obrigatório',
                    'match': False
                }), 400
                
            person_id = request.form['person_id']
            
            if 'image' not in request.files:
                return jsonify({
                    'error': 'Nenhuma imagem foi enviada',
                    'match': False
                }), 400
            
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({
                    'error': 'Nenhum arquivo selecionado',
                    'match': False
                }), 400
            
            if not allowed_file(file.filename):
                return jsonify({
                    'error': 'Tipo de arquivo não suportado. Use: png, jpg, jpeg, gif',
                    'match': False
                }), 400
            
            # Salvar arquivo temporariamente
            filename = secure_filename(file.filename)
            temp_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(temp_path)
        
        try:
            # Carregar encodings da pessoa específica
            person_encodings = get_person_encodings(person_id)
            
            if person_encodings is None:
                return jsonify({
                    'error': f'Pessoa com ID {person_id} não encontrada ou sem imagens válidas',
                    'match': False,
                    'person_id': person_id
                }), 404
            
            # Processar imagem enviada
            target_encoding = load_and_encode(temp_path)
            
            if target_encoding is None:
                return jsonify({
                    'error': 'Não foi possível detectar rosto na imagem enviada',
                    'match': False,
                    'person_id': person_id
                }), 400
            
            # Calcular similaridades usando correlação
            similarities = []
            for encoding in person_encodings:
                # Calcular correlação cruzada normalizada
                correlation = np.corrcoef(encoding, target_encoding)[0, 1]
                if not np.isnan(correlation):
                    similarities.append(correlation)
            
            if not similarities:
                return jsonify({
                    'error': 'Não foi possível calcular similaridades',
                    'match': False,
                    'person_id': person_id
                }), 400
            
            avg_similarity = sum(similarities) / len(similarities)
            max_similarity = max(similarities)
            
            # Threshold para similaridade (quanto maior, melhor o match)
            threshold = 0.7
            is_match = avg_similarity > threshold
            
            return jsonify({
                'person_id': person_id,
                'match': is_match,
                'result': 'match' if is_match else 'no-match',
                'avg_similarity': round(float(avg_similarity), 4),
                'max_similarity': round(float(max_similarity), 4),
                'threshold': threshold,
                'total_reference_images': len(person_encodings),
                'status': 'success'
            })
            
        finally:
            # Limpar arquivo temporário
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        return jsonify({
            'error': f'Erro interno: {str(e)}',
            'match': False
        }), 500

@app.route('/list_people', methods=['GET'])
def list_people():
    """Lista todas as pessoas disponíveis"""
    try:
        people = []
        if os.path.exists(BASE_FOLDER):
            for person_id in os.listdir(BASE_FOLDER):
                person_path = os.path.join(BASE_FOLDER, person_id)
                if os.path.isdir(person_path):
                    # Contar imagens válidas
                    image_count = len([f for f in os.listdir(person_path) if allowed_file(f)])
                    people.append({
                        'person_id': person_id,
                        'image_count': image_count
                    })
        
        return jsonify({
            'people': people,
            'total': len(people),
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': f'Erro interno: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/', methods=['GET'])
def home():
    """Endpoint principal com informações da API"""
    return jsonify({
        'message': 'Face Recognition API',
        'version': '2.0',
        'endpoints': {
            'POST /verify': 'Verificar match facial (person_id + image/base64)',
            'GET /list_people': 'Listar pessoas disponíveis'
        },
        'usage': {
            'form_data': 'person_id + image (arquivo)',
            'json': 'person_id + image_base64 (string)'
        },
        'status': 'running'
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('FLASK_PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
