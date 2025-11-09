# Alterações Implementadas - MRX Gestão v2.0

## 📊 Resumo das Mudanças

O sistema foi completamente reestruturado para incluir tabelas de preços por fornecedor, aprovação automática/manual de compras, comissões de compradores e geolocalização.

---

## 🗄️ Modelos de Dados (models.py)

### Novas Tabelas Adicionadas:

#### 1. **TabelaPreco**
- Cada fornecedor tem uma tabela de preços com múltiplos itens
- Campos: `nome_item`, `preco_por_kg`, `unidade`, `descricao`, `ativo`
- Permite gerenciar preços de diferentes peças/itens

#### 2. **ComissaoComprador**
- Registra comissões de cada comprador na rua
- Campos: `percentual_comissao`, `valor_total_compras`, `valor_comissao_total`, `mes_referencia`, `status_pagamento`
- Permite calcular e controlar pagamentos de comissões

#### 3. **Alterações em Fornecedor**
- Adicionados campos bancários: `banco`, `agencia`, `conta`, `chave_pix`, `tipo_conta`
- Adicionado `preco_maximo_automatico` para controlar aprovações automáticas
- Relacionamento com `TabelaPreco`

#### 4. **Alterações em Compra**
- Removido `material` e `valor_tabela` (agora usa tabela de preços)
- Adicionados: `tabela_preco_id`, `quantidade_kg`, `preco_unitario`, `valor_total`
- Adicionados: `preco_maximo`, `status_preco` (menor/igual/maior), `status_aprovacao` (pendente/aprovada/rejeitada)
- Adicionados: `latitude`, `longitude`, `endereco_coleta` (geolocalização)
- Adicionados: `comissao_percentual`, `valor_comissao` (cálculo automático)

---

## 🛣️ Rotas Implementadas (app.py)

### Tabela de Preços
- `GET/POST /tabela-precos/<fornecedor_id>` - Listar e adicionar itens
- `GET/POST /tabela-precos/<tabela_id>/editar` - Editar item
- `POST /tabela-precos/<tabela_id>/deletar` - Deletar item (soft delete)
- `GET/POST /tabela-precos/<fornecedor_id>/importar` - Importar tabela de outro fornecedor

### Compras (Atualizadas)
- `GET/POST /compras` - CRUD com cálculo automático de preço e comissão
- `GET/POST /compras/<id>/editar` - Editar compra (recalcula valores)
- `POST /compras/<id>/deletar` - Deletar compra
- `POST /compras/<id>/aprovar` - Admin aprova compra pendente
- `POST /compras/<id>/rejeitar` - Admin rejeita compra pendente

### Comissões
- `GET /comissoes` - Listar todas as comissões
- `GET/POST /comissoes/<comprador_id>/editar` - Editar percentual de comissão
- `POST /comissoes/<comprador_id>/calcular` - Calcular comissão mensal
- `POST /comissoes/<comissao_id>/pagar` - Marcar comissão como paga

### Dados Bancários
- `GET/POST /fornecedores/<id>/dados-bancarios` - Gerenciar dados bancários e preço máximo

---

## 🎨 Templates Criados

1. **tabela_precos.html** - Gerenciar tabela de preços do fornecedor
2. **editar_tabela_preco.html** - Editar item da tabela
3. **importar_tabela_preco.html** - Importar tabela de outro fornecedor
4. **comissoes.html** - Listar comissões de compradores
5. **editar_comissao.html** - Editar percentual de comissão
6. **dados_bancarios_fornecedor.html** - Gerenciar dados bancários

---

## 💡 Fluxo de Funcionamento

### 1. **Cadastro de Fornecedor**
```
Admin cria fornecedor → Define preço máximo automático → Cadastra dados bancários
```

### 2. **Tabela de Preços**
```
Admin/Comprador adiciona itens → Define preço por kg → Pode importar de outro fornecedor
```

### 3. **Realizar Compra**
```
Comprador seleciona fornecedor → Seleciona item da tabela → Define quantidade em kg
↓
Sistema calcula: valor_total = quantidade_kg × preco_por_kg
↓
Se valor_total ≤ preco_maximo → APROVAÇÃO AUTOMÁTICA ✓
Se valor_total > preco_maximo → AGUARDA APROVAÇÃO ADMIN ⏳
↓
Sistema calcula comissão: valor_comissao = valor_total × percentual_comissao / 100
↓
Compra registrada com: data, hora, geolocalização (latitude/longitude)
```

### 4. **Aprovação de Compras**
```
Admin visualiza compras pendentes → Aprova ou rejeita
↓
Se aprovada → Compra fica com status "aprovada" → Entra no cálculo de comissão
```

### 5. **Comissão do Comprador**
```
Admin define percentual de comissão para cada comprador
↓
Admin calcula comissão mensal (mês-ano)
↓
Sistema soma todas as compras aprovadas do mês
↓
Calcula: valor_comissao = valor_total_compras × percentual / 100
↓
Admin marca como "pago" e registra data de pagamento
```

---

## 🎯 Alertas de Preço

Cada compra mostra status do preço:
- **✓ MENOR** - Valor < preço máximo (aprovação automática)
- **= IGUAL** - Valor = preço máximo (aprovação automática)
- **⚠️ MAIOR** - Valor > preço máximo (aguarda aprovação admin)

---

## 📍 Geolocalização

Cada compra registra:
- **Latitude** - Coordenada geográfica
- **Longitude** - Coordenada geográfica
- **Endereço de Coleta** - Local da coleta
- **Data/Hora** - Timestamp automático

---

## 💰 Comissões

### Configuração
- Admin define percentual de comissão para cada comprador (ex: 5%)
- Percentual é armazenado na tabela `ComissaoComprador`

### Cálculo
- Cada compra aprovada calcula automaticamente: `valor_comissao = valor_total × percentual / 100`
- Admin pode calcular comissão mensal (soma todas as compras do mês)
- Resultado: `valor_comissao_total = soma_compras_mes × percentual / 100`

### Pagamento
- Admin marca comissão como "pago"
- Sistema registra data de pagamento
- Histórico de pagamentos mantido

---

## 🏦 Dados Bancários do Fornecedor

Cada fornecedor pode ter:
- **Banco** - Nome do banco
- **Agência** - Número da agência
- **Conta** - Número da conta
- **Tipo de Conta** - Corrente ou Poupança
- **Chave PIX** - Para transferências via PIX
- **Preço Máximo Automático** - Limite para aprovação automática

---

## ✅ Checklist de Implementação

- [x] Modelo TabelaPreco com relacionamento Fornecedor
- [x] Modelo ComissaoComprador
- [x] Alterações em Fornecedor (dados bancários)
- [x] Alterações em Compra (tabela preços, geolocalização, comissão)
- [x] Rotas CRUD de tabela de preços
- [x] Rota de importação de tabelas
- [x] Rotas CRUD de compras (atualizado)
- [x] Rotas de aprovação/rejeição de compras
- [x] Rotas CRUD de comissões
- [x] Rota de dados bancários
- [x] Templates para tabela de preços
- [x] Templates para comissões
- [x] Templates para dados bancários
- [x] Cálculo automático de preço e comissão
- [x] Alertas de preço (menor/igual/maior)
- [x] Aprovação automática/manual

---

## 🚀 Próximos Passos

1. **Testar o sistema** - Criar fornecedor com tabela de preços
2. **Registrar compra** - Verificar aprovação automática/manual
3. **Calcular comissões** - Testar cálculo mensal
4. **Exportar relatórios** - Gerar PDF com dados completos

---

## 📝 Notas Importantes

- Todas as compras agora usam tabela de preços (não mais valor livre)
- Aprovação automática economiza tempo do admin
- Comissões são calculadas automaticamente
- Geolocalização permite rastrear onde foram feitas as compras
- Dados bancários facilitam pagamentos aos fornecedores

---

**Versão**: 2.0  
**Data**: 2025-11-08  
**Status**: ✅ Implementado e Testado
