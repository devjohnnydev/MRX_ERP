# 📱 Scanner de Peças & Geolocalização - MRX Gestão v2.1

## ✨ Novas Funcionalidades Implementadas

---

## 1️⃣ Scanner de Peças com Código de Barras/QR

### O que é?
Sistema que permite capturar código de barras ou QR code de peças e validar automaticamente contra o banco de dados.

### Como Funciona?

```
Comprador abre "Compra com Scanner"
        ↓
Seleciona fornecedor
        ↓
Aponta câmera para código de barras/QR
        ↓
Sistema valida código no banco de dados
        ↓
Se encontrado → Adiciona ao carrinho
Se não encontrado → Mostra erro
        ↓
Finaliza compra com dados completos
```

### Benefícios
✅ **Rápido** - Escaneia múltiplas peças em segundos  
✅ **Preciso** - Elimina erros de digitação  
✅ **Automático** - Valida contra banco de dados em tempo real  
✅ **Móvel** - Funciona em qualquer smartphone/tablet  

### Tecnologias Usadas
- **JavaScript** - Captura e processamento
- **Geolocation API** - Localização automática
- **Fetch API** - Comunicação com servidor
- **Bootstrap 5** - Interface responsiva

---

## 2️⃣ Geolocalização Automática

### O que é?
Captura automática da localização GPS do comprador na rua, registrando:
- **Latitude** - Coordenada geográfica
- **Longitude** - Coordenada geográfica
- **Endereço** - Local em formato legível
- **Data/Hora** - Timestamp da compra

### Como Funciona?

```
Página de compra carrega
        ↓
JavaScript solicita permissão de localização
        ↓
Navegador pede confirmação ao usuário
        ↓
Se permitido → Obtém coordenadas GPS
        ↓
Converte coordenadas em endereço (Nominatim/OSM)
        ↓
Exibe localização na página
        ↓
Registra na compra ao finalizar
```

### Benefícios
✅ **Rastreamento** - Sabe onde cada compra foi feita  
✅ **Segurança** - Auditoria de compras  
✅ **Análise** - Identifica padrões de compra por região  
✅ **Automático** - Não precisa digitar endereço  

### Permissões Necessárias
- Navegador pede permissão de localização
- Usuário pode permitir ou negar
- Funciona em HTTPS ou localhost
- Dados não são compartilhados com terceiros

---

## 3️⃣ Validação de Peças em Tempo Real

### O que é?
API que valida se uma peça existe no banco de dados do fornecedor selecionado.

### Endpoint da API

```
POST /api/validar-peca
Content-Type: application/json

{
    "codigo_barras": "123456789",
    "fornecedor_id": 1
}

Response (Sucesso):
{
    "sucesso": true,
    "peca": {
        "id": 5,
        "nome_item": "Papel Branco A4",
        "codigo_barras": "123456789",
        "preco_por_kg": 10.50,
        "unidade": "kg",
        "descricao": "Papel branco de qualidade A4"
    }
}

Response (Erro):
{
    "sucesso": false,
    "mensagem": "Peça não encontrada"
}
```

### Fluxo de Validação

```
1. Comprador escaneia código
        ↓
2. JavaScript envia para API
        ↓
3. API busca no banco de dados
        ↓
4. Se encontrado → Retorna dados da peça
        ↓
5. JavaScript adiciona ao carrinho
        ↓
6. Se não encontrado → Mostra erro
```

---

## 4️⃣ Carrinho de Compras Dinâmico

### Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| **Adicionar Peça** | Escaneia código e adiciona automaticamente |
| **Quantidade** | Define quantidade em quilos |
| **Cálculo Automático** | Multiplica quantidade × preço/kg |
| **Remover Item** | Deleta peça do carrinho |
| **Total Dinâmico** | Atualiza total em tempo real |
| **Validação** | Impede compra sem itens |

### Exemplo de Uso

```
1. Escaneia código "123456789"
   → Papel Branco A4 adicionado (R$ 10.50/kg)

2. Muda quantidade para 100 kg
   → Total atualizado: R$ 1.050,00

3. Escaneia código "987654321"
   → Papel Reciclado adicionado (R$ 8.75/kg)

4. Muda quantidade para 50 kg
   → Total atualizado: R$ 1.487,50

5. Clica "Finalizar Compra"
   → Sistema registra:
      - Peças escaneadas
      - Quantidades
      - Localização GPS
      - Data/Hora
      - Comprador
      - Fornecedor
```

---

## 5️⃣ Banco de Dados - Novo Campo

### Tabela `tabela_precos`

Campo adicionado:
```sql
codigo_barras VARCHAR(255) UNIQUE NOT NULL
```

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER | Identificador único |
| `fornecedor_id` | INTEGER | Referência ao fornecedor |
| `nome_item` | VARCHAR(255) | Nome da peça |
| **`codigo_barras`** | **VARCHAR(255)** | **Código de barras/QR (NOVO)** |
| `preco_por_kg` | FLOAT | Preço por quilo |
| `unidade` | VARCHAR(20) | Unidade de medida |
| `descricao` | TEXT | Descrição |
| `ativo` | BOOLEAN | Ativo/Inativo |
| `criado_em` | DATETIME | Data de criação |
| `atualizado_em` | DATETIME | Data de atualização |

### Tabela `compras`

Campos adicionados:
```sql
latitude FLOAT
longitude FLOAT
endereco_coleta VARCHAR(255)
```

---

## 6️⃣ Interface de Usuário

### Página: "Compra com Scanner"

```
┌─────────────────────────────────────────┐
│ 📱 Compra com Scanner                   │
├─────────────────────────────────────────┤
│                                         │
│ 📍 Localização Atual                    │
│ ├─ Latitude: -23.5505                  │
│ ├─ Longitude: -46.6333                 │
│ └─ Endereço: Av. Paulista, 1000        │
│                                         │
│ 🏢 Selecione o Fornecedor               │
│ └─ [Dropdown: Fornecedor A ▼]          │
│                                         │
│ 📦 Scanner de Peças                     │
│ └─ [Input: Escaneie o código...  ]     │
│                                         │
│ 🛒 Carrinho de Compras                  │
│ ├─ Papel Branco A4     | 100 kg | R$ 1050,00 | [Remover]
│ ├─ Papel Reciclado     | 50 kg  | R$ 437,50  | [Remover]
│ └─ Total: R$ 1.487,50                  │
│                                         │
│ [🔄 Limpar] [✓ Finalizar Compra]       │
└─────────────────────────────────────────┘
```

### Fluxo de Interação

1. **Página carrega** → Solicita permissão de localização
2. **Usuário permite** → Localização e endereço aparecem
3. **Seleciona fornecedor** → Pronto para escanear
4. **Escaneia peça** → Adicionada ao carrinho
5. **Define quantidade** → Total atualizado
6. **Finaliza compra** → Registra tudo (localização, data, hora)

---

## 7️⃣ Arquivos Criados/Modificados

### Novos Arquivos

```
static/js/scanner.js                    # JavaScript para scanner
templates/compra_scanner.html           # Template da página
.vscode/settings.json                   # Configurações VSCode
.vscode/launch.json                     # Debug VSCode
.gitignore                              # Arquivos ignorados
SETUP_LOCAL_VSCODE.md                   # Guia de setup local
SCANNER_GEOLOCATION_FEATURES.md         # Este arquivo
```

### Arquivos Modificados

```
models.py                               # Adicionado campo codigo_barras
app.py                                  # Adicionada rota /api/validar-peca
```

---

## 8️⃣ Como Testar

### Passo 1: Cadastrar Fornecedor com Tabela de Preços

```
1. Acesse "Fornecedores"
2. Crie novo fornecedor
3. Acesse "Tabela de Preços"
4. Adicione itens com código de barras:
   - Nome: "Papel Branco A4"
   - Código: "123456789"
   - Preço: "10.50"
```

### Passo 2: Acessar Compra com Scanner

```
1. Acesse "Compra com Scanner"
2. Permita acesso à localização
3. Selecione fornecedor
4. Digite código "123456789" e pressione ENTER
5. Peça será adicionada ao carrinho
```

### Passo 3: Verificar Dados Registrados

```
1. Acesse "Compras"
2. Clique na compra criada
3. Verifique:
   - Latitude/Longitude
   - Endereço de coleta
   - Data/Hora
   - Peças e quantidades
```

---

## 9️⃣ Segurança & Privacidade

### Geolocalização
- ✅ Dados armazenados localmente no banco de dados
- ✅ Não compartilhados com terceiros
- ✅ Usuário controla permissão
- ✅ Pode negar a qualquer momento

### Scanner
- ✅ Validação no servidor (não apenas cliente)
- ✅ Apenas usuários autenticados podem usar
- ✅ Apenas compradores podem acessar
- ✅ Logs de todas as operações

### API
- ✅ Requer autenticação (token de sessão)
- ✅ Requer papel de comprador
- ✅ Valida entrada (código e fornecedor)
- ✅ Retorna apenas dados necessários

---

## 🔟 Troubleshooting

### Problema: Geolocalização não funciona

**Causas:**
- Navegador em HTTP (não localhost)
- Usuário negou permissão
- GPS desativado no dispositivo
- Navegador desatualizado

**Solução:**
- Use HTTPS ou localhost
- Peça permissão novamente
- Ative GPS no dispositivo
- Atualize navegador

### Problema: Scanner não encontra peça

**Causas:**
- Código digitado errado
- Peça não cadastrada
- Peça inativa
- Fornecedor errado selecionado

**Solução:**
- Verifique código de barras
- Cadastre peça na tabela de preços
- Ative peça (ativo = true)
- Selecione fornecedor correto

### Problema: Endereço não aparece

**Causas:**
- Nominatim (OpenStreetMap) indisponível
- Localização muito remota
- Conexão com internet lenta

**Solução:**
- Aguarde alguns segundos
- Tente em local urbano
- Verifique conexão de internet
- Endereço é opcional (coordenadas já registram)

---

## 📊 Dados Registrados por Compra

```json
{
    "id": 1,
    "fornecedor_id": 1,
    "comprador_id": 2,
    "tabela_preco_id": 5,
    "quantidade_kg": 100,
    "preco_unitario": 10.50,
    "valor_total": 1050.00,
    "preco_maximo": 1000.00,
    "status_preco": "maior",
    "status_aprovacao": "pendente",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "endereco_coleta": "Av. Paulista, 1000",
    "comissao_percentual": 5.0,
    "valor_comissao": 52.50,
    "data": "2025-11-08 14:30:00",
    "criado_em": "2025-11-08 14:30:00"
}
```

---

## 🎯 Próximas Melhorias (Opcionais)

- [ ] Suporte para múltiplos códigos de barras por peça
- [ ] Histórico de localizações por comprador
- [ ] Mapa interativo mostrando locais de compra
- [ ] Relatório de geolocalização em PDF
- [ ] Integração com câmera nativa (PWA)
- [ ] Offline mode para scanner
- [ ] Sincronização automática de dados

---

## 📚 Referências

- **Geolocation API**: https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API
- **Nominatim (OSM)**: https://nominatim.org/
- **Barcode Scanners**: https://developer.mozilla.org/en-US/docs/Web/API/BarcodeDetector_API
- **Flask API**: https://flask.palletsprojects.com/

---

**Versão**: 2.1  
**Data**: 2025-11-08  
**Status**: ✅ Implementado e Testado  
**Autor**: MRX Gestão Team
