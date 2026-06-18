# Plano de Execução: Arquivamento de Skills Específicas (v2)

> **Plano ID:** PLAN-002
> **Dependências:** SPEC-002
> **Data de Criação:** 2026-06-18
> **Status:** Pronto para Revisão

## 1. Escopo das Tarefas

### Tarefa 1: Validação de Registro (Ledger)
- **Ação:** Verificar o estado de `stout-subagent-driven-development` no ledger e confirmar se as demais skills não exigem atualizações sintáticas no JSON.
- **Arquivo:** `C:\Users\victor.bernardi\.gemini\skills\stout-skill-registry\registry.json`

### Tarefa 2: Movimentação Física das Pastas
- **Ação:** Mover os seguintes diretórios de skills de `C:\Users\victor.bernardi\.gemini\skills` para `C:\Users\victor.bernardi\.gemini\skills\_archived`:
  - `find-skills`
  - `subagent-driven-development`
  - `process-writing-skills`
- **Estratégia:** Criar e executar um script em Python temporário (ex: `C:\Users\victor.bernardi\.gemini\antigravity-cli\brain\48e10a76-e77a-4131-ad8a-84a83c33c0e7\scratch\archive_specific_skills.py`) ou um comando PowerShell direto que remova o destino caso ele exista e mova as pastas de forma limpa.

### Tarefa 3: Validação pós-arquivamento
- **Ação 1:** Validar que os diretórios movidos não residem mais em `C:\Users\victor.bernardi\.gemini\skills`.
- **Ação 2:** Validar que os diretórios movidos agora constam em `C:\Users\victor.bernardi\.gemini\skills\_archived`.

---

## 2. Roteiro Passo a Passo de Execução

### Passo 1: Executar Script de Movimentação Física
Executar um script em Python no diretório scratch da conversa para movimentar com segurança os três diretórios. Se a pasta de destino em `_archived` já existir, o script fará um cleanup antes de realizar a movimentação (usando `shutil.rmtree` e `shutil.move`).

### Passo 2: Executar Script de Validação
Verificar a presença/ausência das pastas nas respectivas localizações físico-geográficas usando um script de checagem.

---

## 3. Critérios de Sucesso
- As 3 skills físicas movidas com sucesso para `_archived`.
- Nenhuma falha estrutural no ecossistema local.
