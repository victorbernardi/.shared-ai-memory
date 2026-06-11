# Plano de Implementação: Saneamento e Migração em Massa de Robustez de Session-Learning

> **ID de Governança**: stout_mass_session_learning_retrofit  
> **Status**: [Aguardando Aprovação Humana]  
> **Autor**: Engenheiro Stout / Gemini CLI  
> **Data**: 2026-05-27  

---

## 1. Contexto & Objetivos

Após a validação, implementação e testes com 100% de sucesso das correções de robustez SQLite e transacional no módulo central `stout-memory-capture.py` no workspace ativo, precisamos disseminar essa maturidade técnica para todos os projetos legados e ativos do ecossistema que utilizam ou possuem cópias desse script em suas pastas de ferramentas, além de atualizar as Golden Copies globais do host.

Isso garante a homogeneidade estrutural do ecossistema Stout/Inova, evitando incidentes de concorrência global e erros de transação pendente zumbi em outros repositórios de produção.

---

## 2. Mapeamento de Alvos Físicos

Varremos o host recursivamente e localizamos exatamente **10 arquivos ativos e de referência** que necessitam ser migrados para o novo padrão de robustez consolidado.

### Origens de Sincronização (Workspace Ativo)
* **Origem de Produção (O1)**: `skills/stout-session-learning/scripts/stout-memory-capture.py`  
* **Origem de Template (O2)**: `skills/stout-init/addons/cdd/templates/tools/stout_memory_capture.py`  

### Destinos e Ações de Substituição

#### A. Versão de Produção (O1) → Alvos Legados Equivalentes:
1. `Research/lessons_learned/stout-memory-capture.py` (Local)
2. `C:/Projetos/Inova/projects/pricewatch-jd/Research/lessons_learned/stout-memory-capture.py` (Cópia antiga)
3. `C:/Projetos/Inova/projects/lead-csc-pops/src/tools/stout_memory_capture.py` (Ativo no lead-csc-pops)
4. `C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/Research/lessons_learned/stout-memory-capture.py` (Cópia antiga)
5. `C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/.commandcode/skills/stout-session-learning/scripts/stout-memory-capture.py` (Ativo no 02_Faturamento)
6. `C:/Users/victor.bernardi/.shared-ai-memory/skills/stout-session-learning/scripts/stout-memory-capture.py` (Golden Copy Global de Produção)

#### B. Versão de Template (O2) → Alvos de Templates Equivalentes:
7. `C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/.commandcode/skills/stout-init/addons/cdd/templates/tools/stout_memory_capture.py` (Template ativo no 02_Faturamento)
8. `C:/Users/victor.bernardi/.shared-ai-memory/skills/stout-init/addons/cdd/templates/tools/stout_memory_capture.py` (Golden Copy Global de Scaffolding)

---

## 3. Estratégia de Execução

Criaremos um script Python temporário em `scratch/mass_migration_helper.py` que efetuará as cópias de arquivos usando `shutil.copy2` (para preservar metadados de modificação). A execução em massa será realizada de forma atômica no terminal do host usando a instrução `BypassSandbox: true` para podermos ter acesso de gravação a diretórios externos.

---

## 4. Plano de Verificação

### Validação Física
- Verificar a presença e o tamanho dos arquivos gerados nos subprojetos.
- Rodar a suite de testes unitários locais (`pytest tests/test_session_learning.py -v`) para confirmar que a versão de origem local e o template estão 100% consistentes.

### Saneamento de Encoding
- Garantir que todos os arquivos saneados mantenham o encoding UTF-8 puro (sem BOM), eliminando Mojibakes nos projetos legados.
