#!/bin/bash

# Script de healthcheck para verificar se a API está funcionando

API_URL="http://localhost:3000"

echo "🏥 Verificando health da API em ${API_URL}..."

# Verificar se o container está rodando
if ! docker-compose ps | grep -q "facerecognition-api.*Up"; then
    echo "❌ Container não está rodando"
    exit 1
fi

# Fazer uma requisição simples para verificar se a API responde
if curl -f -s "${API_URL}" > /dev/null 2>&1; then
    echo "✅ API está respondendo em ${API_URL}"
    echo "📡 Status: Healthy"
else
    echo "❌ API não está respondendo"
    echo "📋 Logs recentes:"
    docker-compose logs --tail=10 facerecognition-api
    exit 1
fi
