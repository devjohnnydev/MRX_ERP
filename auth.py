from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user
from models import RoleEnum

def login_required_custom(f):
    """Decorator para exigir login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator para exigir papéis específicos."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Você precisa fazer login.', 'warning')
                return redirect(url_for('login'))
            
            if current_user.papel not in roles:
                flash('Você não tem permissão para acessar esta página.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator para exigir papel ADMIN."""
    return role_required(RoleEnum.ADMIN)(f)

def comprador_required(f):
    """Decorator para exigir papel COMPRADOR ou ADMIN."""
    return role_required(RoleEnum.COMPRADOR, RoleEnum.ADMIN)(f)

def validar_cpf(cpf):
    """Valida CPF (formato básico)."""
    cpf = cpf.replace('.', '').replace('-', '')
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    return True

def validar_cnpj(cnpj):
    """Valida CNPJ (formato básico)."""
    cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
    if len(cnpj) != 14 or not cnpj.isdigit():
        return False
    return True

def formatar_cpf(cpf):
    """Formata CPF para XXX.XXX.XXX-XX."""
    cpf = cpf.replace('.', '').replace('-', '')
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def formatar_cnpj(cnpj):
    """Formata CNPJ para XX.XXX.XXX/XXXX-XX."""
    cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj
