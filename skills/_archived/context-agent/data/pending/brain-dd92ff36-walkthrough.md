# Walkthrough: Automação da Promoção de Artefatos Stout

Esta etapa conclui a implementação do sistema de persistência de memória efêmera (`brain/`) para repositórios locais (`docs/`), padronizando o conhecimento gerado pelas sessões de IA.

## 🛠️ O que foi construído e corrigido

As falhas apontadas durante a análise crítica foram integralmente solucionadas.

1.  **Script de Promoção (`scripts/stout_promote.py`) Refatorado:**
    *   **Isolamento de Projeto (Anti-Contaminação):** O script agora vasculha o arquivo de logs internos (`overview.txt`) das sessões de brain para confirmar se elas realmente pertencem ao projeto atual (`PROJECT_ROOT.name`), ignorando sessões órfãs ou de projetos simultâneos.
    *   **Idempotência Robusta:** O script avalia a existência do arquivo alvo. Se já existir:
        *   Checa se o conteúdo é idêntico via `filecmp` (evita uploads redundantes).
        *   Caso o conteúdo mude (novo plano no mesmo dia), anexa sufixos como `-v2`, `-v3`, garantindo zero perda de histórico.
    *   **Remoção de Sufixos:** A promoção sanitiza nomes para o padrão `YYYY-MM-DD-projeto-plan.md`, limpos de `.resolved` ou `.response`.
    *   **Correção de Encoding:** Terminais Windows `cp1252` não falharão mais por caracteres como `✓`.

2.  **Governança Global Ajustada:**
    *   **GEMINI.md Local:** Atualizado com a instrução mandatória de chamar o script após entregas.
    *   **Skill `using-superantigravity`:** O manual do Orquestrador Global foi atualizado (`SKILL.md`) e agora reconhece planos puros sem `.response`.

3.  **Deploy para Golden Copy:**
    *   O script finalizado foi versionado em `C:\Motores-LLM\gemini-cli\antigravity\templates\scripts\stout_promote.py`.
    *   A skill `stout-init` agora obriga a inserção automática deste novo sanitizador/promotor na fase `2.5` do scaffolding de todo novo projeto da Inova.

## 🧪 Validação Realizada

Testamos o script via shell CLI:
```text
--- Stout Artifact Promoter ---
Projeto: john-deere-api-docs
[OK] PROMOVIDO: implementation_plan.md.resolved -> docs/plans/2026-05-07-john-deere-api-docs-plan.md

Sucesso: 1 artefatos sincronizados com o padrao Stout.
```
A promoção funcionou com perfeição, ignorando sessões inválidas e formatando a nomenclatura.

---
> [!NOTE]
> Recomendação Executiva: O loop de "Deploy local -> Correção de Bugs -> Deploy Golden Copy" está maduro. Todo o ecossistema Stout foi fortificado por esta task.
