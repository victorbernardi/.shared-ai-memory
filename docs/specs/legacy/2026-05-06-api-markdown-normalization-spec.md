# Spec: Normalização de Markdown IA-Friendly (Raiz)

**Data:** 06/05/2026
**Status:** Draft
**Contexto:** John Deere API Documentation Project

---

## 1. Objetivo

Resolver na raiz as falhas de formatação do script `normalize_endpoint_blocks.py`, garantindo que o pipeline de extração gere documentação Markdown em conformidade com padrões técnicos rigorosos e otimizada para consumo por modelos de linguagem (LLMs).

## 2. Requisitos Funcionais (IA-Friendly)

### 2.1 Unicidade de Identificadores (MD024)

- **Regra:** Cada endpoint deve possuir cabeçalhos internos exclusivos.
- **Implementação:** Os subtítulos de seção (Descrição, Parâmetros, JSON) devem ser concatenados semanticamente ou estruturados de forma que o linter não os considere duplicados (ex: `### Descrição: [GET] /path`).

### 2.2 Higienização de Fluxo de Texto (MD012)

- **Regra:** Máximo de 1 linha em branco entre parágrafos.
- **Implementação:** Criar um buffer de saída que colapse múltiplas quebras de linha (`\n\n\n+`) em no máximo duas (`\n\n`).

### 2.3 Formatação de Referências (MD034)

- **Regra:** URLs devem ser navegáveis e válidas.
- **Implementação:** Todas as URLs de fonte e links externos devem ser automaticamente envolvidas em `<url>`.

### 2.4 Excelência em Blocos de Código (MD031/MD040)

- **Regra:** JSONs devem ser legíveis por máquinas e humanos.
- **Implementação:**
  - Indentação obrigatória de 4 espaços para todos os payloads.
  - Especificação explícita da linguagem (` ```json `).
  - Garantia de linha em branco antes e depois do bloco de código.

## 3. Requisitos Não-Funcionais

- **Soberania de Dados:** O script deve processar arquivos `.raw.md` e gerar arquivos finais sem perda de conteúdo original.
- **Performance:** O tempo de processamento por arquivo deve ser inferior a 2 segundos.
- **Manutenibilidade:** Uso de templates ou funções modulares para montagem do Markdown, facilitando futuras alterações de layout.

## 4. Arquitetura da Solução (Proposta)

A função `build_markdown` será refatorada para utilizar um modelo de **Pipeline de Sanitização**:

1. **Extract:** Coleta dados brutos do endpoint.
2. **Sanitize:** Limpa strings, remove HTML residual e formata URLs.
3. **Format JSON:** Usa `json.dumps(..., indent=4)` para normalizar exemplos.
4. **Assemble:** Monta o documento usando uma estrutura de cabeçalhos única.

## 5. Plano de Validação (DoD)

### 5.1 Critérios de Aceitação

- Executar o script contra `output/md/field-operations.raw.md`.
- Validar o output final com o comando `markdownlint` (ou verificação visual de warnings no IDE).
- Testar a ingestão do arquivo gerado em um prompt de IA para verificar a clareza da resposta sobre os endpoints.

---
Assinado por: **Antigravity / Gemini CLI Engenheiro**
