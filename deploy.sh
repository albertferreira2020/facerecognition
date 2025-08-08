#!/bin/bash

echo "🚀 Iniciando deploy do Face Recognition API..."

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Fazer build da nova imagem
echo "🔨 Fazendo build da aplicação..."
docker-compose build --no-cache

# Subir os serviços
echo "▶️ Iniciando serviços..."
docker-compose up -d

# Verificar status
echo "✅ Verificando status dos containers..."
docker-compose ps

echo "🎉 Deploy concluído!"
echo "📡 API disponível em: http://localhost:3000"
echo ""
echo "📝 Para ver logs em tempo real:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para parar a aplicação:"
echo "   docker-compose down"
