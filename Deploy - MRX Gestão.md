# Deploy - MRX Gestão

Este diretório contém scripts e configurações para deploy em produção da aplicação MRX Gestão.

## 📁 Arquivos

### Scripts

| Arquivo | Descrição |
|---------|-----------|
| `deploy.sh` | Script de deploy completo (all-in-one) |
| `setup_gunicorn.sh` | Setup do Gunicorn como servidor de aplicação |
| `setup_nginx.sh` | Setup do Nginx como proxy reverso |
| `setup_ssl.sh` | Setup de certificado SSL/TLS com Let's Encrypt |
| `maintenance.sh` | Script de manutenção e monitoramento |

### Configurações

| Arquivo | Descrição |
|---------|-----------|
| `mrx_gestao.service` | Arquivo de serviço systemd para Gunicorn |
| `nginx.conf` | Configuração completa do Nginx |
| `gunicorn_config.py` | Configuração do Gunicorn (gerada automaticamente) |

### Documentação

| Arquivo | Descrição |
|---------|-----------|
| `DEPLOY_GUIDE.md` | Guia completo de deploy em produção |
| `README.md` | Este arquivo |

---

## 🚀 Quick Start

### Opção 1: Deploy Automático (Recomendado)

```bash
# Dar permissão de execução
chmod +x deploy.sh

# Executar deploy
sudo ./deploy.sh seu-dominio.com admin@seu-dominio.com
```

**Exemplo:**
```bash
sudo ./deploy.sh mrx-gestao.com.br admin@mrx-gestao.com.br
```

### Opção 2: Deploy Manual

Siga os passos em `DEPLOY_GUIDE.md` para configurar manualmente.

---

## 📋 Pré-requisitos

- Ubuntu 20.04 LTS ou superior
- SSH com permissões sudo
- Domínio registrado e apontando para o servidor
- Portas 80 e 443 abertas

---

## 🔧 Uso dos Scripts

### deploy.sh
Script completo que realiza todo o setup:
- Atualiza o sistema
- Instala dependências
- Configura Gunicorn
- Configura Nginx
- Configura SSL/TLS

```bash
sudo ./deploy.sh seu-dominio.com admin@seu-dominio.com
```

### setup_gunicorn.sh
Setup apenas do Gunicorn:

```bash
chmod +x setup_gunicorn.sh
sudo ./setup_gunicorn.sh
```

### setup_nginx.sh
Setup apenas do Nginx:

```bash
chmod +x setup_nginx.sh
sudo ./setup_nginx.sh
```

### setup_ssl.sh
Setup apenas de SSL/TLS:

```bash
chmod +x setup_ssl.sh
sudo ./setup_ssl.sh seu-dominio.com admin@seu-dominio.com
```

### maintenance.sh
Script interativo de manutenção:

```bash
chmod +x maintenance.sh
sudo ./maintenance.sh
```

Menu de opções:
1. Status dos serviços
2. Ver logs
3. Fazer backup
4. Restaurar backup
5. Limpar cache e logs
6. Atualizar aplicação
7. Reiniciar serviços
8. Verificar saúde do sistema
9. Renovar certificado SSL

---

## 📊 Arquitetura de Deploy

```
┌─────────────────────────────────────┐
│         Internet (HTTPS)            │
└──────────────┬──────────────────────┘
               │
        ┌──────▼──────┐
        │   Nginx     │
        │  (Proxy)    │
        │ :80, :443   │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │  Gunicorn   │
        │ :8000       │
        │ (4+ workers)│
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │    Flask    │
        │  App        │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │   SQLite    │
        │  mrx.db     │
        └─────────────┘
```

---

## 🔐 Segurança

### SSL/TLS
- Certificado Let's Encrypt (gratuito)
- Renovação automática
- TLS 1.2 e 1.3
- Ciphers fortes

### Headers de Segurança
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy

### Firewall
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 📊 Monitoramento

### Ver Status
```bash
sudo systemctl status mrx_gestao
sudo systemctl status nginx
```

### Ver Logs
```bash
# Gunicorn
sudo tail -f /var/log/mrx_gestao/gunicorn_error.log

# Nginx
sudo tail -f /var/log/nginx/mrx_gestao_error.log
```

### Health Check
```bash
curl -I https://seu-dominio.com
```

---

## 💾 Backup

### Backup Manual
```bash
sudo cp /var/www/mrx_gestao/mrx.db /backup/mrx_$(date +%Y%m%d).db
```

### Backup Automático (Cron)
```bash
sudo crontab -e

# Adicionar:
0 2 * * * cp /var/www/mrx_gestao/mrx.db /backup/mrx_$(date +\%Y\%m\%d).db
```

### Restaurar
```bash
sudo systemctl stop mrx_gestao
sudo cp /backup/mrx_YYYYMMDD.db /var/www/mrx_gestao/mrx.db
sudo chown www-data:www-data /var/www/mrx_gestao/mrx.db
sudo systemctl start mrx_gestao
```

---

## 🔄 Atualizar Aplicação

```bash
cd /var/www/mrx_gestao
sudo git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart mrx_gestao
```

---

## 🐛 Troubleshooting

### Erro 502 Bad Gateway
```bash
# Verificar se Gunicorn está rodando
sudo systemctl status mrx_gestao

# Reiniciar
sudo systemctl restart mrx_gestao
```

### Certificado SSL expirado
```bash
sudo certbot renew
sudo systemctl restart nginx
```

### Permissão negada
```bash
sudo chown -R www-data:www-data /var/www/mrx_gestao
sudo chmod -R 755 /var/www/mrx_gestao
```

---

## 📞 Suporte

Consulte `DEPLOY_GUIDE.md` para:
- Instruções detalhadas
- Troubleshooting completo
- Otimizações de performance
- Hardening de segurança

---

## 📝 Notas Importantes

1. **Altere o domínio**: Substitua `seu-dominio.com` pelo seu domínio
2. **Altere o email**: Substitua `admin@seu-dominio.com` pelo seu email
3. **Backup**: Sempre faça backup antes de atualizar
4. **Logs**: Monitore os logs regularmente
5. **Certificado**: Renove o certificado SSL antes do vencimento

---

## 🎯 Checklist de Deploy

- [ ] Servidor Ubuntu 20.04+ preparado
- [ ] Domínio registrado e apontando para o servidor
- [ ] SSH configurado com permissões sudo
- [ ] Firewall configurado (portas 80, 443)
- [ ] Script de deploy executado com sucesso
- [ ] Aplicação acessível em HTTPS
- [ ] Certificado SSL válido
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Logs sendo registrados

---

**Última atualização**: 08/11/2025

Para mais informações, consulte `DEPLOY_GUIDE.md`
