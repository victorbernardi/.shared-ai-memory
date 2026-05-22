# Plano de Implementação: Unificação da Arquitetura de Memória Stout

## 1. Background & Motivation
Atualmente, o ecossistema Antigravity sofre com fragmentação de memória e padrões de diretórios devido a:
1. O pipeline de ingestão ignora a pasta `tmp` do Gemini CLI.
2. O Claude persiste no uso da pasta legada `docs/superpowers/`.
3. A skill `stout-init` falha em criar junctions (links simbólicos) para a memória global se a pasta `docs/` local já contiver arquivos, ilhando o conhecimento.
4. Duplicidade conceitual entre as pastas `src/` e `scripts/`.

## 2. Scope & Impact
Este plano visa centralizar a "Fonte da Verdade" da documentação e unificar a taxonomia entre Gemini CLI, Claude e Antigravity.
**Impacto:** Afetará os scripts de automação (`stout-init`, `stout_promote.py`), a configuração do Claude, e a estrutura de novos projetos. A documentação dos projetos existentes será migrada para a memória global de forma segura.

## 3. Proposed Solution & Decisões
- **Docs Junction Migration:** Um novo script (`force_docs_junction.py`) será criado para mover fisicamente arquivos da pasta `docs/` local para `~/.shared-ai-memory/docs/<projeto>/` e então criar o junction, garantindo zero perda de dados. A skill `stout-init` usará esta lógica.
- **Erradicar Legado Claude:** O arquivo `CLAUDE.md` e as diretrizes globais serão atualizadas para proibir a pasta `superpowers/` e direcionar o output de planejamento estritamente para `docs/plans/` e `docs/specs/`.
- **Gemini TMP Promotion:** O script `stout_promote.py` será atualizado para escanear a pasta `.gemini/tmp/shared-ai-memory/*/plans/` e copiar planos aprovados para a pasta `docs/plans/` do projeto em que o agente está operando.
- **Unificação SRC:** A skill `stout-init` será atualizada para não gerar mais a pasta raiz `scripts/`. Automações e ferramentas internas residirão em `src/tools/` ou similares.

## 4. Implementation Steps

### Fase 1: Governança e Diretrizes (Claude & Stout-Init)
1. Editar `C:\Projetos\Inova\CLAUDE.md` (e qualquer configuração global do Claude) para remover referências a `superpowers` e instruir o salvamento em `docs/plans/` e `docs/specs/`.
2. Atualizar `C:\Users\victor.bernardi\.shared-ai-memory\.gemini\skills\stout-init\SKILL.md` para remover a criação da pasta `scripts/` e instruir a unificação em `src/`.
3. Atualizar a skill `process-brainstorming` (se necessário) para refletir essas mudanças.

### Fase 2: Scripting (Migração e Promoção)
1. Criar o script `C:\Users\victor.bernardi\.shared-ai-memory\scripts\force_docs_junction.py`. Este script deve:
   - Receber o caminho base do projeto.
   - Verificar se `docs/` existe e é uma pasta comum.
   - Mover seu conteúdo (preservando estrutura) para `~/.shared-ai-memory/docs/<projeto>/`.
   - Excluir a pasta local `docs/` e criar o junction (usando `mklink /J` no Windows).
2. Modificar `C:\Users\victor.bernardi\.shared-ai-memory\scripts\stout_promote.py` para:
   - Identificar a última sessão ativa na pasta `.gemini/tmp/shared-ai-memory/` (ou iterar sobre os UUIDs).
   - Buscar por arquivos `.md` gerados lá que pareçam planos.
   - Promovê-los para o `docs/plans/` do projeto local.

### Fase 3: Execução e Geração de Spec
1. Rodar o script `force_docs_junction.py` no projeto `C:\Projetos\Inova\projects\Historico-de-Vendas` para migrar sua pasta `docs/` ilhada para a memória global.
2. Gerar a Especificação Oficial (`docs/specs/2026-05-12-unificacao-memoria-stout.md`) para formalizar a nova taxonomia.

## 5. Verification & Testing
- Validar se o `Historico-de-Vendas` agora possui um junction em `docs/` apontando corretamente para o shared-ai-memory.
- Executar `python stout_promote.py` e confirmar se ele consegue ler da pasta `tmp` do Gemini (mockar um plano na tmp para testar).
- Revisar `CLAUDE.md` para garantir a extinção da nomenclatura "superpowers".