# ADR-0008: Evolução da Governança de Skills (Stout Elite vs. Sentinel)

**Status:** Proposto
**Data:** 2026-05-15
**Autor:** Gemini CLI Agent (Stout Architect)

## 1. Contexto

Historicamente, o `skill-sentinel` (global) era a ferramenta de auditoria. Com o avanço do ecossistema para o **Roadmap V6.0**, implementamos o sistema de Elite Stout (`stout-skill-registry`, `stout-skill-auditor` e `stout-improve-skill`). Precisamos validar se o novo sistema substitui o Sentinel e como as novas skills locais performam.

## 2. Resultados da Avaliação Comparativa

### 📊 Skill Sentinel (Legado/Global)

- **Foco:** Métricas técnicas (Linhagem de código, complexidade, segurança de arquivos).
- **Veredito:** Classifica as skills locais com scores medianos (ex: `stout-immunity-gate` com 76/100) devido à falta de documentação exaustiva no frontmatter.
- **Ponto Fraco:** Não entende o "negócio" da skill; apenas a forma técnica.

### 🛡️ Stout System (Elite/Local)

- **Foco:** Papéis semânticos, overlaps funcionais e governança agêntica.
- **Veredito:** Detecta overlaps críticos que o Sentinel ignora (ex: 56% de sobreposição semântica entre `immunity-gate` e novas intenções de `guardrail`).
- **Score de Elite:** Atribui scores de maturidade funcional (ex: `stout-skill-registry` com 96.2/100).

## 3. Diferenças Pontuadas

| Dimensão | Skill Sentinel | Stout Elite System | Impacto |
| :--- | :--- | :--- | :--- |
| **Inteligência** | Técnica (Linting) | Semântica (Role-based) | Stout evita duplicidade de competência. |
| **Ação** | Passiva (Report) | Ativa (Decision & Patch) | Stout refatora e melhora automaticamente. |
| **Governança** | Unilateral | Colaborativa (Human-in-the-Loop) | Stout exige [Y/N] para mudanças críticas. |
| **Ledger** | Não possui | `registry.json` (Imutável) | Stout garante rastreabilidade histórica. |

## 4. Plano de Melhoria (Roadmap V6.1)

Para elevar as skills atuais ao Padrão Ouro de Elite, propomos:

1.  **Uniformização de Frontmatter:** Todas as skills devem adotar o schema v1.2 detectado pelo `diag_runner.py` (incluindo `version`, `author`, `triggers` exaustivos).
2.  **Depreciação do Sentinel Local:** O Sentinel será mantido apenas como uma MCP de leitura para auditoria externa. A decisão de criação/melhoria será 100% via `stout-skill-auditor`.
3.  **Tuning da Fábrica:** Integrar o `diag_runner.py` diretamente no `stout-create-skill` para que nenhuma skill nasça com score de documentação abaixo de 90.

## 5. Conseqüências

- **Positivas:** Redução drástica de ambiguidade; skills mais leves e eficientes; ecossistema auto-gerenciável.
- **Negativas:** Exige maior rigor na fase de Strategy/Brainstorming.

---
*Assinado: Arquiteto de Design Agêntico*
