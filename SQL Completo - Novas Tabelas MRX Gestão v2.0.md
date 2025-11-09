# SQL Completo - Novas Tabelas MRX Gestão v2.0

## 📋 Índice

1. [Tabela `tabela_precos`](#tabela-tabela_precos)
2. [Tabela `comissao_comprador`](#tabela-comissao_comprador)
3. [Alterações em `fornecedores`](#alterações-em-fornecedores)
4. [Alterações em `compras`](#alterações-em-compras)
5. [Índices e Performance](#índices-e-performance)
6. [Consultas Úteis](#consultas-úteis)
7. [Exemplos de Uso](#exemplos-de-uso)

---

## Tabela `tabela_precos`

### Descrição
Armazena os itens de preço de cada fornecedor. Cada fornecedor pode ter múltiplos itens com preços diferentes.

### SQL de Criação

```sql
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
```

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | Identificador único (chave primária) |
| `fornecedor_id` | INTEGER | ID do fornecedor (chave estrangeira) |
| `nome_item` | VARCHAR(255) | Nome do item (ex: "Papel Branco A4") |
| `preco_por_kg` | FLOAT | Preço por quilo em reais |
| `unidade` | VARCHAR(20) | Unidade de medida (padrão: "kg") |
| `descricao` | TEXT | Descrição detalhada do item |
| `ativo` | BOOLEAN | Flag para soft delete (1=ativo, 0=inativo) |
| `criado_em` | DATETIME | Timestamp de criação |
| `atualizado_em` | DATETIME | Timestamp de última atualização |

### Exemplo de Inserção

```sql
INSERT INTO tabela_precos (fornecedor_id, nome_item, preco_por_kg, descricao)
VALUES (1, 'Papel Branco A4', 10.50, 'Papel branco de qualidade A4');

INSERT INTO tabela_precos (fornecedor_id, nome_item, preco_por_kg, descricao)
VALUES (1, 'Papel Reciclado', 8.75, 'Papel reciclado 100%');

INSERT INTO tabela_precos (fornecedor_id, nome_item, preco_por_kg, descricao)
VALUES (2, 'Papelão Ondulado', 5.25, 'Papelão para embalagens');
```

### Índices

```sql
CREATE INDEX idx_tabela_precos_fornecedor_id ON tabela_precos(fornecedor_id);
CREATE INDEX idx_tabela_precos_ativo ON tabela_precos(ativo);
```

---

## Tabela `comissao_comprador`

### Descrição
Registra as comissões de cada comprador na rua. Armazena percentual de comissão, valores calculados e status de pagamento.

### SQL de Criação

```sql
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
```

### Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | Identificador único (chave primária) |
| `comprador_id` | INTEGER | ID do comprador (chave estrangeira) |
| `percentual_comissao` | FLOAT | Percentual de comissão (ex: 5.0 para 5%) |
| `valor_total_compras` | FLOAT | Soma de todas as compras do mês |
| `valor_comissao_total` | FLOAT | Valor total de comissão a pagar |
| `mes_referencia` | VARCHAR(7) | Mês em formato YYYY-MM |
| `status_pagamento` | VARCHAR(20) | Status: 'pendente' ou 'pago' |
| `data_pagamento` | DATETIME | Data em que foi pago |
| `criado_em` | DATETIME | Timestamp de criação |
| `atualizado_em` | DATETIME | Timestamp de última atualização |

### Exemplo de Inserção

```sql
-- Criar registro de comissão para um comprador
INSERT INTO comissao_comprador (comprador_id, percentual_comissao)
VALUES (2, 5.0);

-- Calcular comissão mensal
UPDATE comissao_comprador
SET 
    mes_referencia = '2025-11',
    valor_total_compras = 5000.00,
    valor_comissao_total = 250.00
WHERE comprador_id = 2 AND mes_referencia = '2025-11';

-- Marcar como pago
UPDATE comissao_comprador
SET 
    status_pagamento = 'pago',
    data_pagamento = CURRENT_TIMESTAMP
WHERE id = 1;
```

### Índices

```sql
CREATE INDEX idx_comissao_comprador_id ON comissao_comprador(comprador_id);
CREATE INDEX idx_comissao_mes_referencia ON comissao_comprador(mes_referencia);
CREATE INDEX idx_comissao_status_pagamento ON comissao_comprador(status_pagamento);
```

---

## Alterações em `fornecedores`

### Descrição
Adiciona campos bancários e preço máximo para aprovação automática.

### SQL de Alteração

```sql
-- Banco
ALTER TABLE fornecedores ADD COLUMN banco VARCHAR(100);

-- Agência
ALTER TABLE fornecedores ADD COLUMN agencia VARCHAR(10);

-- Conta
ALTER TABLE fornecedores ADD COLUMN conta VARCHAR(20);

-- Chave PIX
ALTER TABLE fornecedores ADD COLUMN chave_pix VARCHAR(255);

-- Tipo de Conta
ALTER TABLE fornecedores ADD COLUMN tipo_conta VARCHAR(20);

-- Preço Máximo para Aprovação Automática
ALTER TABLE fornecedores ADD COLUMN preco_maximo_automatico FLOAT DEFAULT 1000.0;
```

### Novos Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `banco` | VARCHAR(100) | Nome do banco (ex: "Banco do Brasil") |
| `agencia` | VARCHAR(10) | Número da agência (ex: "1234-5") |
| `conta` | VARCHAR(20) | Número da conta (ex: "123456-7") |
| `chave_pix` | VARCHAR(255) | Chave PIX para transferências |
| `tipo_conta` | VARCHAR(20) | Tipo de conta: 'corrente' ou 'poupanca' |
| `preco_maximo_automatico` | FLOAT | Preço máximo para aprovação automática |

### Exemplo de Atualização

```sql
UPDATE fornecedores
SET 
    banco = 'Banco do Brasil',
    agencia = '1234-5',
    conta = '123456-7',
    tipo_conta = 'corrente',
    chave_pix = 'fornecedor@email.com',
    preco_maximo_automatico = 1000.00
WHERE id = 1;
```

---

## Alterações em `compras`

### Descrição
Adiciona campos para tabela de preços, geolocalização, aprovação e comissão.

### SQL de Alteração

```sql
-- Referência à tabela de preços
ALTER TABLE compras ADD COLUMN tabela_preco_id INTEGER;

-- Quantidade em quilos
ALTER TABLE compras ADD COLUMN quantidade_kg FLOAT;

-- Preço unitário (por kg)
ALTER TABLE compras ADD COLUMN preco_unitario FLOAT;

-- Valor total da compra
ALTER TABLE compras ADD COLUMN valor_total FLOAT;

-- Preço máximo do fornecedor
ALTER TABLE compras ADD COLUMN preco_maximo FLOAT;

-- Status do preço (menor/igual/maior)
ALTER TABLE compras ADD COLUMN status_preco VARCHAR(20) DEFAULT 'igual';

-- Status de aprovação (pendente/aprovada/rejeitada)
ALTER TABLE compras ADD COLUMN status_aprovacao VARCHAR(20) DEFAULT 'pendente';

-- Latitude da coleta
ALTER TABLE compras ADD COLUMN latitude FLOAT;

-- Longitude da coleta
ALTER TABLE compras ADD COLUMN longitude FLOAT;

-- Endereço de coleta
ALTER TABLE compras ADD COLUMN endereco_coleta VARCHAR(255);

-- Percentual de comissão
ALTER TABLE compras ADD COLUMN comissao_percentual FLOAT DEFAULT 0.0;

-- Valor de comissão
ALTER TABLE compras ADD COLUMN valor_comissao FLOAT DEFAULT 0.0;

-- Chave estrangeira
ALTER TABLE compras ADD CONSTRAINT fk_compras_tabela_preco 
    FOREIGN KEY (tabela_preco_id) REFERENCES tabela_precos(id);
```

### Novos Campos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `tabela_preco_id` | INTEGER | ID do item da tabela de preços |
| `quantidade_kg` | FLOAT | Quantidade em quilos |
| `preco_unitario` | FLOAT | Preço por kg |
| `valor_total` | FLOAT | Valor total (quantidade × preço) |
| `preco_maximo` | FLOAT | Preço máximo do fornecedor |
| `status_preco` | VARCHAR(20) | 'menor', 'igual' ou 'maior' |
| `status_aprovacao` | VARCHAR(20) | 'pendente', 'aprovada' ou 'rejeitada' |
| `latitude` | FLOAT | Latitude da coleta |
| `longitude` | FLOAT | Longitude da coleta |
| `endereco_coleta` | VARCHAR(255) | Endereço de coleta |
| `comissao_percentual` | FLOAT | Percentual de comissão |
| `valor_comissao` | FLOAT | Valor de comissão |

### Exemplo de Inserção

```sql
INSERT INTO compras (
    fornecedor_id, 
    comprador_id, 
    tabela_preco_id, 
    quantidade_kg, 
    preco_unitario, 
    valor_total, 
    preco_maximo, 
    status_preco, 
    status_aprovacao, 
    latitude, 
    longitude, 
    endereco_coleta, 
    comissao_percentual, 
    valor_comissao,
    data
)
VALUES (
    1,                          -- fornecedor_id
    2,                          -- comprador_id
    1,                          -- tabela_preco_id (Papel Branco A4)
    100,                        -- quantidade_kg
    10.50,                      -- preco_unitario
    1050.00,                    -- valor_total (100 × 10.50)
    1000.00,                    -- preco_maximo
    'maior',                    -- status_preco (1050 > 1000)
    'pendente',                 -- status_aprovacao
    -23.5505,                   -- latitude (São Paulo)
    -46.6333,                   -- longitude (São Paulo)
    'Rua das Flores, 123',      -- endereco_coleta
    5.0,                        -- comissao_percentual
    52.50,                      -- valor_comissao (1050 × 5%)
    CURRENT_TIMESTAMP           -- data
);
```

### Índices

```sql
CREATE INDEX idx_compras_tabela_preco_id ON compras(tabela_preco_id);
CREATE INDEX idx_compras_status_aprovacao ON compras(status_aprovacao);
CREATE INDEX idx_compras_status_preco ON compras(status_preco);
```

---

## Índices e Performance

### Índices Criados

```sql
-- Tabela de Preços
CREATE INDEX idx_tabela_precos_fornecedor_id ON tabela_precos(fornecedor_id);
CREATE INDEX idx_tabela_precos_ativo ON tabela_precos(ativo);

-- Comissão Comprador
CREATE INDEX idx_comissao_comprador_id ON comissao_comprador(comprador_id);
CREATE INDEX idx_comissao_mes_referencia ON comissao_comprador(mes_referencia);
CREATE INDEX idx_comissao_status_pagamento ON comissao_comprador(status_pagamento);

-- Compras
CREATE INDEX idx_compras_tabela_preco_id ON compras(tabela_preco_id);
CREATE INDEX idx_compras_status_aprovacao ON compras(status_aprovacao);
CREATE INDEX idx_compras_status_preco ON compras(status_preco);
```

### Benefícios
- **Busca rápida** por fornecedor na tabela de preços
- **Filtro rápido** de itens ativos/inativos
- **Busca rápida** de comissões por comprador
- **Filtro rápido** por mês de referência
- **Filtro rápido** por status de pagamento
- **Busca rápida** de compras pendentes de aprovação
- **Filtro rápido** por status de preço

---

## Consultas Úteis

### 1. Listar Tabela de Preços de um Fornecedor

```sql
SELECT 
    tp.id,
    tp.nome_item,
    tp.preco_por_kg,
    tp.unidade,
    tp.descricao,
    f.nome_social
FROM tabela_precos tp
JOIN fornecedores f ON tp.fornecedor_id = f.id
WHERE tp.fornecedor_id = 1 AND tp.ativo = 1
ORDER BY tp.nome_item;
```

### 2. Listar Comissões Pendentes de Pagamento

```sql
SELECT 
    cc.id,
    u.nome,
    cc.percentual_comissao,
    cc.valor_total_compras,
    cc.valor_comissao_total,
    cc.mes_referencia
FROM comissao_comprador cc
JOIN usuarios u ON cc.comprador_id = u.id
WHERE cc.status_pagamento = 'pendente'
ORDER BY cc.mes_referencia DESC;
```

### 3. Listar Compras Pendentes de Aprovação

```sql
SELECT 
    c.id,
    f.nome_social,
    tp.nome_item,
    c.quantidade_kg,
    c.valor_total,
    c.status_preco,
    u.nome as comprador
FROM compras c
JOIN fornecedores f ON c.fornecedor_id = f.id
JOIN tabela_precos tp ON c.tabela_preco_id = tp.id
JOIN usuarios u ON c.comprador_id = u.id
WHERE c.status_aprovacao = 'pendente'
ORDER BY c.criado_em DESC;
```

### 4. Calcular Total de Comissões por Comprador (Mês)

```sql
SELECT 
    u.nome,
    cc.mes_referencia,
    cc.percentual_comissao,
    cc.valor_total_compras,
    cc.valor_comissao_total,
    cc.status_pagamento
FROM comissao_comprador cc
JOIN usuarios u ON cc.comprador_id = u.id
WHERE cc.mes_referencia = '2025-11'
ORDER BY cc.valor_comissao_total DESC;
```

### 5. Listar Compras com Geolocalização

```sql
SELECT 
    c.id,
    u.nome as comprador,
    f.nome_social as fornecedor,
    tp.nome_item,
    c.quantidade_kg,
    c.valor_total,
    c.latitude,
    c.longitude,
    c.endereco_coleta,
    c.data
FROM compras c
JOIN usuarios u ON c.comprador_id = u.id
JOIN fornecedores f ON c.fornecedor_id = f.id
JOIN tabela_precos tp ON c.tabela_preco_id = tp.id
WHERE c.latitude IS NOT NULL AND c.longitude IS NOT NULL
ORDER BY c.data DESC;
```

### 6. Relatório de Compras por Status

```sql
SELECT 
    c.status_aprovacao,
    COUNT(*) as total_compras,
    SUM(c.valor_total) as valor_total,
    AVG(c.valor_total) as valor_medio
FROM compras c
WHERE c.data >= DATE('now', '-30 days')
GROUP BY c.status_aprovacao;
```

### 7. Relatório de Comissões por Comprador (Anual)

```sql
SELECT 
    u.nome,
    SUBSTR(cc.mes_referencia, 1, 4) as ano,
    COUNT(*) as total_meses,
    SUM(cc.valor_comissao_total) as total_comissoes,
    AVG(cc.valor_comissao_total) as media_mensal
FROM comissao_comprador cc
JOIN usuarios u ON cc.comprador_id = u.id
WHERE cc.status_pagamento = 'pago'
GROUP BY u.id, ano
ORDER BY u.nome, ano DESC;
```

---

## Exemplos de Uso

### Exemplo 1: Cadastrar Novo Fornecedor com Tabela de Preços

```sql
-- 1. Inserir fornecedor (já existe na tabela fornecedores)
-- Assumindo que o fornecedor com id=3 já existe

-- 2. Adicionar dados bancários
UPDATE fornecedores
SET 
    banco = 'Caixa Econômica',
    agencia = '0001',
    conta = '000123456-7',
    tipo_conta = 'corrente',
    chave_pix = 'cnpj.fornecedor@email.com',
    preco_maximo_automatico = 1500.00
WHERE id = 3;

-- 3. Adicionar itens à tabela de preços
INSERT INTO tabela_precos (fornecedor_id, nome_item, preco_por_kg, descricao)
VALUES 
    (3, 'Papelão Branco', 6.50, 'Papelão branco para embalagens'),
    (3, 'Papelão Ondulado', 5.75, 'Papelão ondulado resistente'),
    (3, 'Papel Kraft', 7.25, 'Papel kraft natural');
```

### Exemplo 2: Registrar Compra e Calcular Comissão

```sql
-- 1. Inserir compra
INSERT INTO compras (
    fornecedor_id, comprador_id, tabela_preco_id,
    quantidade_kg, preco_unitario, valor_total,
    preco_maximo, status_preco, status_aprovacao,
    latitude, longitude, endereco_coleta,
    comissao_percentual, valor_comissao, data
)
VALUES (
    3, 2, 5,
    200, 6.50, 1300.00,
    1500.00, 'menor', 'aprovada',
    -23.5505, -46.6333, 'Av. Paulista, 1000',
    5.0, 65.00, CURRENT_TIMESTAMP
);

-- 2. Atualizar comissão do comprador
UPDATE comissao_comprador
SET 
    valor_total_compras = valor_total_compras + 1300.00,
    valor_comissao_total = (valor_total_compras + 1300.00) * percentual_comissao / 100
WHERE comprador_id = 2 AND mes_referencia = '2025-11';
```

### Exemplo 3: Aprovar Compra Pendente

```sql
-- Atualizar status de aprovação
UPDATE compras
SET status_aprovacao = 'aprovada'
WHERE id = 1 AND status_aprovacao = 'pendente';

-- Atualizar comissão se necessário
UPDATE comissao_comprador
SET valor_comissao_total = valor_comissao_total + 52.50
WHERE comprador_id = (SELECT comprador_id FROM compras WHERE id = 1);
```

### Exemplo 4: Calcular e Pagar Comissão Mensal

```sql
-- 1. Calcular comissão mensal (mês de novembro de 2025)
UPDATE comissao_comprador cc
SET 
    mes_referencia = '2025-11',
    valor_total_compras = (
        SELECT SUM(c.valor_total)
        FROM compras c
        WHERE c.comprador_id = cc.comprador_id
        AND c.status_aprovacao = 'aprovada'
        AND SUBSTR(c.data, 1, 7) = '2025-11'
    ),
    valor_comissao_total = (
        SELECT SUM(c.valor_total) * cc.percentual_comissao / 100
        FROM compras c
        WHERE c.comprador_id = cc.comprador_id
        AND c.status_aprovacao = 'aprovada'
        AND SUBSTR(c.data, 1, 7) = '2025-11'
    )
WHERE comprador_id = 2;

-- 2. Marcar como pago
UPDATE comissao_comprador
SET 
    status_pagamento = 'pago',
    data_pagamento = CURRENT_TIMESTAMP
WHERE comprador_id = 2 AND mes_referencia = '2025-11';
```

---

## Resumo

| Tabela | Registros | Campos | Índices |
|--------|-----------|--------|---------|
| `tabela_precos` | Múltiplos por fornecedor | 9 | 2 |
| `comissao_comprador` | 1+ por comprador/mês | 10 | 3 |
| `fornecedores` (alterado) | Existentes | +6 | - |
| `compras` (alterado) | Existentes | +12 | 3 |

---

**Data**: 2025-11-08  
**Versão**: 2.0  
**Status**: ✅ Completo
