# Plano de Implementação: Promoção Automática de Artefatos (Padrão Stout) - FINAL

Este plano descreve a execução técnica baseada na **Spec v1** de 2026-05-06.

## User Review Required

> [!IMPORTANT]
> Após a validação local neste projeto, realizaremos a promoção para a Golden Copy (`C:\Motores-LLM`) para que todos os futuros projetos já herdem essa capacidade.

## Proposed Changes

### [Component] Script de Automação
#### [MODIFY] [stout_promote.py](file:///c:/Projetos/Inova/john-deere-api-project-template/scripts/stout_promote.py)
- **Correção de Encoding:** Substituir `✓` por `[OK]` e tratar caracteres especiais.
- **Validação Cross-Project (Anti-Contaminação):** Ao listar as sessões do `brain/`, varrer o arquivo `.system_generated/logs/overview.txt` para garantir que a sessão contenha a string do caminho do projeto atual (`PROJECT_ROOT`). Ignorar sessões de outros projetos.
- **Idempotência e Prevenção de Sobrescrita:** Se o arquivo de destino já existir, adicionar um sufixo numérico (ex: `-v2`, `-v3`) para evitar a perda de planos feitos no mesmo dia.
- **Nomenclatura:** Aplicar padrão `YYYY-MM-DD-{projeto}-{tipo}.md`.
- **Limpeza:** Remover sufixo `.response`.
- **Mapeamento:**
    - `implementation_plan.md.resolved` -> `./docs/plans/`
    - `walkthrough.md` -> `./docs/walkthroughs/`

### [Component] Governança Local
#### [MODIFY] [GEMINI.md](file:///c:/Projetos/Inova/john-deere-api-project-template/GEMINI.md)
- Inserir a diretriz de promoção obrigatória após cada ciclo de entrega.

### [Component] Ecossistema Global
#### [MODIFY] `C:\Motores-LLM\gemini-cli\antigravity\skills\process-superantigravity\SKILL.md`
- Atualizar a regra de nomenclatura dos planos para remover o `.response`, alinhando com a nova automação (exigindo apenas `plan_vN_nome.md`).

#### [MODIFY] `C:\Users\victor.bernardi\.gemini\antigravity\skills\stout-init\SKILL.md`
- Adicionar o script ao template de arquivos do scaffolding.
- Atualizar `install_stout_init.py` para incluir o novo arquivo.

## Verification Plan

### Automated Tests
- Executar `python scripts/stout_promote.py` no terminal local.
- Confirmar criação de:
    - `./docs/plans/2026-05-06-john-deere-api-docs-plan.md`
    - `./docs/walkthroughs/2026-05-06-john-deere-api-docs-walkthrough.md`

### Manual Verification
- Testar `stout-init` em uma pasta temporária para garantir que o script e as regras do `GEMINI.md` nasçam de forma correta.
