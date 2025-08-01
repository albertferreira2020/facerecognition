#!/bin/bash

# Script para inicializar a Face Recognition API

echo "🚀 Iniciando Face Recognition API..."
echo ""

# Verificar se venv existe
if [ ! -d "venv_new" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Execute: python3 -m venv venv_new"
    exit 1
fi

# Ativar venv e executar API
echo "✅ Ativando ambiente virtual..."
source venv_new/bin/activate

echo "✅ Verificando dependências..."
python -c "import cv2, flask, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependências não instaladas!"
    echo "Execute: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Iniciando API na porta 5001..."
echo "🌐 Acesse: http://localhost:5001"
echo "🛑 Pressione Ctrl+C para parar"
echo ""

python app.py
