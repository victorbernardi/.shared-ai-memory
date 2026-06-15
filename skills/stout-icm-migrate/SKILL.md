---
name: stout-icm-migrate
description: "Converte projetos legados para o formato ICM nativo com estágios numerados e contratos explícitos (CONTEXT.md). Detecta estrutura atual, classifica research por conteúdo, cria pipeline com gates de auditoria. Use quando for migrar projeto existente, ICM-izar, converter para pipeline ICM, ou adaptar estrutura. Triggers: migrar projeto, converter para ICM, icm-izar, adaptar estrutura."
version: 1.1.0
author: Arquiteto Stout
tier: 3
category: meta-governance
date_added: "2026-05-27"
---

# Stout ICM Migrate

## Propósito

Converter projetos legados (CDD monolíticos ou scripts procedurais) para o formato ICM nativo com estágios numerados e contratos explícitos (`CONTEXT.md`).

---

## Processo de Migração (8 Passos)

### Passo 0: Verificar Integridade (NOVO)

**Antes de qualquer mudança estrutural, o projeto precisa rodar no estado atual.**

**Verificação do ambiente Python (obrigatório):**

1. Verificar se `.venv` existe no diretório do projeto:
   - Se NÃO existe: criar com `uv venv --python 3.12`
2. Se existe `requirements.txt`: instalar deps com `uv pip install -r requirements.txt`
3. Se NÃO existe `requirements.txt`: gerar via `uvx pipreqs . --encoding utf-8 --force --ignore tests,sandbox`
4. Validar: `uv run python -c "import sys; print(f'Python {sys.version[:5]} OK')"`

**Verificação do entry point:**

- Executar o entry point atual com `uv run python <script> --help` ou `uv run python <script> --dry-run`
- Se falhar com `ModuleNotFoundError` ou `ImportError`: **ABORTAR migração**
- Listar dependências ausentes para o operador corrigir primeiro
- Se rodar com sucesso: capturar output como **baseline** de comportamento esperado
- Verificar se `.env` está presente com credenciais válidas

**Motivo:** Aprendido na migração do Inova-Daily — `db_utils.py` sumiu do `src/`, o pipeline não rodava em formato nenhum. Migrar um projeto quebrado só multiplica os problemas.

**NÃO assumir** que o Anaconda está disponível. Usar `uv run python` em vez de `python` em todos os comandos.

---

### Passo 1: Detectar Estrutura Atual

- Analisar o diretório do projeto legado
- Identificar: entry points, scripts existentes, arquivos de configuração, módulos Python
- Mapear o fluxo de execução atual (ordem de chamadas, dependências entre módulos)
- Listar arquivos de identidade existentes (`GEMINI.md`, `CLAUDE.md`, `ANTIGRAVITY.md`, `CONTEXT.md`)
- Verificar se o domínio (Stout ou Inova) tem `REFERENCES.md` e `.GCC/`

---

### Passo 2: Planejar Estágios ICM

- Decompor o fluxo procedural em estágios sequenciais numerados (01, 02, 03, ...)
- Cada estágio deve ter **um único propósito** claro
- Se um propósito precisar de mais de uma frase, divida em dois estágios
- Identificar quais scripts pertencem a qual estágio
- **Se o projeto original tem validação/auditoria entre etapas, isso vira um estágio GATE**
- Documentar se o projeto original tem flag `--force` — isso vira `FORCAR_VALIDACAO=true` no CONTEXT.md

**Exemplo real (Inova-Daily):**

```
run_daily.py → 5 estágios ICM:
  01_extrair  (M2 + snapshot + recap + scanners)
  02_auditar  (validar_snapshot + validar_recap + reconciliar_fontes) ← GATE
  03_gerar    (gerar_email com template)
  04_validar  (validar_markdown) ← GATE
  05_exportar (salvar output + audit NF)
```

---

### Passo 3: Classificar e Organizar Research

**Pesquisa não é lixo — mas precisa ser classificada por conteúdo.**

Para cada arquivo em `research/` (ou equivalente):

| Tipo de arquivo | Critério | Destino |
|-----------------|----------|---------|
| `.md`, `.pdf` | Qualquer conteúdo | `00_research/references/` |
| `.py` com **paths reais do sistema** | Contém `C:\`, `FABRIC_`, `data/audit/`, paths de produção | `src/` ou `src/scanners/` |
| `.py` **genérico** (modelo) | Sem paths reais — classe abstrata, exemplo, template | `00_research/references/` |
| `.zip`, `.png`, `.csv`, `.xlsx` | Assets de referência | `00_research/references/` |

**Regra de ouro:** Se o script referencia `C:\Projetos\Inova\`, `FABRIC_SERVER`, `data/audit/nf_*.parquet` — é código de produção. Vai para `src/`. Se é uma classe genérica sem caminhos reais — é referência. Fica em `00_research/references/`.

**Motivo:** Aprendido na migração do Inova-Daily — `auditoria_cc.py` e `classificar_canais.py` estavam em `research/` mas continham paths reais do sistema. O agente original não sabia onde salvar.

---

### Passo 4: Criar Estrutura de Diretórios

- A estrutura nasce DENTRO do diretório do projeto existente (`<dominio>\Projetos\<projeto>\`)
- Criar `00_research/` com `CONTEXT.md` (cold storage) e `references/`
- Organizar pesquisas classificadas no passo 3 em `00_research/references/`
- Criar subdiretórios numerados: `01_<estagio>/`, `02_<estagio>/`, ...
- Cada estágio recebe: `CONTEXT.md`, `output/`, `scripts/` (se aplicável)

**Ambiente Python (obrigatório):**

1. Criar `requirements.txt` na raiz do novo workspace com as dependências detectadas no Passo 0
2. Se um estágio tem dependências exclusivas: criar `requirements.txt` dentro do estágio
3. Criar `.venv` na raiz do projeto:

```powershell
cd <novo-workspace-icm>
uv venv --python 3.12
uv pip install -r requirements.txt
```

---

### Passo 5: Extrair Contratos

- Do entry point original, extrair a lógica de orquestração
- Do `SKILL.md` original (se existir), extrair regras e instruções
- Do `GEMINI.md` / `CLAUDE.md` do projeto, extrair regras locais
- Redistribuir nos CONTEXT.md dos estágios correspondentes:
  - Regras de negócio → CONTEXT.md do pipeline
  - Restrições operacionais → CONTEXT.md do estágio específico
  - Paths e configurações → `scripts/` do estágio (importam de `src/config.py`)
- Sempre usar o template de CONTEXT.md (8 seções obrigatórias) de `@../_shared-icm-templates/CONTEXT.stage.md`
- Usar template de pipeline em `@../_shared-icm-templates/CONTEXT.pipeline.md`

---

### Passo 6: Mover Scripts

- **COPIAR** (NUNCA mover) scripts de `src/` para `scripts/` do estágio correto
- Scanners e módulos de domínio → `scripts/` do estágio que os consome
- Scripts compartilhados por múltiplos estágios → `src/` (permanecem no local original)
- Verificar encoding UTF-8 em todos os scripts copiados
- Garantir permissão de execução
- Scripts originais em `src/` permanecem intactos para compatibilidade
- Templates → `templates/` dentro do estágio que os consome

**Após mover scripts, reinstalar deps (se necessário):**

```powershell
cd <estagio-com-scripts>
uv pip install -r ../requirements.txt  # herda deps da raiz
# ou se tem requirements.txt próprio:
uv pip install -r requirements.txt
```

**Validar que o estágio roda no novo ambiente:**

```powershell
uv run python scripts/<script_principal>.py --help
```

---

### Passo 6.5: Injetar CDD (opcional)

**Se o projeto legado tinha CDD, ou se o operador optar por habilitar:**

- Seguir as instruções de `@../stout-init/addons/cdd/ADDON.md` na seção Installation Steps
- Destino da infra: `_config/` (não `src/` — legado)
- Stitching: injetar blocos CDD no `CLAUDE.md` do projeto (seções Governança e Ferramentas)
- Se o projeto legado tinha `data/config/rules.yaml`: mover para `_config/config/rules.yaml`

---

### Passo 7: Criar Envelope Fino

- Criar `SKILL.md` na raiz do projeto com apenas YAML frontmatter + apontadores
- A `description` deve conter triggers semânticos claros
- Máximo 10 linhas no corpo

**Template padrão ICM-CDD (usar `@../_shared-icm-templates/SKILL.thin.md` como base):**

```yaml
---
name: <nome-do-projeto>
description: "<Descrição semântica com triggers.>"
---

# Identidade do workspace: ./CLAUDE.md (Layer 0 — regras globais, mapa ICM)
# Ponteiro Codex/OpenAI:   ./AGENTS.md
# Contrato do pipeline:    ./CONTEXT.md (Layer 1 — ordem dos estágios, regras do pipeline)
```

**Se o domínio NÃO tem `REFERENCES.md`:**

```yaml
# Caminhos canônicos: ./_config/config.py (fallback até REFERENCES.md ser criado na raiz do domínio)
# Pipeline: CONTEXT.md
```

**Motivo:** Aprendido na migração do Inova-Daily — o domínio Inova ainda não tem `REFERENCES.md` nem `.GCC/`. Os ponteiros usam arquivos locais do projeto como fallback.

---

### Passo 8: Atualizar Roteamento

- Se o projeto tem entrada em `_config/config/skills_catalog.yaml` (ou `data/config/skills_catalog.yaml` legado), atualizar:

  ```yaml
  <nome-skill>:
    status: migrated
    icm_workspace: <caminho-do-projeto>
    legacy_entry_point: archived
    migrated_at: <YYYY-MM-DD>
  ```

- Adicionar aviso de arquivamento no entry point original:

  ```markdown
  > [ARQUIVADO: migrado para pipeline ICM — ver CONTEXT.md na raiz do projeto]
  ```

---

## Regras de Migração

- **NUNCA** deletar o código original — apenas adicionar aviso de arquivamento
- **NUNCA** quebrar caminhos de scripts — scripts copiados, não movidos
- **SEMPRE** preservar encoding UTF-8 em todos os arquivos
- **SEMPRE** validar que o projeto roda antes de migrar (Passo 0)
- **SEMPRE** classificar research por conteúdo, não por localização (Passo 3)
- **NUNCA** modificar `GEMINI.md`, `CLAUDE.md` ou `REFERENCES.md` da raiz do domínio
- **Se o domínio não tem REFERENCES.md nem .GCC/:** usar arquivos locais do projeto como fallback e documentar a pendência
- **SEMPRE** usar `uv run python` em vez de `python` em todos os comandos de validação

---

## GATE e FORCAR_VALIDACAO

Se o projeto original tem flag `--force` ou equivalente:

- O estágio de auditoria SEMPRE bloqueia o pipeline quando `passed: false`
- `FORCAR_VALIDACAO=true` permite prosseguir mesmo com falhas (equivale a `--force`)
- Documentar no CONTEXT.md do pipeline e no CONTEXT.md do estágio GATE
- Ambos os CONTEXT.md devem referenciar a flag com a mesma sintaxe

**Exemplo no CONTEXT.md do pipeline:**

```markdown
## Regras do Pipeline
- GATE no estágio 02: Se audit.json retornar passed: false, pipeline BLOQUEIA
- FORCAR: Se FORCAR_VALIDACAO=true, ignore o gate e prossiga com alerta
```

---

## Templates

- `@../_shared-icm-templates/CONTEXT.stage.md` — Template de CONTEXT.md de estágio (8 seções, com L3/L4)
- `@../_shared-icm-templates/CONTEXT.pipeline.md` — Template de CONTEXT.md de pipeline
- `@../_shared-icm-templates/CLAUDE.md.template` — Layer 0 do workspace
- `@../_shared-icm-templates/AGENTS.md.template` — Ponteiro fino Codex/OpenAI
- `@references/migration-checklist.md` — Checklist completo de migração

## Idioma

Obrigatório o uso de **Português (PT-BR)** para todos os artefatos de governança.

## Escopo

Esta skill se aplica à migração de projetos legados para o formato ICM nativo.
