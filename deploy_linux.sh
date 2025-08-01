#!/bin/bash

# 🚀 Script de Deploy para Servidor Linux
# Face Recognition API

set -e  # Parar em caso de erro

echo "🐧 === DEPLOY FACE RECOGNITION API - LINUX ==="
echo ""

# Verificar se é root ou sudo
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Não execute como root. Use um usuário normal com sudo."
   exit 1
fi

# Função para detectar distribuição Linux
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo $ID
    else
        echo "unknown"
    fi
}

DISTRO=$(detect_distro)
echo "✅ Distribuição detectada: $DISTRO"

# Instalar dependências do sistema
install_system_deps() {
    echo "📦 Instalando dependências do sistema..."
    
    case $DISTRO in
        ubuntu|debian)
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv python3-dev
            sudo apt install -y build-essential cmake
            sudo apt install -y libopencv-dev python3-opencv
            sudo apt install -y nginx
            ;;
        centos|rhel|rocky)
            sudo yum update -y
            sudo yum install -y python3 python3-pip python3-devel
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y cmake
            sudo yum install -y nginx
            ;;
        *)
            echo "❌ Distribuição não suportada: $DISTRO"
            echo "Por favor, instale manualmente: python3, pip, opencv, nginx"
            ;;
    esac
}

# Configurar aplicação
setup_app() {
    echo "🔧 Configurando aplicação..."
    
    # Criar ambiente virtual
    if [ ! -d "venv_linux" ]; then
        python3 -m venv venv_linux
    fi
    
    # Ativar e instalar dependências
    source venv_linux/bin/activate
    pip install --upgrade pip
    pip install -r requirements-linux.txt
    
    # Testar instalação
    python3 -c "import cv2, flask, numpy; print('✅ Dependências OK')"
    
    # Criar diretórios necessários
    mkdir -p people temp_uploads logs
    chmod 755 people temp_uploads logs
}

# Configurar como serviço
setup_service() {
    echo "🔧 Configurando serviço systemd..."
    
    # Substituir paths no arquivo de serviço
    CURRENT_DIR=$(pwd)
    sed "s|/path/to/facerecognition|$CURRENT_DIR|g" faceapi.service > /tmp/faceapi.service
    
    # Copiar e habilitar serviço
    sudo cp /tmp/faceapi.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable faceapi
}

# Configurar nginx
setup_nginx() {
    echo "🌐 Configurando nginx..."
    
    # Backup da configuração existente
    if [ -f "/etc/nginx/sites-available/default" ]; then
        sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup
    fi
    
    # Copiar configuração
    sudo cp nginx.conf /etc/nginx/sites-available/faceapi
    
    # Habilitar site
    sudo ln -sf /etc/nginx/sites-available/faceapi /etc/nginx/sites-enabled/
    
    # Testar configuração
    sudo nginx -t
    
    # Reiniciar nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
}

# Configurar firewall
setup_firewall() {
    echo "🔥 Configurando firewall..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian
        sudo ufw allow 80
        sudo ufw allow 443
        sudo ufw allow 5001
        echo "✅ Firewall configurado (ufw)"
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --permanent --add-port=5001/tcp
        sudo firewall-cmd --reload
        echo "✅ Firewall configurado (firewalld)"
    else
        echo "⚠️  Firewall não detectado. Configure manualmente portas 80, 443, 5001"
    fi
}

# Função principal
main() {
    echo "🚀 Iniciando deploy..."
    
    # Verificar se está no diretório correto
    if [ ! -f "app.py" ]; then
        echo "❌ Arquivo app.py não encontrado. Execute no diretório do projeto."
        exit 1
    fi
    
    # Executar etapas
    install_system_deps
    setup_app
    setup_service
    setup_nginx
    setup_firewall
    
    echo ""
    echo "🎉 === DEPLOY CONCLUÍDO ==="
    echo ""
    echo "📍 Comandos úteis:"
    echo "   Iniciar API:     sudo systemctl start faceapi"
    echo "   Parar API:       sudo systemctl stop faceapi"
    echo "   Status API:      sudo systemctl status faceapi"
    echo "   Logs API:        sudo journalctl -u faceapi -f"
    echo "   Logs nginx:      sudo tail -f /var/log/nginx/faceapi_*.log"
    echo ""
    echo "🌐 URLs:"
    echo "   API Direta:      http://$(hostname -I | awk '{print $1}'):5001"
    echo "   Nginx Proxy:     http://$(hostname -I | awk '{print $1}')/"
    echo ""
    echo "🔧 Para testar:"
    echo "   curl http://localhost/  # Via nginx"
    echo "   curl http://localhost:5001/  # Direto"
    echo ""
    
    # Iniciar serviços
    echo "🚀 Iniciando serviços..."
    sudo systemctl start faceapi
    sudo systemctl status faceapi --no-pager -l
    
    echo ""
    echo "✅ API está rodando! 🎉"
}

# Executar apenas se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
