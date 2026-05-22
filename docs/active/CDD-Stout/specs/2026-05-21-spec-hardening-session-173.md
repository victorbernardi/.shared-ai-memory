# Spec: Hardening CDD — Sessão 173

**Data:** 2026-05-21
**Origem:** Brainstorming sobre TODO.md + failure-log.md
**Status:** Aprovado

---

## 1. Objetivo

Corrigir 6 fragilidades do motor CDD identificadas pelo failure-log e pelo grill do AGENTS.md, eliminando falhas recorrentes de ambiente (Windows), governança e rastreabilidade.

## 2. Requisitos

### Funcionais
1. **Testes com skip condicional:** `test_guardrail_v2.py` e `test_e2e_integration.py` devem pular testes que dependem de ferramentas externas (git, docker) quando indisponíveis
2. **Launcher.py resiliente:** Substituir path frágil (`CDD_PROJECT_SKILLS_DIR.parent.parent`) por variável de ambiente ou arquivo de configuração
3. **Catálogo sincronizado:** Atualizar `skills_catalog.yaml` (18 entradas) para refletir as 24 skills em `skills/`
4. **Import guard nas ferramentas:** `sentinel_agent.py`, `gcc_analytics.py`, `rule_simulator.py` devem verificar dependências (PyYAML, jinja2, plotly) antes de executar
5. **Templates sincronizados:** `stout_promote.py` e `post_approve.py` em `src/tools/` devem estar replicados nos templates do `stout-init/addons/cdd/templates/tools/`
6. **Skills sem conteúdo:** Remover as 4 skills casca vazia (`cdd_technical_skill`, `self_healing_skill`, `stout_knowledge_fallback`, `welcome_skill`) descartadas na session-165

### Não-Funcionais
- Mudanças cirúrgicas — tocar apenas nos arquivos necessários
- Seguir Karpathy Laws (simplicidade, sem overengineering)
- Usar `replace`, não `write_file`, em arquivos existentes
- Código em inglês, gerenciamento da sessão em PT-BR

## 3. Arquitetura

### Item 1 — Testes
- **Arquivos:** `tests/test_guardrail_v2.py`, `tests/test_e2e_integration.py`
- **Padrão:** Mesmo já aplicado em `test_stout_promote_v3.py`: `_HAS_GIT = shutil.which("git")` + `@pytest.mark.skipif`
- **Risco baixo:** Mudança aditiva, sem quebra de lógica

### Item 2 — Launcher.py
- **Arquivo:** `skills/stout-cdd-orchestrator/scripts/launcher.py`
- **Abordagem:** Substituir `CDD_PROJECT_SKILLS_DIR.parent.parent` por `os.getenv("STOUT_SKILLS_PATH")` com fallback para o comportamento atual
- **Risco médio:** Path resolution pode afetar outros callers

### Item 3 — Catálogo
- **Ferramenta:** `python scripts/audit_skills.py` para gerar diff
- **Ação:** Atualizar `data/config/skills_catalog.yaml` com as 6 skills faltantes
- **Risco baixo:** Operação de sincronização, sem lógica nova

### Item 4 — Import Guards
- **Arquivos:** `src/tools/sentinel_agent.py`, `src/tools/gcc_analytics.py`, `src/tools/rule_simulator.py`
- **Padrão:** Bloco `try/except ImportError` no topo com mensagem clara de `pip install`
- **Risco baixo:** Mudança aditiva no topo do arquivo

### Item 5 — Templates Sync
- **Origem:** `src/tools/stout_promote.py`, `src/tools/post_approve.py`
- **Destino:** `skills/stout-init/addons/cdd/templates/tools/` (local) + golden copy global
- **Risco médio:** Requer verificação de diff antes de sobrescrever

### Item 6 — Remoção de Skills
- **Pastas:** `skills/cdd_technical_skill`, `skills/self_healing_skill`, `skills/stout_knowledge_fallback`, `skills/welcome_skill`
- **Ação:** `rmdir /s /q` em cada uma
- **Risco baixo:** Já decidido na session-165

## 4. Decisões

| Decisão | Alternativas | Por quê |
|---------|-------------|--------|
| `os.getenv` com fallback no launcher | Arquivo `.conf` YAML | Mais simples, sem dependência extra |
| `try/except ImportError` nos guards | `importlib.util.find_spec` | Mais idiomático Python, mensagem direta |
| `audit_skills.py` para diff do catálogo | Atualização manual | Ferramenta já existe, evita erro humano |
| Remover cascas vazias agora | Deixar para depois | Já decidido, só executar |

## 5. Validação

- **Testes:** Rodar `pytest tests/ -v` após cada item; skipif deve reduzir falsos negativos
- **Launcher:** `python skills/stout-cdd-orchestrator/scripts/launcher.py --skill stout-immunity-gate` deve funcionar
- **Catálogo:** `python scripts/audit_skills.py` deve reportar 0 diffs
- **Guards:** Executar cada ferramenta sem dependências instaladas deve mostrar mensagem clara
- **Templates:** `diff src/tools/stout_promote.py skills/stout-init/addons/cdd/templates/tools/stout_promote.py` deve ser vazio
- **Skills:** `dir skills/` deve mostrar 20 skills (24 - 4 removidas)

## 6. Ordem de Execução

1. Testes (skipif) — menor risco, fecha falhas conhecidas
2. Launcher.py — corrige path frágil
3. Catálogo (audit + update) — sincroniza rastreabilidade
4. Import guards — adiciona resiliência
5. Remoção skills casca vazia — limpeza
6. Templates sync — fecha assimetria de scaffolding
