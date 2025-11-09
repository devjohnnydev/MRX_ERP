import os
import json
from sqlalchemy import extract
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timedelta
from io import BytesIO
from config import config
from models import db, Usuario, RoleEnum, Funcionario, Fornecedor, Compra, Despesa, TabelaPreco, ComissaoComprador
from auth import (
    login_required_custom, role_required, admin_required, comprador_required,
    validar_cpf, validar_cnpj, formatar_cpf, formatar_cnpj
)
from extras import (
    gerar_relatorio_compras_pdf, gerar_relatorio_despesas_pdf,
    filtrar_compras, filtrar_despesas, obter_resumo_periodo
)

# Inicializar aplicação
app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Inicializar extensões
db.init_app(app)
migrate = Migrate(app, db)
CORS(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# ==================== ROTAS DE API ====================

@app.route('/api/validar-peca', methods=['POST'])
@comprador_required
def api_validar_peca():
    """API para validar peça por código de barras."""
    dados = request.get_json()
    codigo_barras = dados.get('codigo_barras', '').strip()
    fornecedor_id = dados.get('fornecedor_id', type=int)
    
    if not codigo_barras or not fornecedor_id:
        return jsonify({'sucesso': False, 'mensagem': 'Código ou fornecedor inválido'}), 400
    
    # Buscar peça no banco de dados
    peca = TabelaPreco.query.filter_by(
        codigo_barras=codigo_barras,
        fornecedor_id=fornecedor_id,
        ativo=True
    ).first()
    
    if not peca:
        return jsonify({'sucesso': False, 'mensagem': 'Peça não encontrada'}), 404
    
    return jsonify({
        'sucesso': True,
        'peca': {
            'id': peca.id,
            'nome_item': peca.nome_item,
            'codigo_barras': peca.codigo_barras,
            'preco_por_kg': peca.preco_por_kg,
            'unidade': peca.unidade,
            'descricao': peca.descricao
        }
    }), 200

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        
        if not email or not senha:
            flash('Email e senha são obrigatórios.', 'danger')
            return redirect(url_for('login'))
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(senha) and usuario.ativo:
            login_user(usuario, remember=request.form.get('lembrar'))
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos, ou usuário inativo.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required_custom
def logout():
    """Rota de logout."""
    logout_user()
    flash('Você foi desconectado com sucesso.', 'info')
    return redirect(url_for('login'))

# ==================== ROTA DE DASHBOARD ====================

@app.route('/')
@app.route('/dashboard')
@login_required_custom
def dashboard():
    """Dashboard com resumo e gráficos."""
    # Dados para o dashboard
    total_funcionarios = Funcionario.query.count()
    total_fornecedores = Fornecedor.query.count()
    total_compras = Compra.query.count()
    total_despesas = Despesa.query.count()
    
    # Valor total de compras
    compras_valor = db.session.query(db.func.sum(Compra.valor_total)).scalar() or 0
    
    # Valor total de despesas
    despesas_valor = db.session.query(db.func.sum(Despesa.valor)).scalar() or 0
    
    # Últimas compras
    ultimas_compras = Compra.query.order_by(Compra.data.desc()).limit(5).all()
    
    # Últimas despesas
    ultimas_despesas = Despesa.query.order_by(Despesa.data.desc()).limit(5).all()
    
    # Dados para gráfico de compras por mês
    hoje = datetime.utcnow()
    seis_meses_atras = hoje - timedelta(days=180)
    
    compras_query = db.session.query(
        db.func.strftime('%Y-%m', Compra.data).label('mes'),
        db.func.sum(Compra.valor_total).label('total')
    ).filter(Compra.data >= seis_meses_atras).group_by('mes').all()
    
    # Converter para dicionário para serialização JSON
    compras_por_mes = [{'mes': row[0], 'total': float(row[1]) if row[1] else 0} for row in compras_query]
    
    despesas_query = db.session.query(
        db.func.strftime('%Y-%m', Despesa.data).label('mes'),
        db.func.sum(Despesa.valor).label('total')
    ).filter(Despesa.data >= seis_meses_atras).group_by('mes').all()
    
    # Converter para dicionário para serialização JSON
    despesas_por_mes = [{'mes': row[0], 'total': float(row[1]) if row[1] else 0} for row in despesas_query]
    
    return render_template('dashboard.html',
        total_funcionarios=total_funcionarios,
        total_fornecedores=total_fornecedores,
        total_compras=total_compras,
        total_despesas=total_despesas,
        compras_valor=compras_valor,
        despesas_valor=despesas_valor,
        ultimas_compras=ultimas_compras,
        ultimas_despesas=ultimas_despesas,
        compras_por_mes=compras_por_mes,
        despesas_por_mes=despesas_por_mes
    )

# ==================== ROTAS CRUD - FUNCIONÁRIOS ====================

@app.route('/funcionarios', methods=['GET', 'POST'])
@admin_required
def funcionarios():
    """CRUD de funcionários."""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cpf = request.form.get('cpf', '').strip()
        telefone = request.form.get('telefone', '').strip()
        cargo = request.form.get('cargo', '').strip()
        
        if not nome or not cpf:
            flash('Nome e CPF são obrigatórios.', 'danger')
            return redirect(url_for('funcionarios'))
        
        if not validar_cpf(cpf):
            flash('CPF inválido.', 'danger')
            return redirect(url_for('funcionarios'))
        
        if Funcionario.query.filter_by(cpf=cpf).first():
            flash('CPF já cadastrado.', 'danger')
            return redirect(url_for('funcionarios'))
        
        funcionario = Funcionario(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            cargo=cargo
        )
        db.session.add(funcionario)
        db.session.commit()
        flash(f'Funcionário {nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('funcionarios'))
    
    page = request.args.get('page', 1, type=int)
    funcionarios_list = Funcionario.query.paginate(page=page, per_page=10)
    return render_template('funcionarios.html', funcionarios=funcionarios_list)

@app.route('/funcionarios/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_funcionario(id):
    """Editar funcionário."""
    funcionario = Funcionario.query.get_or_404(id)
    
    if request.method == 'POST':
        funcionario.nome = request.form.get('nome', '').strip()
        funcionario.telefone = request.form.get('telefone', '').strip()
        funcionario.cargo = request.form.get('cargo', '').strip()
        
        db.session.commit()
        flash('Funcionário atualizado com sucesso!', 'success')
        return redirect(url_for('funcionarios'))
    
    return render_template('editar_funcionario.html', funcionario=funcionario)

@app.route('/funcionarios/<int:id>/deletar', methods=['POST'])
@admin_required
def deletar_funcionario(id):
    """Deletar funcionário."""
    funcionario = Funcionario.query.get_or_404(id)
    nome = funcionario.nome
    db.session.delete(funcionario)
    db.session.commit()
    flash(f'Funcionário {nome} deletado com sucesso!', 'success')
    return redirect(url_for('funcionarios'))

# ==================== ROTAS CRUD - FORNECEDORES ====================

@app.route('/fornecedores', methods=['GET', 'POST'])
@comprador_required
def fornecedores():
    """CRUD de fornecedores."""
    if request.method == 'POST':
        nome_social = request.form.get('nome_social', '').strip()
        cnpj = request.form.get('cnpj', '').strip()
        cpf = request.form.get('cpf', '').strip()
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip()
        endereco_coleta = request.form.get('endereco_coleta', '').strip()
        endereco_emissao = request.form.get('endereco_emissao', '').strip()
        
        if not nome_social:
            flash('Nome social é obrigatório.', 'danger')
            return redirect(url_for('fornecedores'))
        
        if cnpj and not validar_cnpj(cnpj):
            flash('CNPJ inválido.', 'danger')
            return redirect(url_for('fornecedores'))
        
        if cpf and not validar_cpf(cpf):
            flash('CPF inválido.', 'danger')
            return redirect(url_for('fornecedores'))
        
        fornecedor = Fornecedor(
            nome_social=nome_social,
            cnpj=cnpj if cnpj else None,
            cpf=cpf if cpf else None,
            telefone=telefone,
            email=email,
            endereco_coleta=endereco_coleta,
            endereco_emissao=endereco_emissao
        )
        db.session.add(fornecedor)
        db.session.commit()
        flash(f'Fornecedor {nome_social} cadastrado com sucesso!', 'success')
        return redirect(url_for('fornecedores'))
    
    page = request.args.get('page', 1, type=int)
    fornecedores_list = Fornecedor.query.paginate(page=page, per_page=10)
    return render_template('fornecedores.html', fornecedores=fornecedores_list)

@app.route('/fornecedores/<int:id>/editar', methods=['GET', 'POST'])
@comprador_required
def editar_fornecedor(id):
    """Editar fornecedor."""
    fornecedor = Fornecedor.query.get_or_404(id)
    
    if request.method == 'POST':
        fornecedor.nome_social = request.form.get('nome_social', '').strip()
        fornecedor.telefone = request.form.get('telefone', '').strip()
        fornecedor.email = request.form.get('email', '').strip()
        fornecedor.endereco_coleta = request.form.get('endereco_coleta', '').strip()
        fornecedor.endereco_emissao = request.form.get('endereco_emissao', '').strip()
        
        db.session.commit()
        flash('Fornecedor atualizado com sucesso!', 'success')
        return redirect(url_for('fornecedores'))
    
    return render_template('editar_fornecedor.html', fornecedor=fornecedor)

@app.route('/fornecedores/<int:id>/deletar', methods=['POST'])
@comprador_required
def deletar_fornecedor(id):
    """Deletar fornecedor."""
    fornecedor = Fornecedor.query.get_or_404(id)
    nome = fornecedor.nome_social
    db.session.delete(fornecedor)
    db.session.commit()
    flash(f'Fornecedor {nome} deletado com sucesso!', 'success')
    return redirect(url_for('fornecedores'))

# ==================== ROTAS CRUD - TABELA DE PREÇOS ====================

@app.route('/tabela-precos/<int:fornecedor_id>', methods=['GET', 'POST'])
@comprador_required
def tabela_precos(fornecedor_id):
    """Gerenciar tabela de preços de um fornecedor."""
    fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
    
    if request.method == 'POST':
        nome_item = request.form.get('nome_item', '').strip()
        preco_por_kg = request.form.get('preco_por_kg', type=float)
        descricao = request.form.get('descricao', '').strip()
        
        if not nome_item or not preco_por_kg:
            flash('Nome do item e preço por kg são obrigatórios.', 'danger')
            return redirect(url_for('tabela_precos', fornecedor_id=fornecedor_id))
        
        if preco_por_kg <= 0:
            flash('Preço deve ser maior que zero.', 'danger')
            return redirect(url_for('tabela_precos', fornecedor_id=fornecedor_id))
        
        tabela = TabelaPreco(
            fornecedor_id=fornecedor_id,
            nome_item=nome_item,
            preco_por_kg=preco_por_kg,
            descricao=descricao
        )
        db.session.add(tabela)
        db.session.commit()
        flash(f'Item "{nome_item}" adicionado à tabela de preços!', 'success')
        return redirect(url_for('tabela_precos', fornecedor_id=fornecedor_id))
    
    tabelas = TabelaPreco.query.filter_by(fornecedor_id=fornecedor_id, ativo=True).all()
    return render_template('tabela_precos.html', fornecedor=fornecedor, tabelas=tabelas)

@app.route('/tabela-precos/<int:tabela_id>/editar', methods=['GET', 'POST'])
@comprador_required
def editar_tabela_preco(tabela_id):
    """Editar item da tabela de preços."""
    tabela = TabelaPreco.query.get_or_404(tabela_id)
    
    if request.method == 'POST':
        tabela.nome_item = request.form.get('nome_item', '').strip()
        tabela.preco_por_kg = request.form.get('preco_por_kg', type=float)
        tabela.descricao = request.form.get('descricao', '').strip()
        
        db.session.commit()
        flash('Item da tabela atualizado com sucesso!', 'success')
        return redirect(url_for('tabela_precos', fornecedor_id=tabela.fornecedor_id))
    
    return render_template('editar_tabela_preco.html', tabela=tabela)

@app.route('/tabela-precos/<int:tabela_id>/deletar', methods=['POST'])
@comprador_required
def deletar_tabela_preco(tabela_id):
    """Deletar item da tabela de preços."""
    tabela = TabelaPreco.query.get_or_404(tabela_id)
    fornecedor_id = tabela.fornecedor_id
    nome_item = tabela.nome_item
    tabela.ativo = False
    db.session.commit()
    flash(f'Item "{nome_item}" removido da tabela de preços!', 'success')
    return redirect(url_for('tabela_precos', fornecedor_id=fornecedor_id))

@app.route('/tabela-precos/<int:fornecedor_id>/importar', methods=['GET', 'POST'])
@admin_required
def importar_tabela_preco(fornecedor_id):
    """Importar tabela de preços de outro fornecedor."""
    fornecedor_destino = Fornecedor.query.get_or_404(fornecedor_id)
    
    if request.method == 'POST':
        fornecedor_origem_id = request.form.get('fornecedor_origem_id', type=int)
        
        if not fornecedor_origem_id:
            flash('Selecione um fornecedor de origem.', 'danger')
            return redirect(url_for('importar_tabela_preco', fornecedor_id=fornecedor_id))
        
        fornecedor_origem = Fornecedor.query.get_or_404(fornecedor_origem_id)
        tabelas_origem = TabelaPreco.query.filter_by(fornecedor_id=fornecedor_origem_id, ativo=True).all()
        
        if not tabelas_origem:
            flash('Fornecedor de origem não possui tabela de preços.', 'warning')
            return redirect(url_for('importar_tabela_preco', fornecedor_id=fornecedor_id))
        
        # Copiar tabelas
        for tabela_origem in tabelas_origem:
            nova_tabela = TabelaPreco(
                fornecedor_id=fornecedor_id,
                nome_item=tabela_origem.nome_item,
                preco_por_kg=tabela_origem.preco_por_kg,
                descricao=tabela_origem.descricao
            )
            db.session.add(nova_tabela)
        
        db.session.commit()
        flash(f'Tabela de preços importada de {fornecedor_origem.nome_social} com sucesso!', 'success')
        return redirect(url_for('tabela_precos', fornecedor_id=fornecedor_id))
    
    fornecedores_lista = Fornecedor.query.filter(Fornecedor.id != fornecedor_id).all()
    return render_template('importar_tabela_preco.html', fornecedor=fornecedor_destino, fornecedores=fornecedores_lista)

# ==================== ROTAS CRUD - COMPRAS ====================

@app.route('/compras', methods=['GET', 'POST'])
@comprador_required
def compras():
    """CRUD de compras com tabela de preços."""
    if request.method == 'POST':
        fornecedor_id = request.form.get('fornecedor_id', type=int)
        tabela_preco_id = request.form.get('tabela_preco_id', type=int)
        quantidade_kg = request.form.get('quantidade_kg', type=float)
        tipo_coleta = request.form.get('tipo_coleta', '').strip()
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        endereco_coleta = request.form.get('endereco_coleta', '').strip()
        observacao = request.form.get('observacao', '').strip()
        
        if not fornecedor_id or not tabela_preco_id or not quantidade_kg or not tipo_coleta:
            flash('Fornecedor, item, quantidade e tipo de coleta são obrigatórios.', 'danger')
            return redirect(url_for('compras'))
        
        if quantidade_kg <= 0:
            flash('Quantidade deve ser maior que zero.', 'danger')
            return redirect(url_for('compras'))
        
        # Obter dados da tabela de preços
        tabela = TabelaPreco.query.get_or_404(tabela_preco_id)
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
        
        # Calcular valores
        preco_unitario = tabela.preco_por_kg
        valor_total = quantidade_kg * preco_unitario
        preco_maximo = fornecedor.preco_maximo_automatico
        
        # Determinar status do preço
        if valor_total < preco_maximo:
            status_preco = 'menor'
            status_aprovacao = 'aprovada'  # Aprovação automática
        elif valor_total == preco_maximo:
            status_preco = 'igual'
            status_aprovacao = 'aprovada'  # Aprovação automática
        else:
            status_preco = 'maior'
            status_aprovacao = 'pendente'  # Aguarda aprovação admin
        
        # Obter comissão do comprador
        comissao = ComissaoComprador.query.filter_by(comprador_id=current_user.id).first()
        comissao_percentual = comissao.percentual_comissao if comissao else 0.0
        valor_comissao = (valor_total * comissao_percentual) / 100
        
        compra = Compra(
            fornecedor_id=fornecedor_id,
            tabela_preco_id=tabela_preco_id,
            quantidade_kg=quantidade_kg,
            preco_unitario=preco_unitario,
            valor_total=valor_total,
            preco_maximo=preco_maximo,
            status_preco=status_preco,
            status_aprovacao=status_aprovacao,
            tipo_coleta=tipo_coleta,
            latitude=latitude,
            longitude=longitude,
            endereco_coleta=endereco_coleta,
            observacao=observacao,
            comprador_id=current_user.id,
            comissao_percentual=comissao_percentual,
            valor_comissao=valor_comissao
        )
        db.session.add(compra)
        db.session.commit()
        
        if status_aprovacao == 'aprovada':
            flash(f'Compra cadastrada e aprovada automaticamente! Valor: R$ {valor_total:.2f}', 'success')
        else:
            flash(f'Compra cadastrada! Aguardando aprovação do admin. Valor: R$ {valor_total:.2f}', 'warning')
        
        return redirect(url_for('compras'))
    
    page = request.args.get('page', 1, type=int)
    compras_list = Compra.query.order_by(Compra.data.desc()).paginate(page=page, per_page=10)
    fornecedores_list = Fornecedor.query.all()
    return render_template('compras.html', compras=compras_list, fornecedores=fornecedores_list)

@app.route('/compras/<int:id>/editar', methods=['GET', 'POST'])
@comprador_required
def editar_compra(id):
    """Editar compra."""
    compra = Compra.query.get_or_404(id)
    
    if request.method == 'POST':
        compra.quantidade_kg = request.form.get('quantidade_kg', type=float)
        compra.tipo_coleta = request.form.get('tipo_coleta', '').strip()
        compra.latitude = request.form.get('latitude', type=float)
        compra.longitude = request.form.get('longitude', type=float)
        compra.endereco_coleta = request.form.get('endereco_coleta', '').strip()
        compra.observacao = request.form.get('observacao', '').strip()
        
        # Recalcular valores
        compra.valor_total = compra.quantidade_kg * compra.preco_unitario
        compra.valor_comissao = (compra.valor_total * compra.comissao_percentual) / 100
        
        db.session.commit()
        flash('Compra atualizada com sucesso!', 'success')
        return redirect(url_for('compras'))
    
    fornecedores_list = Fornecedor.query.all()
    return render_template('editar_compra.html', compra=compra, fornecedores=fornecedores_list)

@app.route('/compras/<int:id>/deletar', methods=['POST'])
@comprador_required
def deletar_compra(id):
    """Deletar compra."""
    compra = Compra.query.get_or_404(id)
    item_nome = compra.tabela_preco.nome_item if compra.tabela_preco else 'Item'
    db.session.delete(compra)
    db.session.commit()
    flash(f'Compra de {item_nome} deletada com sucesso!', 'success')
    return redirect(url_for('compras'))

@app.route('/compras/<int:id>/aprovar', methods=['POST'])
@admin_required
def aprovar_compra(id):
    """Aprovar compra pendente."""
    compra = Compra.query.get_or_404(id)
    compra.status_aprovacao = 'aprovada'
    db.session.commit()
    flash(f'Compra aprovada com sucesso! Valor: R$ {compra.valor_total:.2f}', 'success')
    return redirect(url_for('compras'))

@app.route('/compras/<int:id>/rejeitar', methods=['POST'])
@admin_required
def rejeitar_compra(id):
    """Rejeitar compra pendente."""
    compra = Compra.query.get_or_404(id)
    compra.status_aprovacao = 'rejeitada'
    db.session.commit()
    flash(f'Compra rejeitada!', 'warning')
    return redirect(url_for('compras'))

# ==================== ROTAS CRUD - DESPESAS ====================

@app.route('/despesas', methods=['GET', 'POST'])
@comprador_required
def despesas():
    """CRUD de despesas."""
    if request.method == 'POST':
        nome_social = request.form.get('nome_social', '').strip()
        valor = request.form.get('valor', type=float)
        data_str = request.form.get('data', '')
        
        if not nome_social or not valor or not data_str:
            flash('Nome social, valor e data são obrigatórios.', 'danger')
            return redirect(url_for('despesas'))
        
        if valor <= 0:
            flash('Valor deve ser maior que zero.', 'danger')
            return redirect(url_for('despesas'))
        
        try:
            data = datetime.strptime(data_str, '%Y-%m-%d')
        except ValueError:
            flash('Data inválida.', 'danger')
            return redirect(url_for('despesas'))
        
        if data > datetime.utcnow():
            flash('Data não pode ser futura.', 'danger')
            return redirect(url_for('despesas'))
        
        despesa = Despesa(
            nome_social=nome_social,
            endereco_rua=request.form.get('endereco_rua', '').strip(),
            endereco_numero=request.form.get('endereco_numero', '').strip(),
            endereco_cidade=request.form.get('endereco_cidade', '').strip(),
            endereco_cep=request.form.get('endereco_cep', '').strip(),
            endereco_estado=request.form.get('endereco_estado', '').strip(),
            telefone=request.form.get('telefone', '').strip(),
            email=request.form.get('email', '').strip(),
            vendedor_id=current_user.id,
            conta=request.form.get('conta', '').strip(),
            agencia=request.form.get('agencia', '').strip(),
            chave_pix=request.form.get('chave_pix', '').strip(),
            banco=request.form.get('banco', '').strip(),
            condicao_pagamento=request.form.get('condicao_pagamento', '').strip(),
            forma_pagamento=request.form.get('forma_pagamento', '').strip(),
            descricao_gasto=request.form.get('descricao_gasto', '').strip(),
            data=data,
            valor=valor,
            observacao=request.form.get('observacao', '').strip()
        )
        db.session.add(despesa)
        db.session.commit()
        flash('Despesa cadastrada com sucesso!', 'success')
        return redirect(url_for('despesas'))
    
    page = request.args.get('page', 1, type=int)
    despesas_list = Despesa.query.order_by(Despesa.data.desc()).paginate(page=page, per_page=10)
    return render_template('despesas.html', despesas=despesas_list)

@app.route('/despesas/<int:id>/editar', methods=['GET', 'POST'])
@comprador_required
def editar_despesa(id):
    """Editar despesa."""
    despesa = Despesa.query.get_or_404(id)
    
    if request.method == 'POST':
        despesa.nome_social = request.form.get('nome_social', '').strip()
        despesa.valor = request.form.get('valor', type=float)
        data_str = request.form.get('data', '')
        
        if despesa.valor <= 0:
            flash('Valor deve ser maior que zero.', 'danger')
            return redirect(url_for('editar_despesa', id=id))
        
        if data_str:
            try:
                despesa.data = datetime.strptime(data_str, '%Y-%m-%d')
            except ValueError:
                flash('Data inválida.', 'danger')
                return redirect(url_for('editar_despesa', id=id))
        
        despesa.endereco_rua = request.form.get('endereco_rua', '').strip()
        despesa.endereco_numero = request.form.get('endereco_numero', '').strip()
        despesa.endereco_cidade = request.form.get('endereco_cidade', '').strip()
        despesa.endereco_cep = request.form.get('endereco_cep', '').strip()
        despesa.endereco_estado = request.form.get('endereco_estado', '').strip()
        despesa.telefone = request.form.get('telefone', '').strip()
        despesa.email = request.form.get('email', '').strip()
        despesa.conta = request.form.get('conta', '').strip()
        despesa.agencia = request.form.get('agencia', '').strip()
        despesa.chave_pix = request.form.get('chave_pix', '').strip()
        despesa.banco = request.form.get('banco', '').strip()
        despesa.condicao_pagamento = request.form.get('condicao_pagamento', '').strip()
        despesa.forma_pagamento = request.form.get('forma_pagamento', '').strip()
        despesa.descricao_gasto = request.form.get('descricao_gasto', '').strip()
        despesa.observacao = request.form.get('observacao', '').strip()
        
        db.session.commit()
        flash('Despesa atualizada com sucesso!', 'success')
        return redirect(url_for('despesas'))
    
    return render_template('editar_despesa.html', despesa=despesa)

@app.route('/despesas/<int:id>/deletar', methods=['POST'])
@comprador_required
def deletar_despesa(id):
    """Deletar despesa."""
    despesa = Despesa.query.get_or_404(id)
    nome = despesa.nome_social
    db.session.delete(despesa)
    db.session.commit()
    flash(f'Despesa de {nome} deletada com sucesso!', 'success')
    return redirect(url_for('despesas'))

# ==================== ROTAS CRUD - USUÁRIOS (ADMIN) ====================

@app.route('/usuarios', methods=['GET', 'POST'])
@admin_required
def usuarios():
    """CRUD de usuários."""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        papel = request.form.get('papel', 'VISUALIZADOR')
        
        if not nome or not email or not senha:
            flash('Nome, email e senha são obrigatórios.', 'danger')
            return redirect(url_for('usuarios'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('usuarios'))
        
        usuario = Usuario(
            nome=nome,
            email=email,
            papel=RoleEnum[papel]
        )
        usuario.set_password(senha)
        db.session.add(usuario)
        db.session.commit()
        flash(f'Usuário {nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    
    page = request.args.get('page', 1, type=int)
    usuarios_list = Usuario.query.paginate(page=page, per_page=10)
    roles = [role.name for role in RoleEnum]
    return render_template('usuarios.html', usuarios=usuarios_list, roles=roles)

@app.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_usuario(id):
    """Editar usuário."""
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        usuario.nome = request.form.get('nome', '').strip()
        usuario.papel = RoleEnum[request.form.get('papel', 'VISUALIZADOR')]
        usuario.ativo = request.form.get('ativo') == 'on'
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    
    roles = [role.name for role in RoleEnum]
    return render_template('editar_usuario.html', usuario=usuario, roles=roles)

@app.route('/usuarios/<int:id>/deletar', methods=['POST'])
@admin_required
def deletar_usuario(id):
    """Deletar usuário."""
    usuario = Usuario.query.get_or_404(id)
    
    if usuario.id == current_user.id:
        flash('Você não pode deletar sua própria conta.', 'danger')
        return redirect(url_for('usuarios'))
    
    nome = usuario.nome
    db.session.delete(usuario)
    db.session.commit()
    flash(f'Usuário {nome} deletado com sucesso!', 'success')
    return redirect(url_for('usuarios'))

# ==================== ROTAS DE EXPORTAÇÃO E FILTROS ====================

@app.route('/compras/exportar-pdf')
@comprador_required
def exportar_compras_pdf():
    """Exporta compras em PDF."""
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    fornecedor_id = request.args.get('fornecedor_id', type=int)
    
    data_inicio = None
    data_fim = None
    
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    pdf_buffer = gerar_relatorio_compras_pdf(data_inicio, data_fim, fornecedor_id)
    
    return app.response_class(
        response=pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=relatorio_compras.pdf'}
    )

@app.route('/despesas/exportar-pdf')
@comprador_required
def exportar_despesas_pdf():
    """Exporta despesas em PDF."""
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    forma_pagamento = request.args.get('forma_pagamento')
    
    data_inicio = None
    data_fim = None
    
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    pdf_buffer = gerar_relatorio_despesas_pdf(data_inicio, data_fim, forma_pagamento)
    
    return app.response_class(
        response=pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': 'attachment; filename=relatorio_despesas.pdf'}
    )

# ==================== ROTAS CRUD - COMISSÕES ====================

@app.route('/comissoes', methods=['GET'])
@admin_required
def comissoes():
    """Listar comissões de compradores."""
    page = request.args.get('page', 1, type=int)
    comissoes_list = ComissaoComprador.query.order_by(ComissaoComprador.mes_referencia.desc()).paginate(page=page, per_page=10)
    return render_template('comissoes.html', comissoes=comissoes_list)

@app.route('/comissoes/<int:comprador_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_comissao(comprador_id):
    """Editar percentual de comissão de um comprador."""
    comprador = Usuario.query.get_or_404(comprador_id)
    
    if request.method == 'POST':
        percentual = request.form.get('percentual_comissao', type=float)
        
        if percentual is None or percentual < 0:
            flash('Percentual de comissão inválido.', 'danger')
            return redirect(url_for('editar_comissao', comprador_id=comprador_id))
        
        # Atualizar ou criar comissão
        comissao = ComissaoComprador.query.filter_by(comprador_id=comprador_id).first()
        if not comissao:
            comissao = ComissaoComprador(comprador_id=comprador_id)
            db.session.add(comissao)
        
        comissao.percentual_comissao = percentual
        db.session.commit()
        flash(f'Comissão de {comprador.nome} atualizada para {percentual}%!', 'success')
        return redirect(url_for('comissoes'))
    
    comissao = ComissaoComprador.query.filter_by(comprador_id=comprador_id).first()
    return render_template('editar_comissao.html', comprador=comprador, comissao=comissao)

@app.route('/comissoes/<int:comprador_id>/calcular', methods=['POST'])
@admin_required
def calcular_comissao(comprador_id):
    """Calcular comissão mensal de um comprador."""
    mes_referencia = request.form.get('mes_referencia')  # Formato: YYYY-MM
    
    if not mes_referencia:
        flash('Mês de referência é obrigatório.', 'danger')
        return redirect(url_for('comissoes'))
    
    # Buscar compras aprovadas do mês
    try:
        ano, mes = mes_referencia.split('-')
        ano, mes = int(ano), int(mes)
    except ValueError:
        flash('Formato de mês inválido.', 'danger')
        return redirect(url_for('comissoes'))
    
    compras = Compra.query.filter(
        Compra.comprador_id == comprador_id,
        Compra.status_aprovacao == 'aprovada',
        db.extract('year', Compra.data) == ano,
        db.extract('month', Compra.data) == mes
    ).all()
    
    valor_total = sum(c.valor_total for c in compras)
    
    # Obter comissão
    comissao = ComissaoComprador.query.filter_by(comprador_id=comprador_id).first()
    if not comissao:
        comissao = ComissaoComprador(comprador_id=comprador_id)
        db.session.add(comissao)
    
    comissao.mes_referencia = mes_referencia
    comissao.valor_total_compras = valor_total
    comissao.valor_comissao_total = (valor_total * comissao.percentual_comissao) / 100
    db.session.commit()
    
    flash(f'Comissão calculada! Total de compras: R$ {valor_total:.2f}, Comissão: R$ {comissao.valor_comissao_total:.2f}', 'success')
    return redirect(url_for('comissoes'))

@app.route('/comissoes/<int:comissao_id>/pagar', methods=['POST'])
@admin_required
def pagar_comissao(comissao_id):
    """Marcar comissão como paga."""
    comissao = ComissaoComprador.query.get_or_404(comissao_id)
    comissao.status_pagamento = 'pago'
    comissao.data_pagamento = datetime.utcnow()
    db.session.commit()
    flash(f'Comissão marcada como paga!', 'success')
    return redirect(url_for('comissoes'))

# ==================== ROTAS CRUD - DADOS BANCÁRIOS ====================

@app.route('/fornecedores/<int:id>/dados-bancarios', methods=['GET', 'POST'])
@admin_required
def dados_bancarios_fornecedor(id):
    """Gerenciar dados bancários de um fornecedor."""
    fornecedor = Fornecedor.query.get_or_404(id)
    
    if request.method == 'POST':
        fornecedor.banco = request.form.get('banco', '').strip()
        fornecedor.agencia = request.form.get('agencia', '').strip()
        fornecedor.conta = request.form.get('conta', '').strip()
        fornecedor.tipo_conta = request.form.get('tipo_conta', '').strip()
        fornecedor.chave_pix = request.form.get('chave_pix', '').strip()
        fornecedor.preco_maximo_automatico = request.form.get('preco_maximo_automatico', type=float)
        
        db.session.commit()
        flash('Dados bancários atualizado com sucesso!', 'success')
        return redirect(url_for('fornecedores'))
    
    return render_template('dados_bancarios_fornecedor.html', fornecedor=fornecedor)

# ==================== TRATAMENTO DE ERROS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ==================== CONTEXTO DE TEMPLATE ====================

@app.context_processor
def inject_user():
    """Injeta usuário atual no contexto de template."""
    return {'current_user': current_user}

# ==================== INICIALIZAÇÃO ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Criar usuário admin padrão se não existir
        if not Usuario.query.filter_by(email='admin@mrx.com.br').first():
            admin = Usuario(
                nome='Administrador MRX',
                email='admin@mrx.com.br',
                papel=RoleEnum.ADMIN,
                ativo=True
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin@mrx.com.br criado com sucesso!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
