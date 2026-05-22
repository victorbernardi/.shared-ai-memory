# PLAN: Refatoração da Skill stout-immunity-gate (Especialização)

## 1. OBJETIVO
Transformar a skill `stout-immunity-gate` em um especialista em Governança e Imunidade, removendo todas as responsabilidades relacionadas ao ciclo de vida de desenvolvimento (Research/Plan/Build), que serão delegadas a uma futura skill `cdd-builder`.

## 2. ETAPAS DE REFATORAÇÃO
1. **Limpeza de Escopo:**
    - Remover as seções `Ciclo de Vida Stout v5` (Pesquisa/Estratégia/Execução) da `SKILL.md`.
    - Substituir por `Governança e Auditoria`.
2. **Definição de Responsabilidade:**
    - Explicitamente proibir que a skill tente realizar comandos de build/planejamento.
    - Definir o `Sentinel Agent` como a "Autoridade Máxima" de leitura e log.
3. **Reforço do Protocolo de Imunidade:**
    - Garantir que o `Audit Gate` tenha a precedência sobre qualquer comando.

## 3. CHECKLIST DE CONFORMIDADE
- [ ] A `SKILL.md` reflete apenas governança?
- [ ] As regras de `Protocolo de Ferramentas` estão mantidas?
- [ ] A delegação para `systematic-debugging` está clara?
- [ ] As referências a `cdd-builder` (futura skill) estão postas como "o que não fazer"?

## 4. IMPACTO
- O orquestrador torna-se um componente atômico de segurança, sem "bloatware" de processo criativo.
- Facilita a manutenção da skill global.
- Prepara o terreno para o `cdd-builder` atuar como orquestrador do ciclo de vida.
