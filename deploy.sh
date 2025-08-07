#!/bin/bash

# Script para build e deploy da aplicação Face Recognition

set -e  # Sair se algum comando falhar

echo "🐳 Face Recognition API - Build & Deploy Script"
echo "=============================================="

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Função para limpeza
cleanup() {
    echo "🧹 Limpando containers antigos..."
    docker-compose -f docker-compose-simple.yml down 2>/dev/null || true
    docker system prune -f
}

# Função para build
build() {
    echo "🔨 Fazendo build da imagem..."
    docker-compose -f docker-compose-simple.yml build --no-cache
}

# Função para deploy
deploy() {
    echo "🚀 Fazendo deploy da aplicação..."
    docker-compose -f docker-compose-simple.yml up -d
    
    echo "⏳ Aguardando a aplicação ficar pronta..."
    sleep 10
    
    # Verificar se está funcionando
    if curl -f http://localhost:5001/health > /dev/null 2>&1; then
        echo "✅ Aplicação está funcionando!"
        echo "🌐 Acesse: http://localhost:5001"
        echo "📊 Health check: http://localhost:5001/health"
        echo "🔧 API endpoint: http://localhost:5001/verify"
    else
        echo "❌ Aplicação não está respondendo"
        echo "📋 Logs:"
        docker-compose -f docker-compose-simple.yml logs --tail=20
        exit 1
    fi
}

# Função para mostrar logs
logs() {
    echo "📋 Mostrando logs da aplicação..."
    docker-compose -f docker-compose-simple.yml logs -f
}

# Função para parar
stop() {
    echo "🛑 Parando a aplicação..."
    docker-compose -f docker-compose-simple.yml down
}

# Menu principal
case "${1:-help}" in
    "build")
        cleanup
        build
        ;;
    "deploy")
        deploy
        ;;
    "restart")
        cleanup
        build
        deploy
        ;;
    "logs")
        logs
        ;;
    "stop")
        stop
        ;;
    "status")
        docker-compose -f docker-compose-simple.yml ps
        ;;
    "help")
        echo ""
        echo "Uso: $0 [comando]"
        echo ""
        echo "Comandos disponíveis:"
        echo "  build    - Fazer build da imagem Docker"
        echo "  deploy   - Fazer deploy da aplicação"
        echo "  restart  - Limpar, build e deploy"
        echo "  logs     - Mostrar logs em tempo real"
        echo "  stop     - Parar a aplicação"
        echo "  status   - Mostrar status dos containers"
        echo "  help     - Mostrar esta ajuda"
        echo ""
        echo "Exemplo: $0 restart"
        ;;
    *)
        echo "❌ Comando desconhecido: $1"
        echo "Use '$0 help' para ver os comandos disponíveis"
        exit 1
        ;;
esac
