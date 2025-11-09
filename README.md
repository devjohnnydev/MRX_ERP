
# 💼 MRX Gestão ERP  
**Sistema de Gestão Empresarial – Flask + SQLAlchemy + Docker**

<div align="center">
  
![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black.svg?logo=flask)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

</div>

---

## 🧭 Sobre o Projeto

**MRX Gestão ERP** é um sistema completo de gestão empresarial desenvolvido em **Flask** com **SQLAlchemy**, voltado para controle de **usuários**, **funcionários**, **fornecedores**, **compras** e **despesas**.  
Ideal para pequenas e médias empresas, com estrutura escalável e suporte a **deploy com Docker, Gunicorn e Nginx**.

> 💡 O projeto foi criado para fins acadêmicos e empresariais, com arquitetura profissional e scripts de automação de deploy.

---

## 🖼️ Demonstração

> Acesso padrão (ambiente local):
> - **Email:** `admin@mrx.com.br`  
> - **Senha:** `Admin@123`

<img src="static/img/escudo.png" width="120" alt="MRX Escudo" />
<img src="static/img/logo.png" width="200" alt="MRX Logo" />

---

## ⚙️ Principais Funcionalidades

✅ Login / Logout com sessão  
✅ Dashboard com visão geral  
✅ CRUD completo de:
  - Usuários
  - Funcionários
  - Fornecedores
  - Compras
  - Despesas  
✅ Estrutura modular com Blueprints  
✅ Templates Jinja2 + CSS customizado  
✅ Scripts automáticos de Deploy (Linux)  
✅ Compatível com Docker e PostgreSQL  

---

## 🧱 Stack Utilizada

| Categoria | Tecnologias |
|------------|--------------|
| **Backend** | Flask, SQLAlchemy, Python 3.12 |
| **Frontend** | HTML5, CSS3, Jinja2 |
| **Banco de Dados** | SQLite (dev) / PostgreSQL (prod) |
| **Infraestrutura** | Docker, Gunicorn, Nginx |
| **Deploy Automático** | Shell Scripts + Systemd |
| **Dev Tools** | Makefile, PowerShell Automation |

---

## 🗂️ Estrutura do Projeto

```bash
MRX_ERP/
├── app.py
├── auth.py
├── config.py
├── models.py
├── requirements.txt
├── static/
│   ├── css/style.css
│   └── img/{logo.png, escudo.png}
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── usuarios.html, funcionarios.html, fornecedores.html
│   ├── compras.html, despesas.html
├── instance/ (criado automaticamente)
├── deploy.sh, maintenance.sh
├── setup_gunicorn.sh, setup_nginx.sh, setup_ssl.sh
├── mrx_gestao.service, nginx.conf
├── docker-compose.yml, compose.override.yml
├── Makefile, make.ps1
└── push_to_github.{sh,ps1}
````

---

## 🚀 Como Rodar Localmente

### 1️⃣ Clonar o projeto

```bash
git clone https://github.com/devjohnnydev/MRX_ERP.git
cd MRX_ERP
```

### 2️⃣ Criar ambiente virtual

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS**

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Instalar dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Rodar aplicação

```bash
python app.py
```

> Acesse: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🧩 Variáveis de Ambiente

Crie um arquivo `.env` na raiz (para uso local ou Docker):

```bash
SECRET_KEY=troque-esta-chave
FLASK_ENV=development
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mrx_db
DB_HOST=db
DB_PORT=5432
DATABASE_URL=postgresql://postgres:postgres@db:5432/mrx_db
```

---

## 🐳 Rodando com Docker (opcional)

### Subir containers

```bash
docker compose up -d
```

### Com hot-reload (modo dev)

```bash
docker compose -f docker-compose.yml -f compose.override.yml up --build
```

### Parar

```bash
docker compose down
```

---

## ⚡ Automação com Make / PowerShell

**Linux/macOS**

```bash
make env      # cria .env padrão
make init     # build + up + logs (modo dev)
make logs     # ver logs do container
make down     # parar containers
```

**Windows PowerShell**

```powershell
./make.ps1 env
./make.ps1 init
./make.ps1 logs
./make.ps1 down
```

---

## 🔁 Envio para o GitHub via Terminal

**PowerShell (Windows):**

```powershell
.\push_to_github.ps1 -Message "feat: atualização geral"
```

**Bash (Linux/macOS):**

```bash
./push_to_github.sh "https://github.com/devjohnnydev/MRX_ERP.git" main "feat: atualização geral"
```

---

## 🧯 Solução de Problemas Comuns

| Erro                                   | Solução                                                         |
| -------------------------------------- | --------------------------------------------------------------- |
| `TemplateNotFound: login.html`         | Verifique se a pasta `templates/` está na raiz.                 |
| `404 /static/...`                      | Confirme se os arquivos estão em `static/css/` e `static/img/`. |
| `src refspec main does not match any`  | Crie branch main com `git branch -M main`.                      |
| `warning: LF will be replaced by CRLF` | Execute `git config --global core.autocrlf true`.               |

---

## 🔐 Produção (Linux)

O deploy completo pode ser feito com:

```bash
./deploy.sh
```

Ou manualmente com:

1. `setup_gunicorn.sh` → instala Gunicorn e cria serviço Systemd
2. `setup_nginx.sh` → cria proxy reverso
3. `setup_ssl.sh` → configura HTTPS via Let’s Encrypt

---

## 👤 Autor

**Johnny Braga de Oliveira**
Professor de Tecnologia da Informação – SENAI Morvan Figueiredo
💼 Especialista em Cloud Computing, Back-End e DevOps

📧 [johnnyb@example.com](mailto:johnnyb@example.com)
🌐 [LinkedIn](https://linkedin.com/in/johnnybraga) | [GitHub](https://github.com/devjohnnydev)

---

## 🧾 Licença

Este projeto é distribuído sob a **Licença MIT**.
Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 💬 Contribuindo

1. Faça um **fork** do projeto
2. Crie uma branch: `git checkout -b minha-feature`
3. Commit suas mudanças: `git commit -m 'feat: minha nova feature'`
4. Envie: `git push origin minha-feature`
5. Abra um **Pull Request**

---

<div align="center">

🧠 *“Transforme processos em soluções inteligentes — MRX Gestão.”* <br>
💻 Desenvolvido com dedicação por **Professor Johnny Braga**

</div>
```

---


