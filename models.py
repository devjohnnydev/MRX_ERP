from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

db = SQLAlchemy()

class RoleEnum(enum.Enum):
    """Enumeração de papéis de usuário."""
    ADMIN = "ADMIN"
    COMPRADOR = "COMPRADOR"
    VISUALIZADOR = "VISUALIZADOR"

class Usuario(UserMixin, db.Model):
    """Modelo de usuário com autenticação."""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    papel = db.Column(db.Enum(RoleEnum), default=RoleEnum.VISUALIZADOR, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    despesas = db.relationship('Despesa', backref='vendedor', lazy=True, foreign_keys='Despesa.vendedor_id')
    compras = db.relationship('Compra', backref='comprador', lazy=True, foreign_keys='Compra.comprador_id')
    comissoes = db.relationship('ComissaoComprador', backref='comprador', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Define a senha com hash seguro."""
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica a senha contra o hash."""
        return check_password_hash(self.senha_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Funcionario(db.Model):
    """Modelo de funcionário."""
    __tablename__ = 'funcionarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(20))
    cargo = db.Column(db.String(100))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Funcionario {self.nome}>'

class Fornecedor(db.Model):
    """Modelo de fornecedor."""
    __tablename__ = 'fornecedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_social = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=True, index=True)
    cpf = db.Column(db.String(14), unique=True, nullable=True, index=True)
    endereco_coleta = db.Column(db.String(255))
    endereco_emissao = db.Column(db.String(255))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    # Dados bancários
    banco = db.Column(db.String(100))
    agencia = db.Column(db.String(10))
    conta = db.Column(db.String(20))
    chave_pix = db.Column(db.String(255))
    tipo_conta = db.Column(db.String(20))  # 'corrente' ou 'poupança'
    # Preço máximo para aprovação automática
    preco_maximo_automatico = db.Column(db.Float, default=1000.0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    compras = db.relationship('Compra', backref='fornecedor', lazy=True, cascade='all, delete-orphan')
    tabela_precos = db.relationship('TabelaPreco', backref='fornecedor', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Fornecedor {self.nome_social}>'

class TabelaPreco(db.Model):
    """Modelo de tabela de preços por fornecedor."""
    __tablename__ = 'tabela_precos'
    
    id = db.Column(db.Integer, primary_key=True)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    nome_item = db.Column(db.String(255), nullable=False)  # Nome da peça/item
    codigo_barras = db.Column(db.String(255), unique=True, nullable=True, index=True)  # Código de barras/QR
    preco_por_kg = db.Column(db.Float, nullable=False)  # Preço por quilo
    unidade = db.Column(db.String(20), default='kg')  # Unidade de medida
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TabelaPreco {self.nome_item}>'

class Compra(db.Model):
    """Modelo de compra com aprovação e comissão."""
    __tablename__ = 'compras'
    
    id = db.Column(db.Integer, primary_key=True)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    tabela_preco_id = db.Column(db.Integer, db.ForeignKey('tabela_precos.id'), nullable=False)
    quantidade_kg = db.Column(db.Float, nullable=False)  # Quantidade em quilos
    preco_unitario = db.Column(db.Float, nullable=False)  # Preço por kg no momento da compra
    valor_total = db.Column(db.Float, nullable=False)  # quantidade_kg * preco_unitario
    preco_maximo = db.Column(db.Float, nullable=False)  # Preço máximo do fornecedor
    status_preco = db.Column(db.String(20), default='igual')  # 'menor', 'igual', 'maior'
    status_aprovacao = db.Column(db.String(20), default='pendente')  # 'pendente', 'aprovada', 'rejeitada'
    tipo_coleta = db.Column(db.String(20), nullable=False)  # 'coleta' ou 'entrega'
    observacao = db.Column(db.Text)
    comprador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    # Geolocalização
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    endereco_coleta = db.Column(db.String(255))
    # Comissão
    comissao_percentual = db.Column(db.Float, default=0.0)  # Percentual de comissão do comprador
    valor_comissao = db.Column(db.Float, default=0.0)  # Valor calculado da comissão
    data = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    tabela_preco = db.relationship('TabelaPreco', backref='compras')
    
    def __repr__(self):
        return f'<Compra {self.id}>'

class ComissaoComprador(db.Model):
    """Modelo de comissão do comprador na rua."""
    __tablename__ = 'comissao_comprador'
    
    id = db.Column(db.Integer, primary_key=True)
    comprador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    percentual_comissao = db.Column(db.Float, default=0.0)  # Percentual de comissão (ex: 5.0 para 5%)
    valor_total_compras = db.Column(db.Float, default=0.0)  # Valor total de compras do mês
    valor_comissao_total = db.Column(db.Float, default=0.0)  # Valor total de comissão a pagar
    mes_referencia = db.Column(db.String(7))  # Formato: YYYY-MM
    status_pagamento = db.Column(db.String(20), default='pendente')  # 'pendente', 'pago'
    data_pagamento = db.Column(db.DateTime)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ComissaoComprador {self.comprador_id}>'

class Despesa(db.Model):
    """Modelo de despesa adicional."""
    __tablename__ = 'despesas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_social = db.Column(db.String(200), nullable=False)
    endereco_rua = db.Column(db.String(255))
    endereco_numero = db.Column(db.String(20))
    endereco_cidade = db.Column(db.String(100))
    endereco_cep = db.Column(db.String(10))
    endereco_estado = db.Column(db.String(2))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    vendedor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    conta = db.Column(db.String(20))
    agencia = db.Column(db.String(10))
    chave_pix = db.Column(db.String(255))
    banco = db.Column(db.String(100))
    condicao_pagamento = db.Column(db.String(20))  # 'a_vista' ou 'parcelado'
    forma_pagamento = db.Column(db.String(20))  # 'cheque', 'pix', 'ted', 'boleto'
    descricao_gasto = db.Column(db.Text)
    data = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    observacao = db.Column(db.Text)
    comprovante = db.Column(db.String(255))  # Caminho do arquivo de comprovante
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Despesa {self.nome_social}>'
