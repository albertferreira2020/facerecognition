#!/bin/bash

# Exemplos de uso da Face Recognition API v2.0

echo "🎯 === Exemplos de Uso da API v2.0 ==="
echo ""

BASE_URL="http://localhost:5001"

# Verificar se API está rodando
echo "1. Verificando se API está rodando..."
curl -s $BASE_URL/ | python3 -m json.tool || {
    echo "❌ API não está rodando! Execute: python app.py"
    exit 1
}
echo ""

# Listar pessoas
echo "2. Listando pessoas disponíveis..."
curl -s $BASE_URL/list_people | python3 -m json.tool
echo ""

echo "3. Exemplos de verificação facial:"
echo ""

# Exemplo 1: Form data
echo "📤 Exemplo 1: Upload de arquivo (form-data)"
echo "curl -X POST \\"
echo "  -F \"person_id=123213521\" \\"
echo "  -F \"image=@foto.jpg\" \\"
echo "  $BASE_URL/verify"
echo ""

# Exemplo 2: JSON com base64
echo "📤 Exemplo 2: JSON com base64"
echo "curl -X POST \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{
    \"person_id\": \"123213521\",
    \"image_base64\": \"$(base64 -i foto.jpg)\"
  }' \\"
echo "  $BASE_URL/verify"
echo ""

echo "📁 Estrutura de pastas necessária:"
echo "people/"
echo "├── 123213521/          # Pessoa 1"
echo "│   ├── ref1.jpg"
echo "│   ├── ref2.jpg"
echo "│   └── ref3.jpg"
echo "├── xxxxx/              # Pessoa 2"
echo "│   ├── foto1.jpg"
echo "│   └── foto2.jpg"
echo "└── outro_id/           # Pessoa 3"
echo "    └── imagem.png"
echo ""

echo "🧪 Para testar:"
echo "python test_api_v2.py 123213521 sua_foto.jpg"
