# Walkthrough - Refatoração Notion PARA (Fase 1)

Concluímos com sucesso a **Fase 1** da migração dos seus bancos de dados do Notion para o modelo PARA. Todos os campos estruturais foram criados e estão prontos para uso.

## ✅ O que foi feito

### 1. Áreas da Vida
- **Status:** Validado.
- **Estrutura:** Confirmada a existência dos campos `Nome` (Title) e `Descrição` (Rich Text).

### 2. Meus Projetos
- **Novas Propriedades:**
  - `Área da Vida` (Select): Com as opções canônicas (Trabalho, Estudo, Finanças, Vida Pessoal, Second Brain).
  - `Organização` (Select): Com opções (Inova Máquinas, Seedz, Pessoal, Outro).
- **Consistência:** O banco agora permite a filtragem e agrupamento por eixos transversais.

### 3. Pendências / Próximos Passos
- **Novas Propriedades:**
  - `Área da Vida` (Select).
  - `Organização` (Select).
  - `Hoje` (Formula): **Automação de Foco Diário** implementada.
- **Lógica da Fórmula `Hoje`:**
  - A marcação ocorre automaticamente se:
    1. O `Status` não for "Concluído" ou "Concluída".
    2. O `Prazo` for menor ou igual a hoje (atrasado ou para hoje).

### 4. Minhas Notas
- **Novas Propriedades:**
  - `Título` (Title): Renomeado para clareza.
  - `Tipo de Nota` (Select): Conhecimento, Decisão, Retrospectiva, Log / Diário, Handover.
  - `Área da Vida` (Select) e `Organização` (Select).
  - `Data` (Date).
- **Nota técnica:** Este banco exigiu o uso da versão mais recente da API do Notion (`2025-09-03`) devido à sua estrutura de múltiplas fontes de dados.

## 🛠️ Script de Automação
O script utilizado para realizar as mudanças foi salvo em:
- [refactor_notion_phase1.py](file:///C:/Projetos/OpenCode/scripts/refactor_notion_phase1.py)

---

## 🚦 Próximos Passos sugeridos

1. **Validação na UI:** Verifique se as novas colunas aparecem nas suas Views favoritas.
2. **Preenchimento Piloto:** Comece a preencher os campos `Área da Vida` e `Organização` nos projetos e tarefas ativos.
3. **Ajuste de Relações:** Como a API tem restrições em criar relações bidirecionais entre bases existentes, verifique se as conexões entre Projetos ↔ Tarefas ↔ Notas estão ativas na interface.
4. **Fase 2 (Limpeza):** Quando você se sentir confortável com o novo modelo, podemos prosseguir para a exclusão dos campos legados (`Contexto`, `Metodologia`, etc.).

> [!TIP]
> Você já pode usar a nova View de **Foco Diário** filtrando pelo campo `Hoje = true` no banco de Pendências!
