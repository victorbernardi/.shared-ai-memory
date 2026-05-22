# ADR-0007: Vínculo com a Referência Técnica Máxima (Skill Folder Pattern)

## Status
Aceito (2026-05-15)

## Contexto
O projeto **Configuration-Driven Development (CDD)** atua como o motor de orquestração para o ecossistema Stout Inova. Para garantir que a arquitetura dos agentes seja resiliente e evite o "Context Wall", é imperativo que todas as implementações de skills sigam o padrão de engenharia de pastas definido no projeto `Skill Folder Pattern`.

## Decisão
Formalizamos o vínculo técnico entre o projeto CDD e o diretório `C:\Projetos\Stout\Projetos\Skill Folder Pattern`.

1.  **Configuração:** O caminho foi adicionado ao `src/config.py` como `stout_blueprint_path`.
2.  **Governança CDD:** Implementada a regra `stout_architectural_alignment` no `rules.yaml` com prioridade elevada.
3.  **Auditoria:** O `SentinelAgent` deve agora utilizar este blueprint para auditar novas skills criadas no diretório `skills/` local.
4.  **Isolamento:** Adota-se o conceito de "Context Wall" (Divulgação Progressiva) como o padrão ouro para a ativação de habilidades.

## Consequências

### Positivas
- **Integridade Arquitetural:** Garantia de que o projeto CDD não diverge do padrão global da Stout.
- **Eficiência de Tokens:** Adoção rigorosa do Nível 1 (Discovery), Nível 2 (Activation) e Nível 3 (Execution) reduz o inchaço de contexto.
- **Rastreabilidade:** Facilita a auditoria de conformidade por agentes automáticos.

### Negativas
- **Dependência Externa:** O motor CDD agora possui um vínculo explícito com um diretório fora de seu repositório imediato (necessário para governança centralizada).

## Referências
- `C:\Projetos\Stout\Projetos\Skill Folder Pattern\Stout Inova_ Context Wall e Agent Skills.md`
- `GEMINI.md` (Referência Técnica Máxima)
