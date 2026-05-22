# Plano de Ação: Institucionalização do Aprendizado Contínuo no stout-init

**ID:** PLAN-STOUT-LEARNING-001
**Status:** Aguardando Aprovação Final (Plan Mode)

## 1. Visão Geral
Este plano visa evoluir a skill `stout-init` para que todo novo projeto no ecossistema nasça com um kernel de aprendizado contínuo. A implementação centraliza-se no arquivo `LESSONS_LEARNED.md`, garantindo que descobertas técnicas e de negócios sejam persistidas estruturalmente.

## 2. Escopo e Impacto
- **Impacto:** Melhoria na governança de projetos, transferência de conhecimento cross-project e fortalecimento da IA como agente de melhoria contínua.
- **Arquivos-Chave:**
  - `stout-init/SKILL.md`
  - `GEMINI_LOCAL_TEMPLATE.md` (Template raiz)
  - `LESSONS_LEARNED_TEMPLATE.md` (Novo)
  - `install_stout_init.py`

## 3. Passos de Implementação

### Passo 1: Criação do Template Base
Criar o arquivo `LESSONS_LEARNED_TEMPLATE.md` (que residirá junto com os outros templates de referência).
**Estrutura do arquivo:**
- Metadados do Projeto
- 🧠 Aprendizados de Negócio (ex: nuances de dados, KPIs não óbvios)
- ⚙️ Descobertas Técnicas (ex: bugs raros, quirks de bibliotecas, soluções arquiteturais)
- 🔄 Processo e Governança (ex: o que funcionou bem no workflow Antigravity/Stout)

### Passo 2: Atualização do GEMINI.md Local
Adicionar uma nova seção ao `GEMINI_LOCAL_TEMPLATE.md`:
```markdown
## 8. APRENDIZADO CONTÍNUO

> **Obrigatório:** Todo aprendizado relevante deve ser documentado no `LESSONS_LEARNED.md` na raiz do projeto.
- Registre descobertas técnicas que possam beneficiar outros projetos.
- Registre anomalias de dados e regras de negócio não documentadas.
- O Agente de Contexto (se ativado) utilizará este arquivo para consolidar a memória global.
```

### Passo 3: Modificação da Skill `stout-init`
Atualizar o arquivo `SKILL.md` do `stout-init`:
- Na **Fase 2 (Scaffolding Físico)**, incluir `LESSONS_LEARNED.md` na árvore de diretórios.
- Na **Fase 2.5** ou similar, adicionar o passo para copiar o template local para `LESSONS_LEARNED.md`.

### Passo 4: Atualização do Instalador
Modificar o script `install_stout_init.py`:
- Adicionar `"references/lessons-learned-template.md": "LESSONS_LEARNED.md"` ao dicionário `SKILL_FILES`.
- Garantir que o instalador crie o template na hora de instalar a skill nas pastas `.gemini/skills/stout-init/references/`.

## 4. Validação
1. Validar se o instalador roda sem erros (`python install_stout_init.py`).
2. Verificar se o template foi parar no diretório correto.
3. Simular a inicialização de um projeto via `stout-init` mentalmente e via dry-run da criação dos arquivos de scaffolding.

## 5. Reversão e Rollback
Se houver falha, restaurar os arquivos `install_stout_init.py` e `SKILL.md` para seus estados originais via versionamento/backup (Canary Deployment será usado se aplicável).