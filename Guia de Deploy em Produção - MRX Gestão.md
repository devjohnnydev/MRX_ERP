# Guia de Deploy em Produção - MRX Gestão

## 📋 Índice

1. [Requisitos](#requisitos)
2. [Deploy Rápido (Recomendado)](#deploy-rápido-recomendado)
3. [Deploy Manual](#deploy-manual)
4. [Configuração SSL/TLS](#configuração-ssltls)
5. [Monitoramento](#monitoramento)
6. [Troubleshooting](#troubleshooting)
7. [Backup e Recuperação](#backup-e-recuperação)

---

## Requisitos

### Servidor
- **OS**: Ubuntu 20.04 LTS ou superior
- **RAM**: Mínimo 1GB (recomendado 2GB+)
- **Disco**: Mínimo 5GB
- **Acesso**: SSH com permissões sudo

### Domínio
- Domínio registrado e apontando para o IP do servidor
- Porta 80 e 443 acessíveis

### Dependências
- Python 3.11+
- Git
- Nginx
- Certbot (para SSL)

---

## Deploy Rápido (Recomendado)

### Passo 1: Preparar o servidor

```bash
# Conectar ao servidor
ssh usuario@seu-servidor.com

# Atualizar sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instalar Git
sudo apt-get install -y git
```

### Passo 2: Executar script de deploy

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/mrx_gestao.git
cd mrx_gestao/deploy

# Dar permissão de execução
chmod +x deploy.sh

# Executar deploy (substitua pelos seus valores)
sudo ./deploy.sh seu-dominio.com admin@seu-dominio.com
```

**Exemplo:**
```bash
sudo ./deploy.sh mrx-gestao.com.br admin@mrx-gestao.com.br
```

### Passo 3: Verificar instalação

```bash
# Verificar status do Gunicorn
sudo systemctl status mrx_gestao

# Verificar status do Nginx
sudo systemctl status nginx

# Acessar a aplicação
# Abra o navegador e acesse: https://seu-dominio.com
```

---

## Deploy Manual

Se preferir configurar manualmente, siga os passos abaixo:

### 1. Preparar Ambiente

```bash
# Criar diretório da aplicação
sudo mkdir -p /var/www/mrx_gestao
cd /var/www/mrx_gestao

# Clonar repositório
sudo git clone https://github.com/seu-usuario/mrx_gestao.git .

# Criar ambiente virtual
sudo python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 2. Configurar Gunicorn

```bash
# Criar arquivo de configuração
sudo tee gunicorn_config.py > /dev/null << 'EOF'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 30
keepalive = 2
accesslog = "/var/log/mrx_gestao/gunicorn_access.log"
errorlog = "/var/log/mrx_gestao/gunicorn_error.log"
loglevel = "info"
raw_env = ["FLASK_ENV=production", "FLASK_APP=app.py"]
EOF

# Criar diretórios de log
sudo mkdir -p /var/log/mrx_gestao
sudo mkdir -p /var/run/mrx_gestao

# Configurar permissões
sudo chown -R www-data:www-data /var/www/mrx_gestao
sudo chown -R www-data:www-data /var/log/mrx_gestao
sudo chown -R www-data:www-data /var/run/mrx_gestao
```

### 3. Criar Serviço Systemd

```bash
# Copiar arquivo de serviço
sudo cp deploy/mrx_gestao.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço
sudo systemctl enable mrx_gestao

# Iniciar serviço
sudo systemctl start mrx_gestao

# Verificar status
sudo systemctl status mrx_gestao
```

### 4. Configurar Nginx

```bash
# Copiar configuração
sudo cp deploy/nginx.conf /etc/nginx/sites-available/mrx_gestao

# Habilitar site
sudo ln -s /etc/nginx/sites-available/mrx_gestao /etc/nginx/sites-enabled/

# Remover site padrão
sudo rm /etc/nginx/sites-enabled/default

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 5. Configurar SSL/TLS

```bash
# Instalar Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot certonly --nginx -d seu-dominio.com

# Configurar renovação automática
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Configuração SSL/TLS

### Let's Encrypt (Gratuito e Recomendado)

```bash
# Obter certificado
sudo certbot certonly --nginx -d seu-dominio.com

# Renovação automática
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Verificar certificados
sudo certbot certificates

# Renovar manualmente
sudo certbot renew --dry-run
```

### Certificado Auto-Assinado (Teste)

```bash
# Gerar certificado
sudo openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/private/mrx_gestao.key \
  -out /etc/ssl/certs/mrx_gestao.crt -days 365 -nodes

# Atualizar Nginx com caminho do certificado
```

---

## Monitoramento

### Verificar Logs

```bash
# Logs do Gunicorn
sudo tail -f /var/log/mrx_gestao/gunicorn_error.log
sudo tail -f /var/log/mrx_gestao/gunicorn_access.log

# Logs do Nginx
sudo tail -f /var/log/nginx/mrx_gestao_error.log
sudo tail -f /var/log/nginx/mrx_gestao_access.log

# Logs do sistema
sudo journalctl -u mrx_gestao -f
```

### Monitorar Recursos

```bash
# CPU e memória
top

# Espaço em disco
df -h

# Conexões de rede
netstat -tuln | grep 8000
```

### Health Check

```bash
# Verificar se aplicação está respondendo
curl -I https://seu-dominio.com

# Verificar banco de dados
sqlite3 /var/www/mrx_gestao/mrx.db ".tables"
```

---

## Troubleshooting

### Problema: Aplicação não inicia

```bash
# Verificar logs
sudo journalctl -u mrx_gestao -n 50

# Verificar permissões
sudo chown -R www-data:www-data /var/www/mrx_gestao

# Reiniciar serviço
sudo systemctl restart mrx_gestao
```

### Problema: Erro 502 Bad Gateway

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status mrx_gestao

# Verificar porta 8000
sudo netstat -tuln | grep 8000

# Reiniciar Gunicorn
sudo systemctl restart mrx_gestao
```

### Problema: Certificado SSL expirado

```bash
# Renovar certificado
sudo certbot renew

# Verificar status
sudo certbot certificates

# Reiniciar Nginx
sudo systemctl restart nginx
```

### Problema: Permissão negada

```bash
# Verificar permissões
ls -la /var/www/mrx_gestao

# Corrigir permissões
sudo chown -R www-data:www-data /var/www/mrx_gestao
sudo chmod -R 755 /var/www/mrx_gestao
sudo chmod -R 775 /var/www/mrx_gestao/static/uploads
```

---

## Backup e Recuperação

### Backup do Banco de Dados

```bash
# Backup manual
sudo cp /var/www/mrx_gestao/mrx.db /backup/mrx_$(date +%Y%m%d_%H%M%S).db

# Backup automático (cron)
sudo crontab -e

# Adicionar linha:
# 0 2 * * * cp /var/www/mrx_gestao/mrx.db /backup/mrx_$(date +\%Y\%m\%d).db
```

### Backup Completo

```bash
# Backup da aplicação
sudo tar -czf /backup/mrx_gestao_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/www/mrx_gestao

# Backup do Nginx
sudo tar -czf /backup/nginx_config_$(date +%Y%m%d).tar.gz \
  /etc/nginx/sites-available/mrx_gestao

# Backup do certificado SSL
sudo tar -czf /backup/ssl_cert_$(date +%Y%m%d).tar.gz \
  /etc/letsencrypt/live/seu-dominio.com
```

### Restaurar Banco de Dados

```bash
# Parar aplicação
sudo systemctl stop mrx_gestao

# Restaurar backup
sudo cp /backup/mrx_YYYYMMDD_HHMMSS.db /var/www/mrx_gestao/mrx.db

# Corrigir permissões
sudo chown www-data:www-data /var/www/mrx_gestao/mrx.db

# Iniciar aplicação
sudo systemctl start mrx_gestao
```

---

## Comandos Úteis

### Gerenciamento de Serviços

```bash
# Iniciar
sudo systemctl start mrx_gestao

# Parar
sudo systemctl stop mrx_gestao

# Reiniciar
sudo systemctl restart mrx_gestao

# Status
sudo systemctl status mrx_gestao

# Habilitar auto-start
sudo systemctl enable mrx_gestao

# Desabilitar auto-start
sudo systemctl disable mrx_gestao
```

### Gerenciamento de Nginx

```bash
# Testar configuração
sudo nginx -t

# Recarregar configuração
sudo systemctl reload nginx

# Reiniciar
sudo systemctl restart nginx

# Ver configuração ativa
sudo nginx -T
```

### Gerenciamento de SSL

```bash
# Listar certificados
sudo certbot certificates

# Renovar certificado
sudo certbot renew

# Renovar com força
sudo certbot renew --force-renewal

# Remover certificado
sudo certbot delete --cert-name seu-dominio.com
```

---

## Otimizações de Performance

### Gunicorn

```python
# gunicorn_config.py
workers = multiprocessing.cpu_count() * 2 + 1  # Aumentar se necessário
worker_class = "sync"  # ou "gevent" para I/O intensivo
max_requests = 1000
max_requests_jitter = 50
```

### Nginx

```nginx
# Aumentar cache
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m;

# Compressão
gzip on;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml application/json;
```

### Banco de Dados

```bash
# Otimizar SQLite
sqlite3 /var/www/mrx_gestao/mrx.db "PRAGMA optimize;"
```

---

## Segurança

### Firewall

```bash
# Abrir portas necessárias
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Atualizações de Segurança

```bash
# Verificar atualizações
sudo apt list --upgradable

# Instalar atualizações
sudo apt-get update && sudo apt-get upgrade -y

# Atualizações automáticas
sudo apt-get install -y unattended-upgrades
sudo systemctl enable unattended-upgrades
```

### Hardening

```bash
# Desabilitar SSH com password
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Alterar porta SSH (opcional)
sudo sed -i 's/^#Port 22/Port 2222/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

---

## Suporte

Para problemas ou dúvidas:

1. Verifique os logs
2. Consulte a documentação do projeto
3. Abra uma issue no GitHub
4. Entre em contato com o suporte

---

**Última atualização**: 08/11/2025
