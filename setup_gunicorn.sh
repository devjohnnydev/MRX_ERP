#!/bin/bash

################################################################################
# Script de Setup do Gunicorn para MRX Gestão
# Este script configura o Gunicorn como servidor de aplicação
################################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configurações
APP_NAME="mrx_gestao"
APP_USER="www-data"
APP_GROUP="www-data"
APP_DIR="/var/www/mrx_gestao"
VENV_DIR="${APP_DIR}/venv"
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
GUNICORN_PORT=8000
GUNICORN_BIND="127.0.0.1:${GUNICORN_PORT}"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Setup Gunicorn - MRX Gestão${NC}"
echo -e "${YELLOW}========================================${NC}"

# 1. Instalar dependências do sistema
echo -e "\n${YELLOW}[1/5] Instalando dependências do sistema...${NC}"
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev \
    build-essential libssl-dev libffi-dev git curl wget

# 2. Criar usuário de aplicação se não existir
echo -e "\n${YELLOW}[2/5] Configurando usuário de aplicação...${NC}"
if ! id "${APP_USER}" &>/dev/null; then
    echo "Usuário ${APP_USER} não encontrado. Usando www-data existente."
else
    echo "Usuário ${APP_USER} já existe."
fi

# 3. Preparar diretório da aplicação
echo -e "\n${YELLOW}[3/5] Preparando diretório da aplicação...${NC}"
if [ ! -d "${APP_DIR}" ]; then
    sudo mkdir -p "${APP_DIR}"
    echo "Diretório ${APP_DIR} criado."
else
    echo "Diretório ${APP_DIR} já existe."
fi

# 4. Instalar Gunicorn
echo -e "\n${YELLOW}[4/5] Instalando Gunicorn...${NC}"
if [ ! -d "${VENV_DIR}" ]; then
    sudo python3.11 -m venv "${VENV_DIR}"
    echo "Ambiente virtual criado."
fi

# Ativar venv e instalar dependências
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip setuptools wheel
pip install gunicorn
pip install -r "${APP_DIR}/requirements.txt"

# 5. Configurar permissões
echo -e "\n${YELLOW}[5/5] Configurando permissões...${NC}"
sudo chown -R "${APP_USER}:${APP_GROUP}" "${APP_DIR}"
sudo chmod -R 755 "${APP_DIR}"
sudo chmod -R 775 "${APP_DIR}/static/uploads"

# Criar arquivo de configuração do Gunicorn
echo -e "\n${YELLOW}Criando arquivo de configuração do Gunicorn...${NC}"

cat > "${APP_DIR}/gunicorn_config.py" << 'EOF'
"""
Configuração do Gunicorn para MRX Gestão
"""

import multiprocessing
import os

# Binding
bind = "127.0.0.1:8000"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout
timeout = 30
keepalive = 2

# Logging
accesslog = "/var/log/mrx_gestao/gunicorn_access.log"
errorlog = "/var/log/mrx_gestao/gunicorn_error.log"
loglevel = "info"

# Processo
daemon = False
pidfile = "/var/run/mrx_gestao/gunicorn.pid"
umask = 0o022

# Aplicação
pythonpath = "/var/www/mrx_gestao"
raw_env = [
    "FLASK_ENV=production",
    "FLASK_APP=app.py"
]

# Hooks
def on_starting(server):
    print("Gunicorn iniciando...")

def when_ready(server):
    print("Gunicorn pronto. Escutando em 127.0.0.1:8000")

def on_exit(server):
    print("Gunicorn encerrando...")
EOF

sudo chown "${APP_USER}:${APP_GROUP}" "${APP_DIR}/gunicorn_config.py"

# Criar diretórios de log
echo -e "\n${YELLOW}Criando diretórios de log...${NC}"
sudo mkdir -p /var/log/mrx_gestao
sudo mkdir -p /var/run/mrx_gestao
sudo chown -R "${APP_USER}:${APP_GROUP}" /var/log/mrx_gestao
sudo chown -R "${APP_USER}:${APP_GROUP}" /var/run/mrx_gestao

echo -e "\n${GREEN}✓ Setup do Gunicorn concluído com sucesso!${NC}"
echo -e "\n${YELLOW}Próximos passos:${NC}"
echo "1. Copie o arquivo mrx_gestao.service para /etc/systemd/system/"
echo "2. Execute: sudo systemctl daemon-reload"
echo "3. Execute: sudo systemctl enable mrx_gestao"
echo "4. Execute: sudo systemctl start mrx_gestao"
echo "5. Configure o Nginx conforme o script setup_nginx.sh"
