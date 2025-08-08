# Face Recognition API

Simple API for face registration and verification.

## Installation

### Option 1: Using Homebrew (Recommended for macOS)
```bash
# Install dependencies first
brew install cmake
brew install dlib

# Create virtual environment
python -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Install face_recognition separately
pip install face_recognition

# Install other requirements
pip install -r requirements.txt
```

### Option 2: Using conda (Alternative)
```bash
conda create -n faceapi python=3.9
conda activate faceapi
conda install -c conda-forge dlib
pip install face_recognition
pip install -r requirements.txt
```

### Option 3: Pre-compiled wheel (if available)
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --find-links https://pypi.org/simple/ dlib
pip install face_recognition
pip install -r requirements.txt
```

### Option 4: OpenCV only (Simplest - if face_recognition fails)
```bash
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Use api_opencv.py instead of api.py
```

### Dependências Opcionais para Testes
```bash
pip install requests matplotlib  # Para scripts de teste
```

## Usage

### Option A: Using face_recognition library (Better accuracy)
```bash
python api.py
```

### Option B: Using OpenCV only (Easier installation)
```bash
python api_opencv.py
```

**Note**: If you have trouble installing `face_recognition`, use Option B with OpenCV.

## Endpoints

### POST /register
Register new person with multiple face images.

```json
{
    "person_id": "0000000000000001",
    "image_base64": ["base64_image1", "base64_image2"]
}
```

### POST /verify
Verify a face against registered person.

```json
{
    "person_id": "0000000000000001", 
    "image_base64": "base64_image"
}
```

Returns match status and similarity score. If match is positive, saves image and retrains model.

## Melhorias Implementadas

### 🔍 **Cropping Automático de Rostos**
- **Registro**: Detecta e cropa automaticamente os rostos antes de salvar
- **Verificação**: Cropa o rosto da imagem de verificação para maior precisão
- **Formato Quadrado**: Cria crop quadrado baseado na maior dimensão do rosto
- **Sem Distorção**: Mantém proporções naturais do rosto
- **Padronização**: Redimensiona todas as faces para 180x180 pixels
- **Qualidade**: Salva com qualidade JPEG 95% para manter detalhes

### 🎯 **Biometria Mais Precisa**
- Remove fundo e elementos desnecessários
- Foca apenas na região facial
- Melhora a consistência entre diferentes fotos
- Reduz variações de iluminação e ângulo

### 📊 **Sistema de Distância Inteligente**
- Usa distância euclidiana em vez de similaridade de cosseno
- Compara com todos os modelos para evitar falsos positivos
- Margem de diferença de 15% entre pessoas para maior segurança
- Threshold adaptativo baseado no número de pessoas cadastradas

## Isolamento de Pessoas

O sistema garante que cada `person_id` seja completamente isolado:

- **Modelos separados**: Cada pessoa tem seu próprio arquivo de modelo (`{person_id}_model.pkl`)
- **Verificação rigorosa**: O `/verify` só retorna match se a face corresponder E o `person_id` for o mesmo
- **Treino isolado**: Cada modelo é treinado apenas com imagens da pasta específica da pessoa

### Exemplo de Uso

```bash
# Registrar pessoa 1
curl -X POST http://localhost:3000/register \
  -H "Content-Type: application/json" \
  -d '{"person_id": "0000000000000001", "image_base64": ["base64_image1"]}'

# Registrar pessoa 2  
curl -X POST http://localhost:3000/register \
  -H "Content-Type: application/json" \
  -d '{"person_id": "0000000000000002", "image_base64": ["base64_image2"]}'

# Verificar pessoa 1 (só dará match com suas próprias imagens)
curl -X POST http://localhost:3000/verify \
  -H "Content-Type: application/json" \
  -d '{"person_id": "0000000000000001", "image_base64": "base64_image"}'
```
