# Spec: Unificação do Histórico Documental (v6)

## 1. Objetivo
Centralizar todos os artefatos de governança (planos e especificações) espalhados entre `.antigravity`, `C:\Motores-LLM` e o workspace atual em uma estrutura única, organizada e cronológica, eliminando a fragmentação do conhecimento técnico.

## 2. Diagnóstico de Riscos e Colisões
- **Colisão de Nomes:** Arquivos como `plan_reconciliacao_v3.md` podem existir com conteúdos diferentes em épocas distintas.
- **Duplicidade Redundante:** `.antigravity` e `C:\Motores-LLM` compartilham 100% dos arquivos (sincronizados). A unificação deve tratar essa origem como única ("Legado Golden Copy").
- **Perda de Metadados:** A data de criação original (2026-04-28/29) é vital para entender a evolução do sistema. Mover arquivos sem preservar ou registrar essa data no nome/conteúdo prejudica a "Mastery of Context".
- **Dependência de Junctions:** Verificar se algum processo de build depende da localização física dos arquivos em `.antigravity/docs`.

## 3. Requisitos de Organização
- **Categorização Cronológica:** Manter os prefixos de data (AAAA-MM-DD) onde já existirem.
- **Hierarquia Proposta:**
  - `docs/specs/legacy/`: Especificações anteriores à sessão atual.
  - `docs/plans/legacy/`: Planos anteriores à sessão atual.
  - `docs/specs/active/`: Especificações desta sessão (v2, v3, v4, v5, v6).
  - `docs/plans/active/`: Planos desta sessão.
- **Unificação de Fontes:** Fundir o rastro de `.antigravity` para dentro do repositório central do workspace.

## 4. Arquitetura de Solução
1. **Mapeamento de Hash:** Identificar se arquivos com nomes iguais em pastas diferentes são idênticos.
2. **Migração Não-Destrutiva:** Copiar em vez de mover inicialmente, validando a integridade antes da limpeza.
3. **Atualização do Strategic Master:** O `GEMINI.md` deve ser atualizado para reconhecer a nova estrutura de histórico.

## 5. Plano de Validação
- **Audit de Contagem:** O total de arquivos no novo repositório central deve bater com a soma (16 planos, 11 specs).
- **Verificação de Acesso:** O agente deve conseguir resumir um plano de 28/04 localizado na pasta `legacy`.

---
*Status: Spec v6 Pesquisada | Pronto para Estratégia*
