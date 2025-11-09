# MRX Gestão - Deploy em Produção
## Arquitetura, Execução e Segurança

---

## Slide 1: Título

# MRX Gestão
## Deploy em Produção

**Arquitetura • Execução • Segurança**

Sistema de Gestão Empresarial  
Python/Flask • Gunicorn • Nginx • Let's Encrypt

---

## Slide 2: Visão Geral do Projeto

### MRX Gestão - Sistema Completo

- **Backend**: Python 3.11 + Flask 3.1.2
- **Banco de Dados**: SQLite local
- **Autenticação**: Login com hash seguro
- **Roles**: ADMIN, COMPRADOR, VISUALIZADOR
- **Funcionalidades**: CRUD completo + Dashboard + Relatórios PDF

### Funcionalidades Principais

✓ Gestão de Funcionários  
✓ Gestão de Fornecedores  
✓ Registro de Compras  
✓ Controle de Despesas  
✓ Dashboard com Gráficos  
✓ Exportação de Relatórios  

---

## Slide 3: Arquitetura de Deploy

### Arquitetura em Camadas

```
┌─────────────────────────────────┐
│   Internet (HTTPS - Port 443)   │
└──────────────┬──────────────────┘
               │
        ┌──────▼──────────┐
        │  Nginx Proxy    │
        │  Reverse Proxy  │
        │  Port 80 → 443  │
        └──────┬──────────┘
               │
        ┌──────▼──────────┐
        │    Gunicorn     │
        │  App Server     │
        │  Port 8000      │
        │  4+ Workers     │
        └──────┬──────────┘
               │
        ┌──────▼──────────┐
        │  Flask App      │
        │  Aplicação      │
        └──────┬──────────┘
               │
        ┌──────▼──────────┐
        │  SQLite DB      │
        │  mrx.db         │
        └─────────────────┘
```

---

## Slide 4: Componentes de Deploy

### Stack Tecnológico

| Componente | Versão | Função |
|-----------|--------|--------|
| **Ubuntu** | 20.04+ | Sistema Operacional |
| **Python** | 3.11 | Runtime da Aplicação |
| **Flask** | 3.1.2 | Framework Web |
| **Gunicorn** | 21.2+ | Servidor de Aplicação |
| **Nginx** | 1.18+ | Proxy Reverso |
| **SQLite** | 3.x | Banco de Dados |
| **Let's Encrypt** | - | Certificado SSL/TLS |
| **Certbot** | - | Gerenciador SSL |

---

## Slide 5: Passos de Deploy - Visão Geral

### Deploy em 3 Passos

#### 1️⃣ Preparar Servidor
```bash
ssh usuario@seu-servidor.com
sudo apt-get update && sudo apt-get upgrade -y
```

#### 2️⃣ Executar Script de Deploy
```bash
cd deploy
sudo ./deploy.sh seu-dominio.com admin@seu-dominio.com
```

#### 3️⃣ Acessar Aplicação
```
https://seu-dominio.com
```

**Tempo Total**: ~5-10 minutos

---

## Slide 6: Script de Deploy - O Que Faz

### deploy.sh - Automação Completa

O script realiza automaticamente:

✓ Atualiza o sistema  
✓ Instala dependências (Python, Nginx, Certbot)  
✓ Cria ambiente virtual Python  
✓ Instala pacotes Python  
✓ Configura Gunicorn (4+ workers)  
✓ Cria arquivo de serviço systemd  
✓ Configura Nginx como proxy reverso  
✓ Obtém certificado SSL/TLS  
✓ Configura renovação automática  
✓ Inicia todos os serviços  
✓ Valida a instalação  

---

## Slide 7: Estrutura de Pastas em Produção

### Diretórios Principais

```
/var/www/mrx_gestao/          # Aplicação
├── app.py
├── models.py
├── requirements.txt
├── mrx.db
├── venv/                      # Ambiente Virtual
├── static/
│   ├── css/
│   ├── img/
│   └── uploads/
└── templates/

/var/log/mrx_gestao/          # Logs
├── gunicorn_access.log
└── gunicorn_error.log

/etc/systemd/system/          # Serviços
└── mrx_gestao.service

/etc/nginx/sites-available/   # Nginx
└── mrx_gestao
```

---

## Slide 8: Configuração Gunicorn

### Gunicorn - Servidor de Aplicação

**Características:**
- Workers: CPU × 2 + 1 (automático)
- Timeout: 30 segundos
- Keepalive: 2 segundos
- Bind: 127.0.0.1:8000

**Arquivo de Serviço (systemd):**
```ini
[Unit]
Description=MRX Gestão - Gunicorn
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/mrx_gestao
ExecStart=/var/www/mrx_gestao/venv/bin/gunicorn \
    --config gunicorn_config.py app:app

Restart=always
```

---

## Slide 9: Configuração Nginx

### Nginx - Proxy Reverso

**Funções:**
- Recebe requisições HTTPS (porta 443)
- Redireciona HTTP para HTTPS
- Proxy para Gunicorn (porta 8000)
- Serve arquivos estáticos
- Compressão Gzip

**Configuração:**
```nginx
server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    ssl_certificate /etc/letsencrypt/live/seu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/seu-dominio.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Slide 10: SSL/TLS - Let's Encrypt

### Certificado HTTPS Automático

**Let's Encrypt:**
- Certificado gratuito
- Válido por 90 dias
- Renovação automática

**Configuração:**
```bash
sudo certbot certonly --nginx -d seu-dominio.com
sudo systemctl enable certbot.timer
```

**Renovação Automática:**
- Certbot verifica diariamente
- Renova 30 dias antes do vencimento
- Sem intervenção manual

---

## Slide 11: Segurança - Headers HTTP

### Headers de Segurança Implementados

| Header | Valor | Função |
|--------|-------|--------|
| **HSTS** | max-age=31536000 | Força HTTPS por 1 ano |
| **X-Frame-Options** | SAMEORIGIN | Previne clickjacking |
| **X-Content-Type-Options** | nosniff | Previne MIME sniffing |
| **X-XSS-Protection** | 1; mode=block | Proteção XSS |
| **Referrer-Policy** | no-referrer-when-downgrade | Controla referrer |

---

## Slide 12: Segurança - Criptografia

### Criptografia de Senhas

**Algoritmo: Argon2**
- Resistente a força bruta
- Resistente a GPU attacks
- Resistente a timing attacks
- Padrão moderno (2015+)

**Exemplo:**
```python
# Senha original
senha = "Admin@123"

# Hash Argon2
hash = "$argon2id$v=19$m=65540,t=3,p=4$..."

# Verificação
check_password_hash(hash, "Admin@123")  # True
```

---

## Slide 13: Segurança - Firewall

### Firewall UFW - Configuração

**Portas Abertas:**
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

**Proteção:**
- Bloqueia todas as conexões por padrão
- Permite apenas portas necessárias
- Logs de tentativas bloqueadas

---

## Slide 14: Segurança - Proteção contra Ataques

### Proteções Implementadas

**SQL Injection:**
✓ SQLAlchemy ORM (queries parametrizadas)

**XSS (Cross-Site Scripting):**
✓ Jinja2 auto-escaping  
✓ Header X-XSS-Protection  

**CSRF (Cross-Site Request Forgery):**
✓ Flask-WTF CSRF tokens

**Clickjacking:**
✓ X-Frame-Options: SAMEORIGIN

**MIME Sniffing:**
✓ X-Content-Type-Options: nosniff

---

## Slide 15: Monitoramento e Logs

### Sistema de Logs

**Arquivos de Log:**
```
/var/log/mrx_gestao/gunicorn_access.log
/var/log/mrx_gestao/gunicorn_error.log
/var/log/nginx/mrx_gestao_access.log
/var/log/nginx/mrx_gestao_error.log
```

**Monitoramento:**
```bash
# Ver logs em tempo real
sudo tail -f /var/log/mrx_gestao/gunicorn_error.log

# Ver status
sudo systemctl status mrx_gestao

# Ver journal
sudo journalctl -u mrx_gestao -f
```

---

## Slide 16: Backup e Recuperação

### Estratégia de Backup

**Backup Automático:**
- Diário do banco de dados
- Retenção de 30 dias
- Armazenamento em /backup

**Backup Manual:**
```bash
sudo cp /var/www/mrx_gestao/mrx.db \
    /backup/mrx_$(date +%Y%m%d).db
```

**Restauração:**
```bash
sudo systemctl stop mrx_gestao
sudo cp /backup/mrx_YYYYMMDD.db \
    /var/www/mrx_gestao/mrx.db
sudo systemctl start mrx_gestao
```

---

## Slide 17: Manutenção - Script Interativo

### maintenance.sh - Menu de Opções

```
1. Status dos serviços
2. Ver logs
3. Fazer backup
4. Restaurar backup
5. Limpar cache e logs
6. Atualizar aplicação
7. Reiniciar serviços
8. Verificar saúde do sistema
9. Renovar certificado SSL
```

**Uso:**
```bash
sudo ./maintenance.sh
```

---

## Slide 18: Atualizar Aplicação

### Atualização em Produção

**Passos:**
```bash
cd /var/www/mrx_gestao

# Fazer backup
sudo cp mrx.db /backup/mrx_before_update.db

# Parar aplicação
sudo systemctl stop mrx_gestao

# Atualizar código
sudo git pull origin main

# Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# Iniciar aplicação
sudo systemctl start mrx_gestao
```

---

## Slide 19: Troubleshooting Rápido

### Problemas Comuns e Soluções

**Erro 502 Bad Gateway:**
```bash
sudo systemctl restart mrx_gestao
```

**Certificado SSL Expirado:**
```bash
sudo certbot renew
sudo systemctl restart nginx
```

**Permissão Negada:**
```bash
sudo chown -R www-data:www-data /var/www/mrx_gestao
```

**Aplicação Não Inicia:**
```bash
sudo journalctl -u mrx_gestao -n 50
```

---

## Slide 20: Performance e Otimizações

### Otimizações Implementadas

**Gunicorn:**
- Workers automáticos (CPU × 2 + 1)
- Connection pooling
- Request timeout

**Nginx:**
- Compressão Gzip
- Cache de arquivos estáticos (30 dias)
- Connection keepalive

**Aplicação:**
- SQLite otimizado
- Índices de banco de dados
- Paginação (10 itens/página)

---

## Slide 21: Checklist de Deploy

### Antes de Fazer Deploy

- [ ] Servidor Ubuntu 20.04+ preparado
- [ ] Domínio registrado e apontando para IP
- [ ] SSH com permissões sudo configurado
- [ ] Portas 80 e 443 abertas
- [ ] Git instalado no servidor
- [ ] Espaço em disco suficiente (5GB+)
- [ ] RAM suficiente (1GB+ recomendado)

### Depois de Fazer Deploy

- [ ] Aplicação acessível em HTTPS
- [ ] Certificado SSL válido
- [ ] Backup configurado
- [ ] Logs sendo registrados
- [ ] Monitoramento ativo
- [ ] Firewall habilitado

---

## Slide 22: Recursos Adicionais

### Scripts Disponíveis

| Script | Função |
|--------|--------|
| **deploy.sh** | Deploy completo (recomendado) |
| **setup_gunicorn.sh** | Setup apenas Gunicorn |
| **setup_nginx.sh** | Setup apenas Nginx |
| **setup_ssl.sh** | Setup apenas SSL/TLS |
| **maintenance.sh** | Manutenção interativa |

### Documentação

- **DEPLOY_GUIDE.md** - Guia completo (7 seções)
- **deploy/README.md** - Quick reference
- **README.md** - Documentação geral

---

## Slide 23: Comandos Úteis

### Gerenciamento de Serviços

```bash
# Iniciar/Parar/Reiniciar
sudo systemctl start mrx_gestao
sudo systemctl stop mrx_gestao
sudo systemctl restart mrx_gestao

# Status
sudo systemctl status mrx_gestao

# Habilitar auto-start
sudo systemctl enable mrx_gestao

# Ver logs
sudo journalctl -u mrx_gestao -f
```

---

## Slide 24: Resumo Executivo

### MRX Gestão - Deploy Pronto para Produção

✅ **Arquitetura**: Nginx + Gunicorn + Flask + SQLite  
✅ **Segurança**: HTTPS, Firewall, Headers, Criptografia  
✅ **Automação**: Deploy em 3 passos, ~5-10 minutos  
✅ **Monitoramento**: Logs, Health checks, Alertas  
✅ **Backup**: Automático, Recuperação fácil  
✅ **Manutenção**: Scripts interativos, Documentação  
✅ **Performance**: Otimizações, Caching, Compressão  

**Tudo pronto para produção!** 🚀

---

## Slide 25: Próximos Passos

### Como Começar

1. **Prepare seu servidor:**
   ```bash
   ssh usuario@seu-servidor.com
   sudo apt-get update && sudo apt-get upgrade -y
   ```

2. **Execute o deploy:**
   ```bash
   cd deploy
   sudo ./deploy.sh seu-dominio.com admin@seu-dominio.com
   ```

3. **Acesse a aplicação:**
   ```
   https://seu-dominio.com
   ```

4. **Monitore:**
   ```bash
   sudo ./maintenance.sh
   ```

---

## Slide 26: Obrigado!

# Obrigado!

## MRX Gestão - Sistema de Gestão Empresarial

**Desenvolvido com ❤️ para MRX do Brasil**

### Contato e Suporte
- Documentação: `/deploy/DEPLOY_GUIDE.md`
- Scripts: `/deploy/*.sh`
- Código: GitHub

**Dúvidas?**
