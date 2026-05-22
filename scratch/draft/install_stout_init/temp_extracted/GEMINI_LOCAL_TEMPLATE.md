# 📂 GEMINI.md - PROJETO: [Nome do Projeto]

> **Herança:** Este arquivo estende as regras do GEMINI.md Global do Plano Executivo.
> Regras aqui definidas prevalecem sobre as globais em caso de conflito.

---

## 1. CONTEXTO DE NEGÓCIO

**Objetivo de Negócio:** [Ex: Reduzir tempo de inatividade de frota otimizando alocação de peças]
**KPI Principal:** [Ex: Aumento do First Time Fix (FTF) e Redução do Backorder]
**Leitura Executiva:** [Resumo de 2 linhas do que este projeto resolve e sua importância estratégica]
**Stakeholders:** [Quem consome os outputs deste projeto]

---

## 2. CONTEXTO TÉCNICO LOCAL

### Stack Específica
- **Linguagem/Framework:** [Ex: Python 3.11 + FastAPI]
- **Banco de Dados:** [Ex: PostgreSQL 15]
- **Dependências Críticas:** [Listar libs/frameworks chave]

### Integrações Externas
- [ ] APIs externas: [Ex: John Deere API, Google Maps API]
- [ ] Serviços internos: [Ex: ERP, CRM]
- [ ] Autenticação: [Ex: OAuth2, API Keys]

### Estrutura de Pastas do Projeto
```
[NomeProjeto]/
├── GEMINI.md              # Este arquivo
├── ANTIGRAVITY.md         # Kernel operacional (se usar Antigravity)
├── README.md              # Visão geral
├── .env.example           # Variáveis de ambiente
├── docs/                  # Documentação
│   ├── specs/             # Especificações
│   ├── plans/             # Planos de ação
│   └── adr/               # Decisões de arquitetura
├── src/                   # Código-fonte
├── data/                  # Dados e queries
├── tests/                 # Testes
└── scripts/               # Automações
```

---

## 3. REGRAS LOCAIS

### Padrões de Código Específicos
- [Ex: Todos os endpoints REST devem retornar envelope JSON `{data, meta, error}`]
- [Ex: Nomenclatura de variáveis em português para domínio de negócio]

### Diretrizes de Análise
- Toda análise de dados deve conectar anomalias técnicas aos KPIs de negócio.
- Outputs estruturados começando pelo impacto financeiro/operacional.

### Restrições
- [Ex: Não usar bibliotecas com licença GPL em módulos de integração]
- [Ex: Limite de 1000 registros por query em ambiente de desenvolvimento]

---

## 4. ESTADO ATUAL DO PROJETO (State Tracking)

> **ATUALIZAR VIA AGENTE:** Use `replace_file_content` (Antigravity) ou `edit` (Gemini CLI) para manter esta seção sincronizada.

### Fase Atual: [Research | Strategy | Execution | Validation | Concluído]

#### Progresso STOUT
- [ ] **Research:** [Status: Completo/Pendente - O que foi descoberto]
- [ ] **Strategy:** [Status: Completo/Pendente - Plano definido]
- [ ] **Execution:** [Status: Completo/Pendente - O que foi implementado]
- [ ] **Validation:** [Status: Completo/Pendente - Testes e resultados]

#### Decisões Pendentes
- [Ex: Definir formato de exportação do relatório - CSV vs Parquet]

#### Bloqueios
- [Ex: Aguardando acesso à API de produção John Deere]

---

## 5. NOTAS DE CONTEXTO

> **Adicione aqui descobertas, variáveis, caminhos e nuances importantes.**

- *Ex: A coluna `dt_movimento` no CSV está vindo como string, precisa de parse para datetime*
- *Ex: Query SQL de referência para faturamento mensal está em `data/queries/faturamento.sql`*
- *Ex: Token da API John Deere expira a cada 24h, implementar refresh automático*

---

## 6. PRÓXIMAS AÇÕES

1. [Ação imediata com próximo passo claro]
2. [Ação seguinte, dependente da primeira]
3. [Ação futura, após validação]

---

## 7. REFERÊNCIAS EXTERNAS

- **Documentação API:** [Link]
- **Wiki/Confluence:** [Link]
- **Repositório Git:** [Link]
- **Board de Tarefas:** [Link Jira/Trello/etc]
