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

### 🐳 Option A: Docker (Recommended for Production)
```bash
# Clone o repositório
git clone https://github.com/albertferreira2020/facerecognition.git
cd facerecognition

# Fazer deploy com Docker Compose
./deploy.sh

# Ou manualmente:
docker-compose up -d --build
```

The API will be available at http://localhost:3000

### 🔧 Option B: Local Development

#### Using face_recognition library (Better accuracy)
```bash
python api.py  # If available
```

#### Using OpenCV only (Easier installation)
```bash
python api_opencv.py
```

**Note**: If you have trouble installing `face_recognition`, use Docker or Option B with OpenCV.

## 🐳 Docker Deployment

### Quick Start
```bash
# Clone e execute
git clone https://github.com/albertferreira2020/facerecognition.git
cd facerecognition
./deploy.sh
```

### Manual Docker Commands
```bash
# Build e start
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Rebuild (após mudanças no código)
docker-compose build --no-cache
docker-compose up -d
```

### Docker Features
- ✅ **Porta 3000**: API rodando em http://localhost:3000
- ✅ **Volume Persistente**: Dataset e modelos mantidos entre restarts
- ✅ **Auto-restart**: Container reinicia automaticamente
- ✅ **Otimizado**: Build otimizado com cache layers
- ✅ **Produção**: Configurado para ambiente de produção

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
