# Plano de Execução: Arquivamento de Skills Não Utilizadas (v1)

## 1. Escopo das Tarefas

### Tarefa 1: Atualização do Ledger (`registry.json`)
- **Ação:** Atualizar o status das 15 skills `stout-*` listadas na especificação de `"status": "active"` para `"status": "deprecated"`.
- **Campos adicionais:** 
  - `"updated_at": "2026-06-18"`
  - `"notes": "Arquivado em lote em 2026-06-18 a pedido do usuário."`
- **Arquivo:** `C:\Users\victor.bernardi\.shared-ai-memory\skills\stout-skill-registry\registry.json`

### Tarefa 2: Movimentação Física das Pastas de Skills
- **Ação:** Mover as 80 pastas listadas do diretório `C:\Users\victor.bernardi\.shared-ai-memory\skills` para `C:\Users\victor.bernardi\.shared-ai-memory\skills\_archived`.
- **Estratégia:** Utilizar um script PowerShell robusto para mover cada pasta individualmente, tratando casos onde a pasta de destino já exista (sobrescrevendo se necessário) para evitar interrupções.

### Tarefa 3: Validação
- **Ação 1:** Verificar se o arquivo `registry.json` continua com sintaxe JSON válida.
- **Ação 2:** Validar a presença das pastas movidas dentro do diretório `_archived` e sua ausência no diretório pai (`skills`).

---

## 2. Roteiro Passo a Passo de Execução

### Passo 1: Executar Script de Modificação do `registry.json`
Criar e executar um script em Python temporário na pasta `scratch` para atualizar o arquivo `registry.json` de forma limpa e segura (garantindo formatação correta e validação sintática do JSON).

### Passo 2: Executar Script de Movimentação Física
Executar comando PowerShell no terminal para realizar a movimentação das 80 pastas listadas de forma segura.

### Passo 3: Executar Preflight de Validação
Rodar um script de verificação de integridade em Python para certificar a consistência estrutural.

---

## 3. Critérios de Sucesso
- `registry.json` atualizado e sintaticamente válido.
- As 80 skills físicas movidas com sucesso para `_archived`.
- O ecossistema Stout continuando operável (sem quebra de dependências essenciais de governança, pois `stout-skill-registry` e `stout-skill-manager` não foram arquivadas).
