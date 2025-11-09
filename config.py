import os
from datetime import timedelta

# Diretório base do projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Diretório da instância (banco e configs locais)
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')

# Garante que a pasta 'instance' existe
os.makedirs(INSTANCE_DIR, exist_ok=True)

class Config:
    """Configuração base da aplicação."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Banco de dados dentro da pasta instance
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'mrx.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    SESSION_COOKIE_SECURE = False  # True apenas em produção
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB para upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
