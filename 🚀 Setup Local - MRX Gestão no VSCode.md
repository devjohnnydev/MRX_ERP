# 🚀 Setup Local - MRX Gestão no VSCode

Guia completo para configurar e executar o projeto MRX Gestão localmente no VSCode.

---

## 📋 Pré-requisitos

- **Python 3.11+** instalado
- **Git** instalado
- **VSCode** instalado
- **Extensões VSCode** (recomendadas):
  - Python (Microsoft)
  - Pylance
  - Flask Snippets
  - SQLite (alexcvzz)

---

## 🔧 Passo 1: Clonar o Repositório

```bash
# Clonar o projeto
git clone <seu-repositorio>
cd mrx_gestao_flask

# Ou, se já tem o projeto localmente
cd /caminho/para/mrx_gestao_flask
```

---

## 🐍 Passo 2: Criar Ambiente Virtual

### Windows

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate
```

### macOS/Linux

```bash
# Criar ambiente virtual
python3.11 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

---

## 📦 Passo 3: Instalar Dependências

```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências do projeto
pip install -r requirements.txt
```

**Dependências principais:**
- Flask 3.1.2
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Flask-Migrate 4.0.5
- Werkzeug 3.0.1
- Pillow 10.1.0
- ReportLab 4.0.9
- Argon2-CFfi 23.2.0

---

## 🗄️ Passo 4: Inicializar Banco de Dados

```bash
# Criar banco de dados e tabelas
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ Banco de dados criado!')"

# Ou, se usar Flask-Migrate
flask db upgrade
```

---

## 🎯 Passo 5: Configurar VSCode

### 1. Abrir Pasta no VSCode

```bash
code .
```

### 2. Selecionar Interpretador Python

1. Pressione `Ctrl + Shift + P` (ou `Cmd + Shift + P` no Mac)
2. Digite: `Python: Select Interpreter`
3. Escolha: `./venv/bin/python` (ou `venv\Scripts\python.exe` no Windows)

### 3. Verificar Configurações

O arquivo `.vscode/settings.json` já está configurado com:
- Formatação automática com Black
- Linting com Pylint
- Rulers em 88 e 120 caracteres
- Exclusão de `__pycache__` e `.pyc`

---

## ▶️ Passo 6: Executar a Aplicação

### Opção 1: Debug no VSCode

1. Pressione `F5` ou vá para **Run → Start Debugging**
2. Selecione **Flask** na lista
3. A aplicação iniciará em `http://localhost:5000`

### Opção 2: Terminal

```bash
# Ativar ambiente virtual (se não estiver ativo)
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows

# Executar aplicação
python app.py

# Ou com Flask CLI
flask run
```

---

## 🌐 Acessar a Aplicação

1. Abra o navegador
2. Acesse: **http://localhost:5000**
3. Faça login com:
   - **Email**: `admin@mrx.com.br`
   - **Senha**: `Admin@123`

---

## 📱 Testar Scanner de Peças

### 1. Cadastrar Fornecedor

1. Acesse **Fornecedores**
2. Crie um novo fornecedor
3. Acesse **Dados Bancários** e configure

### 2. Criar Tabela de Preços

1. Clique em **Tabela de Preços** do fornecedor
2. Adicione itens com:
   - **Nome**: Ex: "Papel Branco A4"
   - **Código de Barras**: Ex: "123456789"
   - **Preço/kg**: Ex: "10.50"

### 3. Testar Scanner

1. Acesse **Compra com Scanner**
2. Selecione o fornecedor
3. Digite o código de barras (ex: `123456789`)
4. Pressione ENTER
5. A peça será adicionada ao carrinho automaticamente

### 4. Verificar Geolocalização

- A localização atual será capturada automaticamente
- O endereço será obtido via OpenStreetMap (Nominatim)
- Coordenadas e endereço aparecem no topo da página

---

## 🐛 Debug e Troubleshooting

### Problema: "ModuleNotFoundError"

```bash
# Solução: Reinstalar dependências
pip install --force-reinstall -r requirements.txt
```

### Problema: "Port 5000 already in use"

```bash
# Solução: Usar porta diferente
flask run --port 5001

# Ou no app.py, mudar:
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Problema: Banco de dados não criado

```bash
# Solução: Deletar e recriar
rm mrx.db  # ou mrx.db no Windows
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Problema: Geolocalização não funciona

- Certifique-se de que está usando **HTTPS** ou **localhost**
- Navegadores bloqueiam geolocalização em HTTP (exceto localhost)
- Permita acesso à localização quando o navegador pedir

---

## 📝 Estrutura do Projeto

```
mrx_gestao_flask/
├── app.py                    # Aplicação principal
├── models.py                 # Modelos SQLAlchemy
├── config.py                 # Configurações
├── auth.py                   # Autenticação e decoradores
├── extras.py                 # Funções auxiliares (PDF, filtros)
├── requirements.txt          # Dependências
├── .gitignore               # Arquivos ignorados
├── .vscode/                 # Configurações VSCode
│   ├── settings.json        # Configurações do editor
│   └── launch.json          # Configurações de debug
├── static/                  # Arquivos estáticos
│   ├── css/
│   │   └── style.css        # Estilos (verde/preto)
│   ├── js/
│   │   └── scanner.js       # Scanner de peças
│   └── img/                 # Imagens (logos MRX)
├── templates/               # Templates HTML
│   ├── base.html            # Layout base
│   ├── login.html           # Login
│   ├── dashboard.html       # Dashboard
│   ├── compra_scanner.html  # Scanner de peças
│   ├── compras.html         # CRUD Compras
│   ├── fornecedores.html    # CRUD Fornecedores
│   ├── tabela_precos.html   # Tabela de preços
│   ├── comissoes.html       # Comissões
│   └── ...                  # Outros templates
├── venv/                    # Ambiente virtual (não commitar)
├── mrx.db                   # Banco de dados SQLite (não commitar)
└── README.md                # Documentação

```

---

## 🔑 Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto (não será commitado):

```bash
FLASK_ENV=development
FLASK_DEBUG=1
DATABASE_URL=sqlite:///mrx.db
SECRET_KEY=sua-chave-secreta-aqui
```

No `config.py`, carregue com:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

## 🧪 Testes (Opcional)

```bash
# Instalar pytest
pip install pytest pytest-flask

# Executar testes
pytest

# Com cobertura
pytest --cov=.
```

---

## 📚 Recursos Úteis

- **Flask Docs**: https://flask.palletsprojects.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Bootstrap 5**: https://getbootstrap.com/
- **Geolocation API**: https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API
- **OpenStreetMap Nominatim**: https://nominatim.org/

---

## 🚀 Deploy (Produção)

Para deploy em produção, veja: `deploy/DEPLOY_GUIDE.md`

---

## 💡 Dicas de Desenvolvimento

### 1. Hot Reload

O Flask com `debug=True` recarrega automaticamente ao salvar arquivos.

### 2. Breakpoints no VSCode

```python
# Adicione em qualquer lugar do código
breakpoint()  # Pausa a execução
```

### 3. Console Python Interativo

```bash
# Abrir shell Flask
flask shell

# Exemplo de uso
>>> from models import *
>>> db.session.query(Usuario).all()
```

### 4. Verificar Logs

Os logs aparecem no terminal onde você executou `python app.py`.

---

## ✅ Checklist de Setup

- [ ] Python 3.11+ instalado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado (`venv/`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Banco de dados inicializado (`mrx.db` criado)
- [ ] Interpretador Python selecionado no VSCode
- [ ] Aplicação rodando em `http://localhost:5000`
- [ ] Login funcionando (admin@mrx.com.br / Admin@123)
- [ ] Scanner de peças testado
- [ ] Geolocalização funcionando

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique se o ambiente virtual está ativado
2. Verifique se as dependências estão instaladas
3. Verifique os logs no terminal
4. Limpe cache: `rm -rf __pycache__ .pytest_cache`
5. Recrie o banco de dados se necessário

---

**Versão**: 2.0  
**Data**: 2025-11-08  
**Status**: ✅ Pronto para Desenvolvimento Local
