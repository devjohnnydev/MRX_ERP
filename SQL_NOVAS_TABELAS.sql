-- ============================================================================
-- SQL COMPLETO - CRIAÇÃO DAS NOVAS TABELAS
-- MRX Gestão v2.0
-- Data: 2025-11-08
-- ============================================================================

-- ============================================================================
-- 1. TABELA: tabela_precos
-- Descrição: Armazena os itens de preço de cada fornecedor
-- ============================================================================

CREATE TABLE IF NOT EXISTS tabela_precos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fornecedor_id INTEGER NOT NULL,
    nome_item VARCHAR(255) NOT NULL,
    preco_por_kg FLOAT NOT NULL,
    unidade VARCHAR(20) DEFAULT 'kg',
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id) ON DELETE CASCADE
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_tabela_precos_fornecedor_id 
    ON tabela_precos(fornecedor_id);

CREATE INDEX IF NOT EXISTS idx_tabela_precos_ativo 
    ON tabela_precos(ativo);

-- ============================================================================
-- 2. TABELA: comissao_comprador
-- Descrição: Registra comissões de cada comprador na rua
-- ============================================================================

CREATE TABLE IF NOT EXISTS comissao_comprador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comprador_id INTEGER NOT NULL,
    percentual_comissao FLOAT DEFAULT 0.0,
    valor_total_compras FLOAT DEFAULT 0.0,
    valor_comissao_total FLOAT DEFAULT 0.0,
    mes_referencia VARCHAR(7),
    status_pagamento VARCHAR(20) DEFAULT 'pendente',
    data_pagamento DATETIME,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comprador_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_comissao_comprador_id 
    ON comissao_comprador(comprador_id);

CREATE INDEX IF NOT EXISTS idx_comissao_mes_referencia 
    ON comissao_comprador(mes_referencia);

CREATE INDEX IF NOT EXISTS idx_comissao_status_pagamento 
    ON comissao_comprador(status_pagamento);

-- ============================================================================
-- 3. ALTERAÇÕES NA TABELA: fornecedores
-- Descrição: Adiciona campos bancários e preço máximo
-- ============================================================================

-- Adicionar coluna banco (se não existir)
ALTER TABLE fornecedores ADD COLUMN banco VARCHAR(100);

-- Adicionar coluna agencia (se não existir)
ALTER TABLE fornecedores ADD COLUMN agencia VARCHAR(10);

-- Adicionar coluna conta (se não existir)
ALTER TABLE fornecedores ADD COLUMN conta VARCHAR(20);

-- Adicionar coluna chave_pix (se não existir)
ALTER TABLE fornecedores ADD COLUMN chave_pix VARCHAR(255);

-- Adicionar coluna tipo_conta (se não existir)
ALTER TABLE fornecedores ADD COLUMN tipo_conta VARCHAR(20);

-- Adicionar coluna preco_maximo_automatico (se não existir)
ALTER TABLE fornecedores ADD COLUMN preco_maximo_automatico FLOAT DEFAULT 1000.0;

-- ============================================================================
-- 4. ALTERAÇÕES NA TABELA: compras
-- Descrição: Adiciona campos de tabela de preços, geolocalização e comissão
-- ============================================================================

-- Adicionar coluna tabela_preco_id
ALTER TABLE compras ADD COLUMN tabela_preco_id INTEGER;

-- Adicionar coluna quantidade_kg
ALTER TABLE compras ADD COLUMN quantidade_kg FLOAT;

-- Adicionar coluna preco_unitario
ALTER TABLE compras ADD COLUMN preco_unitario FLOAT;

-- Adicionar coluna valor_total
ALTER TABLE compras ADD COLUMN valor_total FLOAT;

-- Adicionar coluna preco_maximo
ALTER TABLE compras ADD COLUMN preco_maximo FLOAT;

-- Adicionar coluna status_preco
ALTER TABLE compras ADD COLUMN status_preco VARCHAR(20) DEFAULT 'igual';

-- Adicionar coluna status_aprovacao
ALTER TABLE compras ADD COLUMN status_aprovacao VARCHAR(20) DEFAULT 'pendente';

-- Adicionar coluna latitude
ALTER TABLE compras ADD COLUMN latitude FLOAT;

-- Adicionar coluna longitude
ALTER TABLE compras ADD COLUMN longitude FLOAT;

-- Adicionar coluna endereco_coleta
ALTER TABLE compras ADD COLUMN endereco_coleta VARCHAR(255);

-- Adicionar coluna comissao_percentual
ALTER TABLE compras ADD COLUMN comissao_percentual FLOAT DEFAULT 0.0;

-- Adicionar coluna valor_comissao
ALTER TABLE compras ADD COLUMN valor_comissao FLOAT DEFAULT 0.0;

-- Adicionar chave estrangeira para tabela_precos
ALTER TABLE compras ADD CONSTRAINT fk_compras_tabela_preco 
    FOREIGN KEY (tabela_preco_id) REFERENCES tabela_precos(id);

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_compras_tabela_preco_id 
    ON compras(tabela_preco_id);

CREATE INDEX IF NOT EXISTS idx_compras_status_aprovacao 
    ON compras(status_aprovacao);

CREATE INDEX IF NOT EXISTS idx_compras_status_preco 
    ON compras(status_preco);

-- ============================================================================
-- 5. DADOS DE EXEMPLO (OPCIONAL)
-- ============================================================================

-- Exemplo 1: Adicionar item à tabela de preços (fornecedor_id = 1)
-- INSERT INTO tabela_precos (fornecedor_id, nome_item, preco_por_kg, descricao)
-- VALUES (1, 'Papel Branco A4', 10.50, 'Papel branco de qualidade A4');

-- Exemplo 2: Adicionar comissão para comprador (comprador_id = 2)
-- INSERT INTO comissao_comprador (comprador_id, percentual_comissao)
-- VALUES (2, 5.0);

-- Exemplo 3: Atualizar dados bancários do fornecedor (fornecedor_id = 1)
-- UPDATE fornecedores 
-- SET banco = 'Banco do Brasil',
--     agencia = '1234-5',
--     conta = '123456-7',
--     tipo_conta = 'corrente',
--     chave_pix = 'fornecedor@email.com',
--     preco_maximo_automatico = 1000.00
-- WHERE id = 1;

-- ============================================================================
-- 6. CONSULTAS ÚTEIS
-- ============================================================================

-- Listar todos os itens da tabela de preços
-- SELECT tp.id, tp.nome_item, tp.preco_por_kg, f.nome_social
-- FROM tabela_precos tp
-- JOIN fornecedores f ON tp.fornecedor_id = f.id
-- WHERE tp.ativo = 1
-- ORDER BY f.nome_social, tp.nome_item;

-- Listar comissões pendentes de pagamento
-- SELECT cc.id, u.nome, cc.percentual_comissao, cc.valor_comissao_total, cc.mes_referencia
-- FROM comissao_comprador cc
-- JOIN usuarios u ON cc.comprador_id = u.id
-- WHERE cc.status_pagamento = 'pendente'
-- ORDER BY cc.mes_referencia DESC;

-- Listar compras pendentes de aprovação
-- SELECT c.id, f.nome_social, tp.nome_item, c.quantidade_kg, c.valor_total, c.status_preco
-- FROM compras c
-- JOIN fornecedores f ON c.fornecedor_id = f.id
-- JOIN tabela_precos tp ON c.tabela_preco_id = tp.id
-- WHERE c.status_aprovacao = 'pendente'
-- ORDER BY c.criado_em DESC;

-- Calcular total de comissões por comprador (mês)
-- SELECT 
--     u.nome,
--     cc.mes_referencia,
--     cc.percentual_comissao,
--     cc.valor_total_compras,
--     cc.valor_comissao_total,
--     cc.status_pagamento
-- FROM comissao_comprador cc
-- JOIN usuarios u ON cc.comprador_id = u.id
-- ORDER BY cc.mes_referencia DESC, u.nome;

-- Listar compras com geolocalização
-- SELECT 
--     c.id,
--     u.nome as comprador,
--     f.nome_social as fornecedor,
--     tp.nome_item,
--     c.quantidade_kg,
--     c.valor_total,
--     c.latitude,
--     c.longitude,
--     c.endereco_coleta,
--     c.data
-- FROM compras c
-- JOIN usuarios u ON c.comprador_id = u.id
-- JOIN fornecedores f ON c.fornecedor_id = f.id
-- JOIN tabela_precos tp ON c.tabela_preco_id = tp.id
-- WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
-- ORDER BY c.data DESC;

-- ============================================================================
-- 7. BACKUP E RESTAURAÇÃO
-- ============================================================================

-- Para fazer backup das tabelas:
-- .dump tabela_precos > backup_tabela_precos.sql
-- .dump comissao_comprador > backup_comissao_comprador.sql

-- Para restaurar:
-- .read backup_tabela_precos.sql
-- .read backup_comissao_comprador.sql

-- ============================================================================
-- FIM DO SCRIPT SQL
-- ============================================================================
