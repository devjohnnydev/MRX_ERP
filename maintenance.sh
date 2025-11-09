#!/bin/bash

################################################################################
# Script de Manutenção - MRX Gestão
# Realiza tarefas de manutenção e monitoramento
################################################################################

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
APP_DIR="/var/www/mrx_gestao"
LOG_DIR="/var/log/mrx_gestao"
BACKUP_DIR="/backup"
BACKUP_RETENTION_DAYS=30

# Menu
show_menu() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   MRX Gestão - Manutenção e Monitor   ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "1. Status dos serviços"
    echo "2. Ver logs"
    echo "3. Fazer backup"
    echo "4. Restaurar backup"
    echo "5. Limpar cache e logs"
    echo "6. Atualizar aplicação"
    echo "7. Reiniciar serviços"
    echo "8. Verificar saúde do sistema"
    echo "9. Renovar certificado SSL"
    echo "0. Sair"
    echo ""
}

# 1. Status dos serviços
status_services() {
    echo -e "\n${YELLOW}Status do Gunicorn:${NC}"
    sudo systemctl status mrx_gestao --no-pager | head -20
    
    echo -e "\n${YELLOW}Status do Nginx:${NC}"
    sudo systemctl status nginx --no-pager | head -20
    
    echo -e "\n${YELLOW}Portas em uso:${NC}"
    sudo netstat -tuln | grep -E ':(80|443|8000)'
}

# 2. Ver logs
view_logs() {
    echo -e "\n${YELLOW}Selecione o log a visualizar:${NC}"
    echo "1. Gunicorn (erro)"
    echo "2. Gunicorn (acesso)"
    echo "3. Nginx (erro)"
    echo "4. Nginx (acesso)"
    echo "5. Sistema"
    echo "0. Voltar"
    read -p "Opção: " log_choice
    
    case $log_choice in
        1)
            echo -e "\n${YELLOW}Últimas 50 linhas de /var/log/mrx_gestao/gunicorn_error.log${NC}"
            sudo tail -50 /var/log/mrx_gestao/gunicorn_error.log
            ;;
        2)
            echo -e "\n${YELLOW}Últimas 50 linhas de /var/log/mrx_gestao/gunicorn_access.log${NC}"
            sudo tail -50 /var/log/mrx_gestao/gunicorn_access.log
            ;;
        3)
            echo -e "\n${YELLOW}Últimas 50 linhas de /var/log/nginx/mrx_gestao_error.log${NC}"
            sudo tail -50 /var/log/nginx/mrx_gestao_error.log
            ;;
        4)
            echo -e "\n${YELLOW}Últimas 50 linhas de /var/log/nginx/mrx_gestao_access.log${NC}"
            sudo tail -50 /var/log/nginx/mrx_gestao_access.log
            ;;
        5)
            echo -e "\n${YELLOW}Últimas 50 linhas do journal${NC}"
            sudo journalctl -u mrx_gestao -n 50 --no-pager
            ;;
    esac
}

# 3. Fazer backup
make_backup() {
    echo -e "\n${YELLOW}Criando backup...${NC}"
    
    # Criar diretório de backup
    sudo mkdir -p "${BACKUP_DIR}"
    
    # Backup do banco de dados
    BACKUP_FILE="${BACKUP_DIR}/mrx_db_$(date +%Y%m%d_%H%M%S).db"
    sudo cp "${APP_DIR}/mrx.db" "${BACKUP_FILE}"
    sudo chown $(whoami):$(whoami) "${BACKUP_FILE}"
    
    echo -e "${GREEN}✓ Backup do banco de dados criado: ${BACKUP_FILE}${NC}"
    
    # Backup completo (opcional)
    read -p "Deseja fazer backup completo da aplicação? (s/n) " full_backup
    if [ "$full_backup" = "s" ] || [ "$full_backup" = "S" ]; then
        FULL_BACKUP="${BACKUP_DIR}/mrx_full_$(date +%Y%m%d_%H%M%S).tar.gz"
        sudo tar -czf "${FULL_BACKUP}" -C /var/www mrx_gestao
        sudo chown $(whoami):$(whoami) "${FULL_BACKUP}"
        echo -e "${GREEN}✓ Backup completo criado: ${FULL_BACKUP}${NC}"
    fi
    
    # Listar backups
    echo -e "\n${YELLOW}Backups disponíveis:${NC}"
    ls -lh "${BACKUP_DIR}" | grep mrx
}

# 4. Restaurar backup
restore_backup() {
    echo -e "\n${YELLOW}Backups disponíveis:${NC}"
    ls -lh "${BACKUP_DIR}" | grep mrx
    
    read -p "Digite o nome do arquivo de backup: " backup_file
    
    if [ ! -f "${BACKUP_DIR}/${backup_file}" ]; then
        echo -e "${RED}Arquivo não encontrado!${NC}"
        return
    fi
    
    echo -e "\n${YELLOW}Parando aplicação...${NC}"
    sudo systemctl stop mrx_gestao
    
    if [[ $backup_file == *.tar.gz ]]; then
        echo -e "${YELLOW}Restaurando backup completo...${NC}"
        sudo tar -xzf "${BACKUP_DIR}/${backup_file}" -C /var/www
    else
        echo -e "${YELLOW}Restaurando banco de dados...${NC}"
        sudo cp "${BACKUP_DIR}/${backup_file}" "${APP_DIR}/mrx.db"
    fi
    
    sudo chown -R www-data:www-data "${APP_DIR}"
    
    echo -e "${YELLOW}Iniciando aplicação...${NC}"
    sudo systemctl start mrx_gestao
    
    echo -e "${GREEN}✓ Backup restaurado com sucesso!${NC}"
}

# 5. Limpar cache e logs
cleanup() {
    echo -e "\n${YELLOW}Limpando cache e logs...${NC}"
    
    # Limpar logs antigos
    sudo find /var/log/mrx_gestao -type f -name "*.log" -mtime +30 -delete
    sudo find /var/log/nginx -type f -name "*mrx*" -mtime +30 -delete
    
    # Limpar backups antigos
    sudo find "${BACKUP_DIR}" -type f -name "mrx*" -mtime +${BACKUP_RETENTION_DAYS} -delete
    
    # Limpar cache do Nginx
    sudo rm -rf /var/cache/nginx/*
    
    echo -e "${GREEN}✓ Limpeza concluída!${NC}"
    
    # Mostrar espaço liberado
    echo -e "\n${YELLOW}Espaço em disco:${NC}"
    df -h /
}

# 6. Atualizar aplicação
update_app() {
    echo -e "\n${YELLOW}Atualizando aplicação...${NC}"
    
    cd "${APP_DIR}"
    
    # Fazer backup antes de atualizar
    echo -e "${YELLOW}Fazendo backup antes da atualização...${NC}"
    sudo cp mrx.db "${BACKUP_DIR}/mrx_before_update_$(date +%Y%m%d_%H%M%S).db"
    
    # Parar aplicação
    echo -e "${YELLOW}Parando aplicação...${NC}"
    sudo systemctl stop mrx_gestao
    
    # Atualizar código
    echo -e "${YELLOW}Atualizando código...${NC}"
    sudo git pull origin main
    
    # Atualizar dependências
    echo -e "${YELLOW}Atualizando dependências...${NC}"
    source venv/bin/activate
    pip install --upgrade -r requirements.txt
    
    # Iniciar aplicação
    echo -e "${YELLOW}Iniciando aplicação...${NC}"
    sudo systemctl start mrx_gestao
    
    echo -e "${GREEN}✓ Aplicação atualizada com sucesso!${NC}"
}

# 7. Reiniciar serviços
restart_services() {
    echo -e "\n${YELLOW}Reiniciando serviços...${NC}"
    
    sudo systemctl restart mrx_gestao
    sudo systemctl restart nginx
    
    sleep 2
    
    echo -e "\n${YELLOW}Status após reinicialização:${NC}"
    status_services
}

# 8. Verificar saúde do sistema
health_check() {
    echo -e "\n${BLUE}═════════════════════════════════════════${NC}"
    echo -e "${BLUE}Health Check - MRX Gestão${NC}"
    echo -e "${BLUE}═════════════════════════════════════════${NC}"
    
    # CPU e Memória
    echo -e "\n${YELLOW}CPU e Memória:${NC}"
    free -h | grep -E "Mem|Swap"
    echo "CPU Load: $(uptime | awk -F'load average:' '{print $2}')"
    
    # Espaço em disco
    echo -e "\n${YELLOW}Espaço em disco:${NC}"
    df -h / | tail -1
    
    # Serviços
    echo -e "\n${YELLOW}Serviços:${NC}"
    for service in mrx_gestao nginx; do
        if sudo systemctl is-active --quiet $service; then
            echo -e "${GREEN}✓ $service${NC}"
        else
            echo -e "${RED}✗ $service${NC}"
        fi
    done
    
    # Conectividade
    echo -e "\n${YELLOW}Conectividade:${NC}"
    if curl -s -o /dev/null -w "%{http_code}" https://localhost > /dev/null 2>&1; then
        echo -e "${GREEN}✓ HTTPS respondendo${NC}"
    else
        echo -e "${RED}✗ HTTPS não respondendo${NC}"
    fi
    
    # Banco de dados
    echo -e "\n${YELLOW}Banco de dados:${NC}"
    if [ -f "${APP_DIR}/mrx.db" ]; then
        DB_SIZE=$(du -h "${APP_DIR}/mrx.db" | cut -f1)
        echo -e "${GREEN}✓ Banco de dados: ${DB_SIZE}${NC}"
    else
        echo -e "${RED}✗ Banco de dados não encontrado${NC}"
    fi
    
    # Certificado SSL
    echo -e "\n${YELLOW}Certificado SSL:${NC}"
    if sudo certbot certificates 2>/dev/null | grep -q "VALID"; then
        EXPIRY=$(sudo certbot certificates 2>/dev/null | grep "expiry" | head -1)
        echo -e "${GREEN}✓ ${EXPIRY}${NC}"
    else
        echo -e "${YELLOW}⚠ Certificado não configurado${NC}"
    fi
}

# 9. Renovar certificado SSL
renew_ssl() {
    echo -e "\n${YELLOW}Renovando certificado SSL...${NC}"
    
    sudo certbot renew --dry-run
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Certificado renovado com sucesso!${NC}"
        sudo systemctl restart nginx
    else
        echo -e "${RED}✗ Erro ao renovar certificado${NC}"
    fi
}

# Main loop
while true; do
    show_menu
    read -p "Selecione uma opção: " choice
    
    case $choice in
        1) status_services ;;
        2) view_logs ;;
        3) make_backup ;;
        4) restore_backup ;;
        5) cleanup ;;
        6) update_app ;;
        7) restart_services ;;
        8) health_check ;;
        9) renew_ssl ;;
        0) 
            echo -e "\n${GREEN}Até logo!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opção inválida!${NC}"
            ;;
    esac
    
    read -p "Pressione Enter para continuar..."
done
