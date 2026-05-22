# Especificação Técnica: Promoção de Artefatos Stout

**Data:** 2026-05-06
**Status:** Aprovada (Brainstorming Encerrado)
**Autor:** Antigravity (Engenheiro)

---

## 1. Objetivo
Padronizar e automatizar a persistência de conhecimento gerado durante as sessões do Antigravity no repositório local do projeto, eliminando a dependência do cache efêmero (`brain/`) e garantindo a soberania dos dados do framework Stout.

## 2. Requisitos

### 2.1 Funcionais
- **Descoberta de Sessão:** O sistema deve localizar a pasta de sessão mais recente no diretório global do Antigravity que contenha artefatos válidos.
- **Nomenclatura Padrão:** Os arquivos devem ser renomeados seguindo o padrão: `YYYY-MM-DD-{nome-do-projeto}-{tipo}.md`.
- **Limpeza de Sufixos:** O sufixo `.response` deve ser removido dos nomes dos arquivos durante a promoção.
- **Organização por Subpastas:**
    - Planos (.resolved) -> `./docs/plans/`
    - Walkthroughs -> `./docs/walkthroughs/`
- **Extração de Nome de Projeto:** O nome do projeto deve ser extraído prioritariamente do arquivo `GEMINI.md` local (seção `PROJETO:`).

### 2.2 Não-Funcionais
- **Encoding:** O script deve utilizar UTF-8 e evitar caracteres especiais que causem falhas em terminais Windows (substituir símbolos Unicode por ASCII).
- **Idempotência:** O script não deve realizar cópias se o arquivo de destino já existir com o mesmo conteúdo (opcional, mas recomendado).
- **Integração Global:** A solução deve ser integrável à skill `stout-init` para replicação automática em novos projetos.

## 3. Arquitetura Proposta

### 3.1 Script `scripts/stout_promote.py`
Um script Python autônomo que será o coração da automação. Ele será responsável pela lógica de busca no sistema de arquivos e renomeação.

### 3.2 Fluxo de Execução
1. O Agente finaliza uma tarefa ou plano.
2. O Agente executa `python scripts/stout_promote.py`.
3. O script varre `~/.gemini/antigravity/brain/`.
4. O script identifica os artefatos `implementation_plan.md.resolved` e `walkthrough.md`.
5. O script realiza o espelhamento para a pasta `docs/` do projeto local.

## 4. Plano de Validação (DoD)
- [ ] Script executado sem erros de encoding no Windows.
- [ ] Arquivo `implementation_plan.md.resolved` promovido como `YYYY-MM-DD-projeto-plan.md` em `docs/plans/`.
- [ ] Arquivo `walkthrough.md` promovido como `YYYY-MM-DD-projeto-walkthrough.md` em `docs/walkthroughs/`.
- [ ] Regra de automação visível no `GEMINI.md` local.

---
*Esta Spec encerra a fase de design e autoriza a criação do plano de execução.*
