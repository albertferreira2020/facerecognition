# Use Python 3.9 como base
FROM python:3.9-slim

# Instalar dependências do sistema necessárias para OpenCV e face_recognition
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código do projeto
COPY . .

# Criar diretório dataset se não existir
RUN mkdir -p dataset

# Expor a porta 3000
EXPOSE 3000

# Comando para rodar a aplicação
CMD ["python", "api_opencv.py"]
