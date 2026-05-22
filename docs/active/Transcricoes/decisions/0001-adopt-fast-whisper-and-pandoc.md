# Adotar Fast-Whisper e Pandoc para o Pipeline de Transcrição e Conversão

* Status: accepted
* Date: 2026-05-04
* Decision-makers: Victor Bernardi (USER), Antigravity (AI Agent)
* Consulted: doc-workflow-orchestrator

## Context and Problem Statement

O projeto de transcrições necessita de um pipeline robusto que garanta alta fidelidade (1:1) para alimentação do NotebookLM e resumos executivos (Atas) para consumo humano. 
Problemas identificados:
1. Instabilidade em scripts Python que tentam invocar CLIs globais (erro WinError 2).
2. Baixa qualidade visual de PDFs gerados por scripts básicos de `fpdf`.
3. Falta de um motor de conversão padronizado que suporte formatação rica de Markdown.

## Decision Outcome

Escolhido: **Unified Antigravity Pipeline (UAP)**.
A decisão é utilizar o motor `faster-whisper` para a extração bruta e o `pandoc` como motor oficial de conversão para PDF, garantindo que a "Transcrição Full" seja um artefato premium para análise de longo prazo.

### Positive Consequences

* **Estabilidade:** Remoção de dependências de scripts "scratch" instáveis.
* **Qualidade Visual:** PDFs gerados pelo Pandoc possuem suporte completo a tabelas e timestamps.
* **Integridade:** Separação clara entre dados brutos (NotebookLM) e dados sumarizados (Humanos).

### Negative Consequences

* **Dependência:** Exige que o `pandoc` esteja presente no PATH do sistema Windows.
* **Complexidade:** Necessita de parametrização correta dos comandos de conversão.

## Considered Options

### 1. Scratch Python Scripts (Status Quo)
* Bom: Leve e sem dependências externas.
* Ruim: Falha com caracteres especiais e formatação rica de Markdown.

### 2. Pandoc + PDF Engine (Chosen)
* Bom: Padrão da indústria para conversão de documentos. Altamente customizável.
* Ruim: Requer instalação de motor de renderização no SO.

## Pros and Cons of the Options

### Pandoc
* Good, because it handles tables, links and images natively.
* Good, because it is the Antigravity standard for high-end documentation.
* Bad, because it requires command-line familiarity.

## Confirmation

A conformidade será verificada através da geração do arquivo `2026-05-04_Inova-Maquinas-15_FULL.pdf` com formatação preservada e ausência de erros de codec no log de execução.

---
*ID: ADR-0001 | Projeto: Transcricoes*
