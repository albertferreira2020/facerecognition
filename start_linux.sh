#!/bin/bash

# Script para inicializar a Face Recognition API no Linux

echo "🐧 Iniciando Face Recognition API no Linux..."
echo ""

# Verificar se está no Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "⚠️  Este script é otimizado para Linux"
fi

# Verificar se venv existe
if [ ! -d "venv_linux" ] && [ ! -d "venv_new" ] && [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Execute: python3 -m venv venv_linux"
    exit 1
fi

# Determinar qual venv usar
VENV_DIR=""
if [ -d "venv_linux" ]; then
    VENV_DIR="venv_linux"
elif [ -d "venv_new" ]; then
    VENV_DIR="venv_new"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
fi

echo "✅ Usando ambiente virtual: $VENV_DIR"
source $VENV_DIR/bin/activate

echo "✅ Verificando dependências..."
python3 -c "import flask, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependências básicas não instaladas!"
    echo "Execute: pip install -r requirements.txt"
    exit 1
fi

# Verificar OpenCV
python3 -c "import cv2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  OpenCV não encontrado via pip, tentando sistema..."
    python3 -c "import sys; sys.path.append('/usr/lib/python3/dist-packages'); import cv2" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "❌ OpenCV não instalado!"
        echo "Ubuntu/Debian: sudo apt install python3-opencv"
        echo "CentOS/RHEL: sudo yum install opencv-python3"
        exit 1
    else
        echo "✅ OpenCV encontrado no sistema"
    fi
else
    echo "✅ OpenCV encontrado no venv"
fi

echo "✅ Verificando porta 5001..."
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Porta 5001 em uso, tentando porta 5002..."
    export FLASK_PORT=5002
else
    export FLASK_PORT=5001
fi

echo "✅ Iniciando API na porta $FLASK_PORT..."
echo "🌐 Acesse: http://localhost:$FLASK_PORT"
echo "🌐 Rede: http://$(hostname -I | awk '{print $1}'):$FLASK_PORT"
echo "🛑 Pressione Ctrl+C para parar"
echo ""

# Executar com gunicorn se disponível, senão Flask dev server
if command -v gunicorn &> /dev/null; then
    echo "🚀 Usando Gunicorn (produção)..."
    gunicorn -w 2 -b 0.0.0.0:$FLASK_PORT app:app
else
    echo "🔧 Usando Flask dev server..."
    python3 app.py
fi
