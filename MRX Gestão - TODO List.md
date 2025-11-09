# MRX Gestão - TODO List

## ✅ Funcionalidades Implementadas

### Backend
- [x] Configuração Flask com SQLAlchemy
- [x] Modelos de dados (Usuários, Funcionários, Fornecedores, Compras, Despesas)
- [x] Autenticação com login/senha (hash seguro)
- [x] Sistema de roles (ADMIN, COMPRADOR, VISUALIZADOR)
- [x] Decoradores de permissão (@admin_required, @comprador_required)
- [x] Validações (CPF, CNPJ, valores, datas)

### Rotas CRUD
- [x] Funcionários (CRUD completo - ADMIN)
- [x] Fornecedores (CRUD completo - ADMIN/COMPRADOR)
- [x] Compras (CRUD completo - ADMIN/COMPRADOR)
- [x] Despesas (CRUD completo - ADMIN/COMPRADOR)
- [x] Usuários (CRUD completo - ADMIN)
- [x] Login/Logout

### Frontend
- [x] Template base com navbar e sidebar
- [x] Página de login
- [x] Dashboard com estatísticas
- [x] Gráficos com Chart.js (compras e despesas por mês)
- [x] Templates CRUD para todas as entidades
- [x] Paginação em listas
- [x] Alertas flash (sucesso, erro, aviso)
- [x] Tratamento de erros (404, 403, 500)

### Estilos
- [x] CSS com tema verde (#006600) e preto (#000000)
- [x] Design responsivo
- [x] Identidade visual MRX do Brasil
- [x] Logos MRX (escudo e logo)
- [x] Tabelas estilizadas
- [x] Formulários com validação visual
- [x] Botões com hover effects

### Extras
- [x] Exportação de compras em PDF
- [x] Exportação de despesas em PDF
- [x] Funções de filtro avançado
- [x] Resumo de períodos
- [x] Relatórios com totalizadores

### Deploy em Produção
- [x] Script de deploy automático (deploy.sh)
- [x] Setup Gunicorn (setup_gunicorn.sh)
- [x] Setup Nginx (setup_nginx.sh)
- [x] Setup SSL/TLS (setup_ssl.sh)
- [x] Script de manutenção (maintenance.sh)
- [x] Arquivo de serviço systemd
- [x] Configuração Nginx completa
- [x] Guia de deploy (DEPLOY_GUIDE.md)
- [x] README para pasta deploy

## 📋 Estrutura de Arquivos

```
mrx_gestao_flask/
├── app.py                 # Aplicação principal com todas as rotas
├── models.py              # Modelos SQLAlchemy
├── auth.py                # Autenticação e decoradores
├── config.py              # Configurações
├── extras.py              # Funções extras (PDF, filtros)
├── requirements.txt       # Dependências Python
├── README.md              # Documentação
├── todo.md                # Este arquivo
├── mrx.db                 # Banco de dados SQLite
├── deploy/
│   ├── deploy.sh          # Script de deploy completo
│   ├── setup_gunicorn.sh  # Setup Gunicorn
│   ├── setup_nginx.sh     # Setup Nginx
│   ├── setup_ssl.sh       # Setup SSL/TLS
│   ├── maintenance.sh     # Script de manutenção
│   ├── mrx_gestao.service # Arquivo de serviço systemd
│   ├── nginx.conf         # Configuração Nginx
│   ├── DEPLOY_GUIDE.md    # Guia de deploy
│   └── README.md          # README do deploy
├── static/
│   ├── css/
│   │   └── style.css      # Estilos CSS (verde/preto)
│   ├── img/
│   │   ├── logo.png       # Logo MRX
│   │   └── escudo.png     # Escudo MRX
│   └── uploads/           # Pasta para uploads
└── templates/
    ├── base.html          # Layout base
    ├── login.html         # Login
    ├── dashboard.html     # Dashboard
    ├── funcionarios.html  # CRUD Funcionários
    ├── editar_funcionario.html
    ├── fornecedores.html  # CRUD Fornecedores
    ├── editar_fornecedor.html
    ├── compras.html       # CRUD Compras
    ├── editar_compra.html
    ├── despesas.html      # CRUD Despesas
    ├── editar_despesa.html
    ├── usuarios.html      # CRUD Usuários
    ├── editar_usuario.html
    ├── 404.html           # Erro 404
    ├── 403.html           # Erro 403
    └── 500.html           # Erro 500
```

## 🚀 Como Usar

### Instalação Local
```bash
cd /home/ubuntu/mrx_gestao_flask
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Executar Desenvolvimento
```bash
python app.py
```

Acesse: http://localhost:5000

### Deploy em Produção
```bash
cd deploy
sudo ./deploy.sh seu-dominio.com admin@seu-dominio.com
```

### Credenciais Padrão
- Email: `admin@mrx.com.br`
- Senha: `Admin@123`

## 📊 Funcionalidades por Papel

### ADMIN
- Ver Dashboard
- Gerenciar Funcionários (C/R/U/D)
- Gerenciar Usuários (C/R/U/D)
- Gerenciar Fornecedores (C/R/U/D)
- Cadastrar Compras (C/R/U/D)
- Cadastrar Despesas (C/R/U/D)
- Exportar relatórios em PDF

### COMPRADOR
- Ver Dashboard
- Gerenciar Fornecedores (C/R/U/D)
- Cadastrar Compras (C/R/U/D)
- Cadastrar Despesas (C/R/U/D)
- Exportar relatórios em PDF

### VISUALIZADOR
- Ver Dashboard (somente leitura)
- Visualizar dados (sem edição)

## 🔧 Tecnologias Utilizadas

- **Backend**: Python 3.11 + Flask 3.1.2
- **Banco de Dados**: SQLite
- **ORM**: SQLAlchemy 2.0.44
- **Autenticação**: Flask-Login + Werkzeug
- **Criptografia**: Argon2-CFfi
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Gráficos**: Chart.js
- **PDF**: ReportLab
- **Imagens**: Pillow
- **Servidor**: Gunicorn
- **Proxy**: Nginx
- **SSL/TLS**: Let's Encrypt + Certbot

## 📝 Notas

- Todas as senhas são criptografadas com hash seguro
- Validações de CPF/CNPJ implementadas
- Datas são armazenadas em UTC
- Paginação padrão: 10 itens por página
- Sessões persistem por 7 dias
- Banco de dados SQLite local (sem necessidade de servidor externo)

## 🎯 Status do Projeto

**Status**: ✅ **COMPLETO E PRONTO PARA PRODUÇÃO**

Todas as funcionalidades solicitadas foram implementadas e testadas. O sistema está pronto para:
- ✅ Uso em desenvolvimento
- ✅ Deploy em produção com Gunicorn + Nginx
- ✅ Backup e recuperação
- ✅ Monitoramento e manutenção
- ✅ Renovação automática de certificado SSL

## 📚 Documentação

- `README.md` - Documentação geral do projeto
- `deploy/DEPLOY_GUIDE.md` - Guia completo de deploy
- `deploy/README.md` - Documentação dos scripts de deploy

## 🔐 Segurança em Produção

✅ HTTPS com Let's Encrypt  
✅ Headers de segurança (HSTS, CSP, X-Frame-Options)  
✅ Senhas com hash Argon2  
✅ CSRF protection  
✅ SQL injection prevention (SQLAlchemy)  
✅ XSS protection  
✅ Rate limiting (Nginx)  
✅ Firewall (UFW)  

---

**Última atualização**: 08/11/2025
