# 🐳 Face Recognition API - Docker Setup

## 📦 Arquivos de Deploy

Este projeto inclui vários arquivos para facilitar o deploy:

### 🔧 Arquivos Principais
- `Dockerfile` - Imagem Docker da aplicação
- `docker-compose.yml` - Setup completo com Nginx
- `docker-compose-simple.yml` - Setup simples apenas com API  
- `requirements-docker.txt` - Dependências Python otimizadas
- `nginx.conf` - Configuração do proxy reverso
- `deploy.sh` - Script automatizado de deploy

### 📋 Arquivos de Configuração
- `.dockerignore` - Arquivos ignorados no build
- `.env.example` - Variáveis de ambiente exemplo
- `PORTAINER_DEPLOY.md` - Instruções para Portainer

## 🚀 Deploy Rápido

### Opção 1: Script Automatizado
```bash
# Build e deploy em um comando
./deploy.sh restart

# Ver logs
./deploy.sh logs

# Parar aplicação
./deploy.sh stop
```

### Opção 2: Docker Compose Manual
```bash
# Setup simples (apenas API)
docker-compose -f docker-compose-simple.yml up -d

# Setup completo (API + Nginx)
docker-compose up -d
```

### Opção 3: Docker Manual
```bash
# Build da imagem
docker build -t facerecognition-api .

# Executar container
docker run -d \
  --name facerecognition \
  -p 5001:5001 \
  -v people_data:/app/people \
  facerecognition-api
```

## 🔗 Endpoints

| Endpoint | Método | Descrição |
|----------|---------|-----------|
| `/health` | GET | Health check |
| `/verify` | POST | Verificar reconhecimento facial |

### Exemplo de Uso
```bash
# Health check
curl http://localhost:5001/health

# Verificar face
curl -X POST http://localhost:5001/verify \
  -H "Content-Type: application/json" \
  -d '{
    "person_id": "123",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD..."
  }'
```

## 📊 Monitoramento

### Status dos Containers
```bash
# Ver containers rodando
docker ps

# Ver logs
docker logs facerecognition-api

# Estatísticas de uso
docker stats facerecognition-api
```

### Health Check
```bash
# Verificar se está saudável
curl -f http://localhost:5001/health || echo "Service is down"
```

## 💾 Volumes e Dados

### Backup das Imagens
```bash
# Backup do volume
docker run --rm -v people_data:/data -v $(pwd):/backup alpine tar czf /backup/people-backup.tar.gz -C /data .

# Restaurar backup
docker run --rm -v people_data:/data -v $(pwd):/backup alpine tar xzf /backup/people-backup.tar.gz -C /data
```

### Limpar Dados
```bash
# Remover volume (cuidado!)
docker volume rm people_data
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```yaml
environment:
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
  - CORRELATION_THRESHOLD=0.80
  - MAX_IMAGE_SIZE=50MB
```

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Networking
```yaml
networks:
  facerecognition_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🛠️ Desenvolvimento

### Build Local
```bash
# Build para desenvolvimento
docker build -t facerecognition-dev -f Dockerfile.dev .

# Executar com reload automático
docker run -it --rm \
  -p 5001:5001 \
  -v $(pwd):/app \
  facerecognition-dev
```

### Debug
```bash
# Executar shell no container
docker exec -it facerecognition-api bash

# Ver arquivos
docker exec facerecognition-api ls -la /app/people
```

## 🚨 Troubleshooting

### Problemas Comuns

**Container não inicia:**
```bash
# Verificar logs
docker logs facerecognition-api

# Verificar recursos
docker system df
```

**API não responde:**
```bash
# Testar conectividade
docker exec facerecognition-api curl localhost:5001/health

# Verificar processos
docker exec facerecognition-api ps aux
```

**Erro de dependências:**
```bash
# Rebuild sem cache
docker build --no-cache -t facerecognition-api .
```

### Limpeza
```bash
# Limpar tudo
docker-compose down -v
docker system prune -a

# Remover apenas imagens não utilizadas
docker image prune
```

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Portainer](https://documentation.portainer.io/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.0.x/deploying/)
