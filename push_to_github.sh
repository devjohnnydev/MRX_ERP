#!/bin/bash

# Script para fazer push do projeto MRX Gestão para GitHub
# Uso: bash push_to_github.sh

cd /home/ubuntu/mrx_gestao_flask

echo "📦 Preparando para fazer push para GitHub..."
echo ""

# Verificar se Git está inicializado
if [ ! -d ".git" ]; then
    echo "🔧 Inicializando repositório Git..."
    git init
    git remote add origin https://github.com/devjohnnydev/manu.git
    echo "✓ Repositório Git inicializado"
else
    echo "✓ Repositório Git já existe"
fi

echo ""
echo "📝 Adicionando arquivos..."
git add -A

echo ""
echo "💬 Commitando mudanças..."
git commit -m "MRX Gestão v2.1 - Scanner, Geolocalização e Correção de Bugs

- Adicionado scanner de peças com código de barras/QR
- Implementado geolocalização automática (latitude/longitude)
- Criada API de validação de peças (/api/validar-peca)
- Adicionado carrinho dinâmico com cálculo automático
- Configuração VSCode com debug (F5)
- Corrigido erro de serialização JSON no dashboard
- Documentação completa (SETUP_LOCAL_VSCODE.md)
- Scripts de deploy em produção (Gunicorn + Nginx + SSL)
- Tabela de preços com código de barras
- Aprovação automática/manual de compras
- Comissões de compradores
- Dados bancários de fornecedores
- Exportação de relatórios em PDF
- Tema verde/preto com identidade visual MRX"

echo ""
echo "🚀 Fazendo push para GitHub..."
git push -u origin main

echo ""
echo "✅ Push concluído com sucesso!"
echo ""
echo "Repositório: https://github.com/devjohnnydev/manu"
