# 🐧 Face Recognition API - Guia para Linux

## 📋 Requisitos do Sistema Linux

### Dependências do Sistema
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y build-essential cmake
sudo apt install -y libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev
sudo apt install -y libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev
sudo apt install -y libpng-dev libjpeg-dev libopenexr-dev libtiff-dev libwebp-dev

# CentOS/RHEL/Rocky Linux
sudo yum update -y
sudo yum install -y python3 python3-pip python3-devel
sudo yum groupinstall -y "Development Tools"
sudo yum install -y cmake gcc-c++
sudo yum install -y opencv-devel opencv-python3

# Arch Linux
sudo pacman -S python python-pip python-virtualenv
sudo pacman -S opencv python-opencv
sudo pacman -S base-devel cmake
```

## 🚀 Instalação no Linux

### 1. Clonar/Baixar o projeto
```bash
git clone <seu-repo>
cd facerecognition
```

### 2. Criar ambiente virtual
```bash
# Criar venv
python3 -m venv venv_linux

# Ativar venv
source venv_linux/bin/activate

# Atualizar pip
pip install --upgrade pip
```

### 3. Instalar dependências
```bash
# Opção 1: Tentar com OpenCV do pip
pip install -r requirements.txt

# Opção 2: Se der erro, usar sistema
pip install Flask==2.3.3 numpy==1.24.3 Pillow==10.0.1 Werkzeug==2.3.7 requests==2.31.0
# OpenCV será usado do sistema (apt install python3-opencv)
```

### 4. Configurar para servidor
```bash
# Tornar executável
chmod +x start_linux.sh

# Executar
./start_linux.sh
```

## 🌐 Configuração para Servidor

### 1. Configurar Firewall
```bash
# Ubuntu/Debian (ufw)
sudo ufw allow 5001
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --reload
```

### 2. Executar como Serviço (systemd)
```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/faceapi.service
```

### 3. Configurar NGINX (Proxy Reverso)
```bash
# Instalar nginx
sudo apt install nginx  # Ubuntu/Debian
sudo yum install nginx  # CentOS/RHEL

# Configurar proxy
sudo nano /etc/nginx/sites-available/faceapi
```

### 4. Usar Gunicorn (Produção)
```bash
# Instalar gunicorn
pip install gunicorn

# Executar
gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

## 🔧 Diferenças para Linux

1. **Variáveis de ambiente**: Usar `export` ao invés de `set`
2. **Separador de path**: `/` ao invés de `\`
3. **Permissões**: Usar `chmod +x` para scripts
4. **Serviços**: systemd ao invés de Windows Services
5. **Firewall**: ufw/firewalld ao invés de Windows Firewall

## 🧪 Teste no Linux
```bash
# Ativar ambiente
source venv_linux/bin/activate

# Testar OpenCV
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"

# Iniciar API
python3 app.py

# Testar API
python3 test_api.py
```

## 📊 Monitoramento no Linux
```bash
# Ver logs
tail -f /var/log/faceapi.log

# Status do serviço
sudo systemctl status faceapi

# Usar htop para monitorar recursos
htop
```

## ⚡ Performance no Linux

- **CPU**: Linux geralmente tem melhor performance
- **Memória**: Gerenciamento mais eficiente
- **I/O**: Sistema de arquivos mais rápido
- **Rede**: Stack de rede otimizado

**✅ O programa funcionará perfeitamente no Linux, possivelmente com melhor performance que no macOS/Windows!**
