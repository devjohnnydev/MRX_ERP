#!/bin/bash

################################################################################
# Script de Setup SSL/TLS com Let's Encrypt para MRX Gestão
# Este script configura certificados HTTPS automáticos
################################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
DOMAIN="${1:-seu-dominio.com}"
EMAIL="${2:-admin@seu-dominio.com}"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Setup SSL/TLS - MRX Gestão${NC}"
echo -e "${YELLOW}========================================${NC}"

if [ -z "$1" ]; then
    echo -e "${RED}Erro: Domínio não especificado${NC}"
    echo "Uso: $0 seu-dominio.com admin@seu-dominio.com"
    exit 1
fi

# 1. Instalar Certbot
echo -e "\n${YELLOW}[1/4] Instalando Certbot...${NC}"
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx

# 2. Obter certificado
echo -e "\n${YELLOW}[2/4] Obtendo certificado SSL...${NC}"
sudo certbot certonly --nginx \
    -d "${DOMAIN}" \
    --non-interactive \
    --agree-tos \
    --email "${EMAIL}" \
    --redirect

# 3. Configurar renovação automática
echo -e "\n${YELLOW}[3/4] Configurando renovação automática...${NC}"
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Verificar status
echo -e "\n${YELLOW}[4/4] Verificando status...${NC}"
sudo certbot certificates

echo -e "\n${GREEN}✓ Setup SSL/TLS concluído com sucesso!${NC}"
echo -e "\n${YELLOW}Informações do certificado:${NC}"
echo "Domínio: ${DOMAIN}"
echo "Email: ${EMAIL}"
echo "Localização: /etc/letsencrypt/live/${DOMAIN}/"
echo ""
echo -e "${YELLOW}Próximos passos:${NC}"
echo "1. Verifique o Nginx: sudo nginx -t"
echo "2. Reinicie o Nginx: sudo systemctl restart nginx"
echo "3. Acesse: https://${DOMAIN}"
echo ""
echo -e "${YELLOW}Renovação automática:${NC}"
echo "O certificado será renovado automaticamente 30 dias antes do vencimento."
echo "Verifique com: sudo systemctl status certbot.timer"
