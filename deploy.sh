#!/bin/bash

################################################################################
# Script de Deploy Completo - MRX Gestão
# Este script realiza o deploy completo da aplicação em produção
################################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
DOMAIN="${1:-seu-dominio.com}"
EMAIL="${2:-admin@seu-dominio.com}"
APP_DIR="/var/www/mrx_gestao"
REPO_URL="${3:-https://github.com/seu-usuario/mrx_gestao.git}"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════╗"
echo "║   MRX Gestão - Deploy em Produção     ║"
echo "╚════════════════════════════════════════╝"
echo -e "${NC}"

# Validar parâmetros
if [ -z "$1" ]; then
    echo -e "${RED}Erro: Domínio não especificado${NC}"
    echo "Uso: $0 seu-dominio.com admin@seu-dominio.com [repo-url]"
    exit 1
fi

# 1. Atualizar sistema
echo -e "\n${YELLOW}[1/7] Atualizando sistema...${NC}"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y curl wget git build-essential

# 2. Instalar dependências
echo -e "\n${YELLOW}[2/7] Instalando dependências...${NC}"
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev \
    libssl-dev libffi-dev nginx certbot python3-certbot-nginx

# 3. Preparar diretório da aplicação
echo -e "\n${YELLOW}[3/7] Preparando diretório da aplicação...${NC}"
if [ ! -d "${APP_DIR}" ]; then
    sudo mkdir -p "${APP_DIR}"
    echo "Diretório criado: ${APP_DIR}"
fi

# Clonar/atualizar repositório
if [ -d "${APP_DIR}/.git" ]; then
    echo "Atualizando repositório..."
    cd "${APP_DIR}"
    sudo git pull origin main
else
    echo "Clonando repositório..."
    sudo git clone "${REPO_URL}" "${APP_DIR}"
fi

# 4. Configurar ambiente virtual e dependências
echo -e "\n${YELLOW}[4/7] Configurando ambiente virtual...${NC}"
if [ ! -d "${APP_DIR}/venv" ]; then
    sudo python3.11 -m venv "${APP_DIR}/venv"
fi

source "${APP_DIR}/venv/bin/activate"
pip install --upgrade pip setuptools wheel
pip install -r "${APP_DIR}/requirements.txt"
pip install gunicorn

# 5. Configurar Gunicorn
echo -e "\n${YELLOW}[5/7] Configurando Gunicorn...${NC}"

# Criar arquivo de configuração
sudo tee "${APP_DIR}/gunicorn_config.py" > /dev/null << 'EOF'
import multiprocessing
import os

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
sudo chown -R www-data:www-data "${APP_DIR}"
sudo chown -R www-data:www-data /var/log/mrx_gestao
sudo chown -R www-data:www-data /var/run/mrx_gestao
sudo chmod -R 755 "${APP_DIR}"
sudo chmod -R 775 "${APP_DIR}/static/uploads"

# Criar arquivo de serviço systemd
echo -e "\n${YELLOW}Criando serviço systemd...${NC}"
sudo tee /etc/systemd/system/mrx_gestao.service > /dev/null << EOF
[Unit]
Description=MRX Gestão - Gunicorn Application Server
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
Environment="FLASK_ENV=production"
Environment="FLASK_APP=app.py"
ExecStart=${APP_DIR}/venv/bin/gunicorn \\
    --config ${APP_DIR}/gunicorn_config.py \\
    --access-logfile /var/log/mrx_gestao/gunicorn_access.log \\
    --error-logfile /var/log/mrx_gestao/gunicorn_error.log \\
    app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 6. Configurar Nginx
echo -e "\n${YELLOW}[6/7] Configurando Nginx...${NC}"

sudo tee /etc/nginx/sites-available/mrx_gestao > /dev/null << EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    access_log /var/log/nginx/mrx_gestao_access.log;
    error_log /var/log/nginx/mrx_gestao_error.log;

    client_max_body_size 16M;

    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias ${APP_DIR}/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location ~ /\. {
        deny all;
    }
}
EOF

# Habilitar site
if [ ! -L /etc/nginx/sites-enabled/mrx_gestao ]; then
    sudo ln -s /etc/nginx/sites-available/mrx_gestao /etc/nginx/sites-enabled/
fi

# Remover site padrão
if [ -L /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# Testar Nginx
sudo nginx -t

# 7. Configurar SSL/TLS
echo -e "\n${YELLOW}[7/7] Configurando SSL/TLS com Let's Encrypt...${NC}"
sudo certbot certonly --nginx \
    -d "${DOMAIN}" \
    --non-interactive \
    --agree-tos \
    --email "${EMAIL}" \
    --redirect 2>/dev/null || echo "Certificado pode já estar configurado"

# Habilitar renovação automática
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Iniciar serviços
echo -e "\n${YELLOW}Iniciando serviços...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable mrx_gestao
sudo systemctl start mrx_gestao
sudo systemctl restart nginx

# Verificar status
echo -e "\n${GREEN}✓ Deploy concluído com sucesso!${NC}"
echo -e "\n${BLUE}═════════════════════════════════════════${NC}"
echo -e "${BLUE}Status dos Serviços:${NC}"
echo -e "${BLUE}═════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}Gunicorn:${NC}"
sudo systemctl status mrx_gestao --no-pager

echo -e "\n${YELLOW}Nginx:${NC}"
sudo systemctl status nginx --no-pager

echo -e "\n${BLUE}═════════════════════════════════════════${NC}"
echo -e "${GREEN}Acesse a aplicação em: https://${DOMAIN}${NC}"
echo -e "${BLUE}═════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}Comandos úteis:${NC}"
echo "• Ver logs do Gunicorn: sudo tail -f /var/log/mrx_gestao/gunicorn_error.log"
echo "• Ver logs do Nginx: sudo tail -f /var/log/nginx/mrx_gestao_error.log"
echo "• Reiniciar aplicação: sudo systemctl restart mrx_gestao"
echo "• Parar aplicação: sudo systemctl stop mrx_gestao"
echo "• Ver status: sudo systemctl status mrx_gestao"
echo "• Certificado SSL: sudo certbot certificates"
