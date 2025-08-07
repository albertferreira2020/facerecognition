# 🐳 Face Recognition API - Deploy no Portainer

## 📋 Pré-requisitos

- Portainer instalado e rodando
- Docker Engine funcionando
- Repositório clonado no servidor

## 🚀 Deploy via Portainer

### Método 1: Via Repository (Recomendado)

1. **Acessar Portainer**
   - Abra o Portainer no seu navegador
   - Faça login com suas credenciais

2. **Criar Stack**
   - Vá em `Stacks` no menu lateral
   - Clique em `+ Add stack`
   - Nomeie como: `facerecognition-api`

3. **Configurar Repository**
   - Selecione `Repository`
   - Repository URL: `https://github.com/albertferreira2020/facerecognition.git`
   - Reference: `refs/heads/main`
   - Compose path: `docker-compose-simple.yml`

4. **Deploy**
   - Clique em `Deploy the stack`
   - Aguarde o build e deploy completar

### Método 2: Via Web Editor

1. **Criar Stack**
   - Nome: `facerecognition-api`
   - Selecione `Web editor`

2. **Copiar Docker Compose**
   ```yaml
   version: '3.8'

   services:
     facerecognition:
       build: .
       container_name: facerecognition-api
       ports:
         - "3000:3000"
       volumes:
         - people_data:/app/people
         - ./logs:/app/logs
       environment:
         - FLASK_ENV=production
         - PYTHONUNBUFFERED=1
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
         interval: 30s
         timeout: 10s
         retries: 5
         start_period: 40s

   volumes:
     people_data:
       driver: local

   networks:
     default:
       name: facerecognition_network
   ```

3. **Deploy**
   - Clique em `Deploy the stack`

## 🔧 Configuração Pós-Deploy

### Verificar Status
1. Em `Stacks`, clique na stack `facerecognition-api`
2. Verifique se todos os containers estão `running`
3. Acesse os logs para verificar se não há erros

### Testar API
1. **Health Check**
   ```bash
   curl http://seu-servidor:3000/health
   ```

2. **Teste de Reconhecimento**
   ```bash
   curl -X POST http://seu-servidor:3000/verify \
        -H "Content-Type: application/json" \
        -d '{
          "person_id": "test",
          "image_base64": "data:image/jpeg;base64,..."
        }'
   ```

## 📊 Monitoramento

### Logs
- No Portainer: `Stacks` > `facerecognition-api` > `facerecognition` > `Logs`

### Métricas
- Health check endpoint: `http://seu-servidor:3000/health`
- Status: `docker ps` via console

### Volume de Dados
- As imagens são armazenadas no volume `people_data`
- Para backup: `docker cp facerecognition-api:/app/people ./backup-people`

## 🔄 Atualizações

### Via Portainer
1. Vá em `Stacks` > `facerecognition-api`
2. Clique em `Editor`
3. Clique em `Update the stack`

### Via Git Pull
1. Se usando repository, apenas faça commit no GitHub
2. No Portainer: `Pull and redeploy`

## 🛠️ Troubleshooting

### Container não inicia
1. Verificar logs: `Stacks` > `facerecognition-api` > `Logs`
2. Verificar se a porta 3000 não está em uso
3. Verificar recursos do servidor (RAM/CPU)

### API não responde
1. Verificar health check: `curl http://localhost:3000/health`
2. Verificar logs para erros de dependências
3. Restart do container via Portainer

### Problemas de build
1. Limpar imagens antigas: `docker system prune -a`
2. Rebuild forçado: marcar `Re-build` no deploy

## 🔐 Segurança

### Recomendações
- Use reverse proxy (nginx) na frente
- Configure rate limiting
- Use HTTPS em produção
- Monitore logs de acesso

### Firewall
```bash
# Permitir apenas porta necessária
ufw allow 3000/tcp
```

## 📈 Performance

### Otimizações
- Use volume para cache de modelos
- Configure resource limits:
  ```yaml
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '1.0'
        memory: 1G
  ```

### Scaling
- Para múltiplas instâncias, use load balancer
- Configure shared volume para imagens

## 🆘 Suporte

Em caso de problemas:
1. Verifique os logs completos
2. Teste o health check
3. Verifique conectividade de rede
4. Consulte documentação do Docker/Portainer
