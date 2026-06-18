# Plano de Execução: Registro de Skills Ausentes no Ledger (v3)

> **Plano ID:** PLAN-003
> **Dependências:** SPEC-003
> **Data de Criação:** 2026-06-18
> **Status:** Pronto para Revisão

## 1. Escopo das Tarefas

### Tarefa 1: Execução da Mesclagem no Ledger (`registry.json`)
- **Ação:** Criar e executar um script em Python temporário `register_missing_skills.py` na pasta de scratch.
- **Origem dos dados novos:** `C:\Users\victor.bernardi\.gemini\antigravity-cli\brain\48e10a76-e77a-4131-ad8a-84a83c33c0e7\scratch\missing_skills.json`
- **Arquivo de destino:** `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`
- **Regras do script:**
  - Ler o JSON original de `registry.json`.
  - Ler as novas skills em `missing_skills.json`.
  - Adicionar as novas skills no array `"skills"` do `registry.json`.
  - Mudar o valor de `"last_updated"` para `"2026-06-18"`.
  - Salvar o arquivo preservando a formatação.

### Tarefa 2: Validação Pós-Escrita
- **Ação 1:** Verificar se o arquivo `registry.json` continua sendo um JSON sintaticamente válido.
- **Ação 2:** Validar que o total de skills ativas no arquivo aumentou de 30 para 80 (30 originais + 50 novas).

---

## 2. Roteiro Passo a Passo de Execução

### Passo 1: Executar Script Python de Registro
Executar o script Python de scratch para atualizar o `registry.json`.

### Passo 2: Executar Script de Validação
Rodar um comando de teste/validação via PowerShell ou Python para checar a integridade do JSON gerado.

---

## 3. Critérios de Sucesso
- `registry.json` modificado com sucesso e com sintaxe válida.
- 50 novas skills inseridas de forma estruturada no array `"skills"`.
- `"last_updated"` atualizado no cabeçalho.
