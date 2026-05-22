# Memory Index

- [Fabric Database Connector](project_fabric_connector.md) — Conector JDBC/Java para Microsoft Fabric sem admin; auth via AuthenticationRecord persistido em ~/.azure/

- [Transição OpenCode — Concluída](project_opencode_transition.md) — Motor OpenCode operacional desde 2026-04-22 com 5 MCPs, plugins Superpowers+ECC, repo GitHub privado
- [Context Agent](project_context_agent.md) — Skill de continuidade entre sessões OpenCode. Trigger: "encerrar sessão" → rodar save antes de fechar
- [Knowledge Graph → Obsidian](project_knowledge_graph_pending.md) — Implementado em 2026-04-17: extração de entidades + mapeamento de relações no Trigger Gamma
- [Agente de Rastreamento — URGENTE](project_tracking_agent_pending.md) — Gap crítico: sugestões do Córtex não têm rastreamento sugestão→decisão→plano→implementação
- [LLM Wiki — Reforma Z Híbrido](project_llm_wiki_reforma.md) — Reforma do wiki-compiler (2026-04-23): Ar9av como motor, context-agent unificado, reset+rebuild. 5 planos em docs/superpowers/plans/
- [Docs Centralizados — Modelo B + PROJECT_ID](project_docs_centralizados.md) — Centralizar specs/plans em Stout/docs/projects/<id>/. PROJECT_ID verbal por sessão. Implementar após Fase 1.
- [Context-agent Antigravity paths](feedback_antigravity_context_agent_paths.md) — Plans da reforma referenciam path errado; corrigir antes de executar (scripts em context-agent/scripts/, não context-management/context-agent/scripts/)
- [Rotação de tokens pendente](project_token_rotation_pending.md) — GitHub PAT e Tavily key migrados para ~/.credentials/ mas chaves ainda precisam ser rotacionadas
- [Padrão de Credenciais](feedback_credentials_pattern.md) — Tokens sempre em ~/.credentials/*.key, nunca hardcoded; referenciar via ${VAR} nos configs
- [Reestruturação Antigravity — Pendente](project_antigravity_reset.md) — Backup do .gemini criado em C:\Projetos\gemini-backup-2026-04-24\; falta limpar e reinstalar skills do zero
