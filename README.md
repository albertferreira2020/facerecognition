# Face Recognition API

Uma API Flask simples para reconhecimento facial que compara uma imagem enviada com imagens de referência.

## 🚀 Setup Completo

### 1. Clonar/Baixar o projeto
```bash
git clone <seu-repo>
cd facerecognition
```

### 2. Criar e ativar ambiente virtual
```bash
# Criar venv
python3 -m venv venv

# Ativar venv (macOS/Linux)
source venv/bin/activate

pip install --upgrade pip
# Ativar venv (Windows)
# venv_new\Scripts\activate
```

### 3. Instalar dependências

**Opção 1 - OpenCV (Recomendado para macOS):**
```bash
pip install -r requirements.txt
```

**Opção 2 - Se dar erro de compilação no macOS:**
```bash
# Instalar dependências via Homebrew primeiro
brew install cmake
brew install dlib

# Depois instalar via pip
pip install -r requirements-face-recognition.txt
```

**Opção 3 - Problemas com dlib:**
```bash
# Usar apenas OpenCV (implementação atual)
pip install -r requirements-opencv.txt
```

### 4. Preparar imagens de referência
Coloque as fotos de referência na pasta `people/`:
```
people/
├── 123213521/
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── foto3.png
└── outra_pessoa/
    ├── img1.jpg
    └── img2.jpg
```

### 5. Executar a API
```bash
python app.py
```

A API estará rodando em: `http://localhost:3000`

## 📍 Endpoints

### POST `/register`
Cadastra uma nova pessoa com múltiplas imagens de referência.

**Parâmetros:**
- `person_id`: ID único da pessoa (string)
- `image_base64`: Array de imagens em formato base64 (máximo 10 imagens)

**Exemplo usando curl:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "123456789",
    "image_base64": [
      "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAA...",
      "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAA..."
    ]
  }' \
  http://localhost:3000/register
```

**Resposta de sucesso:**
```json
{
    "success": true,
    "person_id": "123456789",
    "total_images_received": 2,
    "images_saved": 2,
    "images_failed": 0,
    "saved_images": [
        {
            "index": 0,
            "filename": "reference_1_a1b2c3d4.jpg",
            "path": "people/123456789/reference_1_a1b2c3d4.jpg"
        }
    ],
    "message": "Pessoa 123456789 cadastrada com sucesso com 2 imagem(ns) de referência"
}
```

### POST `/verify`
Verifica se há match facial com as imagens de referência.

**Parâmetros:**
- `person_id`: ID da pessoa para verificar
- `image_base64`: Imagem em formato base64 para comparar

**Exemplo usando curl:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "123456789",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAA..."
  }' \
  http://localhost:3000/verify
```

**Resposta de sucesso:**
```json
{
    "match": true,
    "result": "match",
    "avg_similarity": 0.8532,
    "max_similarity": 0.9201,
    "threshold": 0.7,
    "total_reference_images": 5
}
```

**Resposta de erro:**
```json
{
    "error": "Não foi possível detectar rosto na imagem enviada",
    "match": false
}
```

## 🧪 Teste Rápido

```bash
# Cadastrar uma pessoa
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "123456789",
    "image_base64": ["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAA..."]
  }' \
  http://localhost:3000/register

# Verificar uma pessoa
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "123456789", 
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAA..."
  }' \
  http://localhost:3000/verify

# Verificar se API está rodando
curl http://localhost:3000/health
```

## ⚙️ Configurações

- **Threshold**: 0.7 (valores maiores = mais restritivo)
- **Formatos suportados**: PNG, JPG, JPEG, GIF
- **Porta**: 3000
- **Algoritmo**: OpenCV + correlação normalizada

## 🔧 Solução de Problemas

### Erro de compilação do dlib:
1. Instale via Homebrew:
```bash
brew install cmake
brew install dlib
```

2. Ou use apenas OpenCV:
```bash
pip install -r requirements-opencv.txt
```

### Erro "No module named cv2":
```bash
pip install opencv-python
```

### API não detecta rostos:
- Use fotos com boa qualidade
- Certifique-se de que o rosto está bem visível
- Evite fotos muito escuras ou borradas

## 📝 Notas

- Coloque 2-5 fotos de referência por pessoa
- Use fotos claras com rostos bem visíveis
- A API compara com TODAS as imagens de referência na pasta `people/`
- Arquivos temporários são limpos automaticamente
- Algoritmo usa correlação cruzada normalizada para comparação
