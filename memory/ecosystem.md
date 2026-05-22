# Ecossistema — Victor Bernardi

## Quem sou

Analista/engenheiro de dados da **Inova AI**. Trabalho com análise de dados, modelagem financeira e construção de ecossistema de AI tooling para uso interno e pessoal.

- Email: victorotaviob@icloud.com
- Idioma principal: PT-BR (toda comunicação, documentação e código comentado em português)

---

## Mapa do Ecossistema

### Stout (`C:\Projetos\Stout`)
Source of truth de todo o AI tooling. Onde agents, skills, workflows e rules são criados e mantidos.
- **Motor:** OpenCode (modelos OpenAI — gpt-5.2 para planning, gpt-5.1-codex para coding)
- **Não é uma aplicação** — sem build pipeline, sem CI/CD no root
- Qualquer modificação de AI tooling passa pelo Stout

### Antigravity (`C:\Users\victor.bernardi\.gemini\`)
Ferramenta diária de análise da Inova. Lê agents/skills do Stout (via junction).
- Usado para análises do dia a dia na Inova
- **Não recebe edições diretas** — toda modificação vai para o Stout primeiro

### Inova (`C:\Projetos\Inova`)
Workspace do projeto Inova AI — datasets, scripts de análise, notebooks.
- Apenas código de negócio — sem AI tooling próprio
- Dados financeiros, modelos de análise, pipelines de dados

### wiki-compiler (`C:\Projetos\Stout\wiki-compiler\`)
Sistema autônomo que transforma logs de sessões em wiki estruturada no Obsidian.
- Vault Obsidian: `C:\Users\victor.bernardi\Documents\Obsidian-Victor-Global\`
- Gera `SUGESTOES-HOJE.md` com sugestões do Córtex
- Lê de `wiki/raw/` → compila para `wiki/`

### Córtex
Agente de evolução do ecossistema. Gera sugestões de melhoria em `SUGESTOES-HOJE.md`.
- Roda diariamente às 08h
- Sugestões fluem: Córtex → SUGESTOES-HOJE.md → usuário decide → implementa ou descarta

### Consulta da Wiki
- `INDEX.md` primeiro.
- Nota consolidada depois.
- `wiki/raw/` apenas como fallback sujo e transitório.

### Everything Claude Code (ECC) (`Plugins/everything-claude-code/`)
Plugin público de skills/agents para múltiplos IDEs. Repositório separado — não modificar sem impacto em usuários externos.

---

## Projetos Ativos

### Knowledge Graph → Obsidian (implementado em 2026-04-17)
Extração de entidades e mapeamento de relações via `librarian_policy.md` no Antigravity.
- Trigger Gamma detecta entidades e relações durante sessões
- Vocabulário de 7 tipos de relação: evolução de, substitui, implementa, alimenta, pertence a, usado por, baseado em
- Feature ativa — não reabrir como pendência

### Agente de Rastreamento (pendente — alta prioridade)
Gap crítico: sugestões do Córtex não têm rastreamento sugestão→decisão→plano→implementação.
- Fluxo esperado: lê SUGESTOES-HOJE.md → pergunta ao usuário (implementar/rejeitar/adiar) → aprovadas criam tarefa + plano no Stout → implementadas geram handoff para wiki
- Prioridade: próxima sessão de planejamento do ecossistema

### Transição Claude Code → OpenCode (em andamento — 2026-04-22)
Stout passa a usar OpenCode como motor de coding. Claude Code continua como ferramenta de gestão/planejamento.
