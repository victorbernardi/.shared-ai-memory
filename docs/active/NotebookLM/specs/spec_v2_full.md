# Especificação Técnica v2 — NotebookLM Knowledge Base (Stout Edition)

## 1. Visão Geral
Este projeto automatiza a construção de uma base de conhecimento sênior para o **NotebookLM**. Ele processa uma curadoria de 300 fontes acadêmicas e técnicas, transformando-as em PDFs otimizados para ingestão via API.

## 2. Requisitos Funcionais (Functional Requirements)
| ID | Descrição | Rastreabilidade |
| --- | --- | --- |
| **FR-101** | Ingestão de 300 fontes curadas com alta fidelidade semântica. | Implements: AC-3 |
| **FR-102** | Captura de conteúdo HTML e extração de Markdown via `trafilatura`. | Implements: AC-2 |
| **FR-103** | Geração de PDF via motor estável (`fpdf`). | Implements: AC-2 |
| **FR-104** | Divisão de conteúdo em chunks semânticos baseados em headings e limite de palavras. | Implements: AC-2 |
| **FR-105** | Upload em ondas controladas (25, 50, 100, 300) via API. | Implements: AC-1, AC-3 |
| **FR-106** | Sistema de logs persistentes e catálogo de resultados/erros para recuperação. | Implements: AC-4 |

## 3. Cenários de Teste (Test Scenarios)
| ID | Cenário | Referência FR |
| --- | --- | --- |
| **T-101** | Validar captura de uma URL complexa com tabelas e links. | FR-102 |
| **T-102** | Validar se o chunking respeita os limites de palavras definidos no manifesto. | FR-104 |
| **T-103** | Validar geração de PDF legível no Windows usando `fpdf`. | FR-103 |
| **T-104** | Executar dry run (Wave 0) de 10 itens sem falhas de ambiente. | FR-105, FR-106 |

## 4. Arquitetura do Sistema

### 4.1. Fluxo de Dados
1.  **Ingestão:** Leitura do manifesto JSON (`notebooklm_llm_manifest_research_300.json`).
2.  **Captura:** Download do HTML e extração de conteúdo Markdown via `trafilatura`.
3.  **Processamento (Chunking):** Divisão do conteúdo em partes baseada em headings (H1-H3) e orçamento de palavras (target: 1500 palavras/PDF).
4.  **Conversão:** Geração de PDF via `fpdf` (motor otimizado para Windows/Stout).
5.  **Upload:** Envio via protocolo `raw` para a API do Google Discovery Engine (NotebookLM).

## 5. Pilha Tecnológica
- **Linguagem:** Python 3.11+
- **Captura:** `trafilatura` (precisão em artigos acadêmicos).
- **Conversão PDF:** `fpdf` (escolhida pela ausência de dependências externas).
- **Comunicação:** `requests` para chamadas de API.
- **Logging:** Sistema de logs persistentes em `./logs_research_300/`.

## 6. Governança e Segurança
- **Segredos:** Todas as chaves e IDs devem ser passados via **variáveis de ambiente**.
- **Gestão de Falhas:**
    - **Classe A (Ambiente):** Aborto imediato.
    - **Classe B (Extração):** Log de erro e skip para próxima fonte.
- **Protocolo de Ondas:** Wave 0 (Dry Run), Wave 1 (25 itens), etc.

## 7. Estrutura de Diretórios
```text
C:\Projetos\NotebookLM\
├── GEMINI.md                    # Manifesto Estratégico
├── docs\                        # Documentação Stout
│   ├── specs\                   # Especificações (Esta Spec)
│   └── plans\                   # Planos de Execução aprovados
├── exported-assets (6)\         # Pasta de Execução Atual
│   ├── script.py                # Motor de Execução
│   ├── manifest.json            # Fonte da Verdade
│   ├── logs_research_300\       # Logs da rodada
│   └── generated_pdfs_...\      # PDFs gerados
```

---
**Aprovado por: Gemini CLI — 04/05/2026**
