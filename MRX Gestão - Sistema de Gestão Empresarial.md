# MRX Gestão - Sistema de Gestão Empresarial

Sistema web completo para gestão de funcionários, fornecedores, compras e despesas com autenticação e controle de permissões.

## 🎨 Características

- **Tema Visual**: Verde e preto com identidade visual MRX do Brasil
- **Autenticação**: Login com email e senha criptografada (bcrypt)
- **Controle de Permissões**: 3 papéis (ADMIN, COMPRADOR, VISUALIZADOR)
- **CRUD Completo**: Funcionários, Fornecedores, Compras e Despesas
- **Dashboard**: Resumo com estatísticas e gráficos
- **Validações**: CPF, CNPJ, valores e datas
- **Responsivo**: Interface adaptável para diferentes telas

## 🧩 Stack Técnica

- **Backend**: Python 3.11 + Flask
- **Banco de Dados**: SQLite (arquivo local `mrx.db`)
- **ORM**: SQLAlchemy com Flask-SQLAlchemy
- **Autenticação**: Flask-Login + Bcrypt
- **Migrações**: Flask-Migrate
- **Frontend**: HTML5 + CSS3 + JavaScript
- **Gráficos**: Chart.js

## 📦 Instalação

### 1. Clonar/Baixar o projeto
```bash
cd /home/ubuntu/mrx_gestao_flask
```

### 2. Criar ambiente virtual
```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Inicializar banco de dados
```bash
python app.py
```

Isso criará o arquivo `mrx.db` e o usuário admin padrão.

## 🚀 Executar a aplicação

```bash
source venv/bin/activate
python app.py
```

A aplicação estará disponível em: **http://localhost:5000**

## 🔐 Credenciais Padrão

- **Email**: `admin@mrx.com.br`
- **Senha**: `Admin@123`

## 📊 Estrutura de Pastas

```
mrx_gestao_flask/
├── app.py                 # Aplicação principal
├── config.py              # Configurações
├── models.py              # Modelos de dados
├── auth.py                # Autenticação e decoradores
├── requirements.txt       # Dependências
├── mrx.db                 # Banco de dados SQLite
├── static/
│   ├── css/
│   │   └── style.css      # Estilos (verde/preto)
│   ├── img/
│   │   ├── logo.png       # Logo MRX
│   │   └── escudo.png     # Escudo MRX
│   └── uploads/           # Pasta para uploads
└── templates/
    ├── base.html          # Layout base
    ├── login.html         # Página de login
    ├── dashboard.html     # Dashboard
    ├── funcionarios.html  # CRUD Funcionários
    ├── fornecedores.html  # CRUD Fornecedores
    ├── compras.html       # CRUD Compras
    ├── despesas.html      # CRUD Despesas
    ├── usuarios.html      # CRUD Usuários (Admin)
    └── [templates de edição...]
```

## 🧠 Regras de Negócio

### Papéis e Permissões

| Ação | ADMIN | COMPRADOR | VISUALIZADOR |
|------|-------|-----------|--------------|
| Ver Dashboard | ✓ | ✓ | ✓ |
| Gerenciar Funcionários | ✓ | ✗ | ✗ |
| Gerenciar Usuários | ✓ | ✗ | ✗ |
| Gerenciar Fornecedores | ✓ | ✓ | ✗ |
| Cadastrar Compras | ✓ | ✓ | ✗ |
| Cadastrar Despesas | ✓ | ✓ | ✗ |
| Visualizar Dados | ✓ | ✓ | ✓ |

### Validações

- **CPF/CNPJ**: Validação de formato básico
- **Valores**: Devem ser maiores que zero
- **Datas**: Não podem ser futuras
- **Campos Obrigatórios**: Nome, valor, data

## 📋 Tabelas do Banco de Dados

### Usuários
- `id`, `nome`, `email`, `senha_hash`, `papel`, `ativo`, `criado_em`, `atualizado_em`

### Funcionários
- `id`, `nome`, `cpf`, `telefone`, `cargo`, `criado_em`, `atualizado_em`

### Fornecedores
- `id`, `nome_social`, `cnpj`, `cpf`, `endereco_coleta`, `endereco_emissao`, `telefone`, `email`, `criado_em`, `atualizado_em`

### Compras
- `id`, `fornecedor_id`, `material`, `valor_tabela`, `tipo_coleta`, `observacao`, `comprador_id`, `data`, `criado_em`, `atualizado_em`

### Despesas
- `id`, `nome_social`, `endereco_*`, `telefone`, `email`, `vendedor_id`, `conta`, `agencia`, `chave_pix`, `banco`, `condicao_pagamento`, `forma_pagamento`, `descricao_gasto`, `data`, `valor`, `observacao`, `criado_em`, `atualizado_em`

## 🎨 Paleta de Cores

- **Verde Escuro**: `#004d00`
- **Verde Médio**: `#006600`
- **Verde Claro**: `#00cc00`
- **Preto**: `#000000`
- **Cinza Escuro**: `#1a1a1a`
- **Cinza Médio**: `#333333`
- **Branco**: `#ffffff`

## 🔧 Desenvolvimento

### Adicionar nova rota

```python
@app.route('/nova-pagina')
@login_required_custom
def nova_pagina():
    return render_template('nova_pagina.html')
```

### Adicionar novo modelo

```python
class NovoModelo(db.Model):
    __tablename__ = 'novo_modelo'
    id = db.Column(db.Integer, primary_key=True)
    # ... campos
```

### Usar decoradores de permissão

```python
@admin_required  # Apenas ADMIN
def admin_only():
    pass

@comprador_required  # ADMIN ou COMPRADOR
def comprador_only():
    pass

@role_required(RoleEnum.ADMIN, RoleEnum.COMPRADOR)  # Múltiplos papéis
def multi_role():
    pass
```

## 📝 Notas

- O banco de dados é SQLite local (`mrx.db`)
- Senhas são criptografadas com bcrypt
- Sessões persistem por 7 dias
- Uploads são salvos em `static/uploads/`
- Todos os campos de data/hora usam UTC

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Erro: "Database is locked"
Feche outras conexões com o banco de dados ou reinicie a aplicação.

### Erro: "Permissão negada"
Verifique o papel do usuário logado e as permissões da rota.

## 📞 Suporte

Para dúvidas ou problemas, verifique:
1. Se as dependências estão instaladas (`pip list`)
2. Se o banco de dados foi criado (`ls -la mrx.db`)
3. Se o servidor está rodando (`http://localhost:5000`)

## 📄 Licença

Este projeto é fornecido como está para uso interno da MRX do Brasil.

---

**Desenvolvido com ❤️ para MRX Gestão**
