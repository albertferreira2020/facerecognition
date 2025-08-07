# Use uma imagem base do Python com OpenCV pré-instalado
FROM python:3.10-slim

# Instalar dependências do sistema necessárias para OpenCV e processamento de imagem
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements-docker.txt requirements.txt

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app.py .
COPY test_recognition.py .
COPY README_MELHORIAS.md .

# Copiar pasta people com imagens de referência
COPY people/ ./people/

# Criar diretório people para armazenar imagens (caso não exista)
RUN mkdir -p people

# Expor porta
EXPOSE 3000

# Definir variáveis de ambiente
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Comando para executar a aplicação
CMD ["python", "app.py"]
