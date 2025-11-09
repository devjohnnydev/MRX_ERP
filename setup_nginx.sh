#!/bin/bash

################################################################################
# Script de Setup do Nginx para MRX Gestão
# Este script configura o Nginx como proxy reverso para o Gunicorn
################################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
DOMAIN="seu-dominio.com"  # ALTERAR PARA SEU DOMÍNIO
APP_DIR="/var/www/mrx_gestao"
GUNICORN_SOCKET="127.0.0.1:8000"
NGINX_USER="www-data"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Setup Nginx - MRX Gestão${NC}"
echo -e "${YELLOW}========================================${NC}"

# 1. Instalar Nginx
echo -e "\n${YELLOW}[1/4] Instalando Nginx...${NC}"
sudo apt-get update
sudo apt-get install -y nginx

# 2. Criar arquivo de configuração do Nginx
echo -e "\n${YELLOW}[2/4] Criando configuração do Nginx...${NC}"

sudo tee /etc/nginx/sites-available/mrx_gestao > /dev/null << EOF
# Redirecionar HTTP para HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name ${DOMAIN};
    return 301 https://\$server_name\$request_uri;
}

# HTTPS - Configuração Principal
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ${DOMAIN};

    # SSL/TLS - Certificado Let's Encrypt
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;

    # Configurações SSL/TLS
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Headers de Segurança
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logging
    access_log /var/log/nginx/mrx_gestao_access.log;
    error_log /var/log/nginx/mrx_gestao_error.log;

    # Tamanho máximo de upload
    client_max_body_size 16M;

    # Compressão
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;

    # Proxy para Gunicorn
    location / {
        proxy_pass http://${GUNICORN_SOCKET};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
        proxy_request_buffering off;
    }

    # Arquivos estáticos
    location /static/ {
        alias ${APP_DIR}/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
    }
}
EOF

# 3. Habilitar site
echo -e "\n${YELLOW}[3/4] Habilitando site...${NC}"
if [ -L /etc/nginx/sites-enabled/mrx_gestao ]; then
    echo "Site já está habilitado."
else
    sudo ln -s /etc/nginx/sites-available/mrx_gestao /etc/nginx/sites-enabled/
    echo "Site habilitado."
fi

# Desabilitar site padrão
if [ -L /etc/nginx/sites-enabled/default ]; then
    sudo rm /etc/nginx/sites-enabled/default
fi

# 4. Testar e reiniciar Nginx
echo -e "\n${YELLOW}[4/4] Testando e reiniciando Nginx...${NC}"
sudo nginx -t
sudo systemctl restart nginx

echo -e "\n${GREEN}✓ Setup do Nginx concluído com sucesso!${NC}"
echo -e "\n${YELLOW}Próximos passos:${NC}"
echo "1. Configure o certificado SSL com Let's Encrypt:"
echo "   sudo certbot certonly --nginx -d ${DOMAIN}"
echo "2. Configure renovação automática:"
echo "   sudo systemctl enable certbot.timer"
echo "3. Verifique o status:"
echo "   sudo systemctl status nginx"
echo "4. Acesse: https://${DOMAIN}"
