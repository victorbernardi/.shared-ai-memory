# Fase 4 — Reset + Rebuild do Vault de Produção

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended para esta fase — tem passos destrutivos que exigem checkpoints humanos). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Esvaziar o vault de produção (`Obsidian-Victor-Global/wiki/`) após backup completo, inicializar git nele, e reconstruir o conteúdo passando TUDO (páginas atuais do wiki + histórico de sessões + specs/plans limpos) pela peneira nova e pelo novo motor Ar9av. Validar integridade com audit engine e revisão manual antes do commit final.

**Architecture:** Fase inerentemente destrutiva — backup é obrigatório e validado antes de qualquer operação. Opera em etapas com checkpoint humano entre cada uma: backup → git init → esvaziar → re-seed → compile → audit → revisão → commit. Cada etapa tem validação de reversibilidade (backup existe e é legível? diff antes de commit?). O script orchestrator (`wiki-compiler/run_wiki_work.sh`) já foi construído na Fase 3 — aqui só aponta para produção via env var `VAULT`.

**Tech Stack:** bash, Python 3.13, git. Uso extensivo de `git diff` para validação.

---

## Contexto para o engenheiro

Pré-requisitos:
- Fases 1-3 concluídas e validadas
- Ar9av funcionando end-to-end no test-vault (Task 11 da Fase 3 validada)
- Acesso ao GitHub para criar repo privado novo
- ~500MB livres no backup destino (vault atual tem dezenas de `.md`)

**Paths importantes:**
- **Vault de produção:** `C:\Users\victor.bernardi\Documents\Obsidian-Victor-Global\wiki\`
- **Backup destino:** `C:\Users\victor.bernardi\Documents\Obsidian-Victor-Global\backup\wiki-pre-reforma-YYYY-MM-DD\`
- **Repo git novo** (GitHub privado): `stout-wiki` ou nome que preferir

**Critério de sucesso:**
- Backup verificável (checksum ou file count) antes de qualquer destruição
- Vault reconstruído contém >= 70% das páginas do estado original (perda aceita para duplicatas + páginas poluídas)
- Nenhum link órfão residual no audit report
- Revisão manual em amostra aleatória confirma qualidade

**Pontos de no-go (parar e reverter):**
- Backup incompleto ou corrompido
- Pipeline produz 0 páginas (algo quebrou no re-seed)
- Audit report mostra >= 20% de órfãos (sinal de colapso de wikilinks)
- Amostra revisada revela perda de informação crítica

---

## File Structure

**Será criado:**
- `C:\Users\victor.bernardi\Documents\Obsidian-Victor-Global\backup\wiki-pre-reforma-YYYY-MM-DD\` (diretório de backup — fora do vault)
- `.git/` dentro do vault (repo git inicializado)
- `scripts/reseed/backup_vault.sh`
- `scripts/reseed/validate_backup.py`
- `scripts/reseed/empty_vault.sh`
- `scripts/reseed/reseed_from_backup.sh`
- `scripts/reseed/verify_rebuild.py`

**Será modificado:**
- Vault inteiro (esvaziado + repovoado)
- `wiki-compiler/run_wiki_work.sh` (adicionar modo `--production` que aponta para vault real)

**Será removido (depreciado):**
- `wiki-compiler/harvest_brain.sh` (após validação de Fase 4)
- Escrita direta do Bibliotecário em `raw/_pending/` (atualizar `librarian_policy.md`)

---

## Task 1: Script de backup atômico

**Files:**
- Create: `scripts/reseed/backup_vault.sh`
- Create: `scripts/reseed/validate_backup.py`

- [ ] **Step 1: Escrever script de backup**

Criar `C:\Projetos\Stout\scripts\reseed\backup_vault.sh`:

```bash
#!/bin/bash
# Backup atomico do vault de producao antes do reset.
# Gera checksums de todos os .md para validacao posterior.

set -euo pipefail

VAULT="/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
BACKUP_ROOT="/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/backup"
DATE=$(date +%Y-%m-%d-%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/wiki-pre-reforma-$DATE"

if [ ! -d "$VAULT" ]; then
    echo "ERRO: vault nao existe em $VAULT"
    exit 1
fi

echo "Backup: $VAULT -> $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Copia preservando estrutura e timestamps
cp -r -p "$VAULT"/* "$BACKUP_DIR/" 2>/dev/null || true
cp -r -p "$VAULT"/.[!.]* "$BACKUP_DIR/" 2>/dev/null || true

# Gera manifest com checksums
MANIFEST="$BACKUP_DIR/BACKUP_MANIFEST.txt"
echo "# Backup manifest — $DATE" > "$MANIFEST"
echo "# Source: $VAULT" >> "$MANIFEST"
echo "" >> "$MANIFEST"
(cd "$BACKUP_DIR" && find . -type f -name "*.md" -exec sha256sum {} \;) >> "$MANIFEST"

# Count para validacao rapida
MD_COUNT=$(find "$BACKUP_DIR" -type f -name "*.md" | wc -l)
echo ""
echo "Backup completo:"
echo "  Destino: $BACKUP_DIR"
echo "  Arquivos .md: $MD_COUNT"
echo "  Manifest: $MANIFEST"
echo ""
echo "Exporte o path para uso pelos proximos scripts:"
echo "  export BACKUP_DIR=\"$BACKUP_DIR\""
```

- [ ] **Step 2: Escrever validador de backup**

Criar `C:\Projetos\Stout\scripts\reseed\validate_backup.py`:

```python
"""
Valida integridade do backup:
- Manifest existe e é lido
- Todos os arquivos listados existem no backup
- Checksums batem
- Count de .md no backup >= count no vault original
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


def validate(backup_dir: Path, vault_dir: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    manifest = backup_dir / "BACKUP_MANIFEST.txt"
    if not manifest.exists():
        return False, [f"Manifest ausente: {manifest}"]

    # Parse manifest (linhas `<sha256>  <path>`)
    entries: list[tuple[str, Path]] = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        sha, rel = parts
        entries.append((sha, backup_dir / rel.lstrip("./")))

    # Checksum de cada arquivo
    for sha, path in entries:
        if not path.exists():
            errors.append(f"Arquivo ausente no backup: {path}")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != sha:
            errors.append(f"Checksum divergente: {path}")

    # Count de .md no vault vs backup
    vault_md = len(list(vault_dir.rglob("*.md")))
    backup_md = len(list(backup_dir.rglob("*.md")))
    if backup_md < vault_md:
        errors.append(
            f"Backup incompleto: vault tem {vault_md} .md, backup tem {backup_md}"
        )

    return len(errors) == 0, errors


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: validate_backup.py <backup_dir> <vault_dir>")
        sys.exit(2)
    ok, errs = validate(Path(sys.argv[1]), Path(sys.argv[2]))
    if ok:
        print("Backup VALIDO")
        sys.exit(0)
    print("Backup INVALIDO:")
    for e in errs:
        print(f"  - {e}")
    sys.exit(1)
```

- [ ] **Step 3: Executar backup**

```bash
bash scripts/reseed/backup_vault.sh
```

Anotar o `BACKUP_DIR` impresso.

- [ ] **Step 4: Validar backup**

```bash
python scripts/reseed/validate_backup.py \
    "$BACKUP_DIR" \
    "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
```

Expected: `Backup VALIDO`. Se `INVALIDO`, parar e resolver antes de seguir.

- [ ] **Step 5: Commit scripts**

```bash
git add scripts/reseed/backup_vault.sh scripts/reseed/validate_backup.py
git commit -m "chore: scripts de backup e validacao do vault"
```

**⚠ Checkpoint humano obrigatório:** Confirmar visualmente que `$BACKUP_DIR` existe, contém pelo menos 20 arquivos `.md`, e o `BACKUP_MANIFEST.txt` abre sem erro. **Só proseguir para Task 2 após confirmação.**

---

## Task 2: Git init no vault + remote privado

**Files:**
- Create: `.git/` dentro do vault (via `git init`)
- Create: repo privado no GitHub

- [ ] **Step 1: Inicializar git no path do vault**

```bash
cd "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
git init
git branch -m main
```

- [ ] **Step 2: Criar `.gitignore` básico**

No root do vault, criar `.gitignore`:

```
# Obsidian workspace (não versionar — pessoal)
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/workspaces.json

# OS
.DS_Store
Thumbs.db

# Trash do Obsidian
.trash/

# Sync manifest (runtime, nao conteudo)
.nlm_sync_manifest.json.lock
```

- [ ] **Step 3: Primeiro commit = snapshot do estado atual**

```bash
cd "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
git add .
git commit -m "chore: snapshot pre-reforma do vault (estado 2026-04-23)"
```

- [ ] **Step 4: Criar repo remoto privado**

Via GitHub UI ou `gh`:

```bash
cd "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
gh repo create stout-wiki --private --source=. --remote=origin --push
```

Ou, se preferir nome diferente, ajustar.

Expected: o repo é criado e o primeiro commit é pushed.

- [ ] **Step 5: Validar que o remote está configurado**

```bash
cd "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
git remote -v
```

Expected: origin aparece apontando para github.com.

**⚠ Checkpoint humano:** verificar via GitHub UI que o repo existe, é privado, e recebeu o commit inicial.

---

## Task 3: Apontar wiki-compiler para produção

**Files:**
- Modify: `wiki-compiler/run_wiki_work.sh` (suportar flag `--production`)

- [ ] **Step 1: Adicionar suporte a modo produção**

Em `C:\Projetos\Stout\wiki-compiler\run_wiki_work.sh`, substituir a linha `VAULT="${VAULT:-$STOUT_ROOT/wiki-compiler/test-vault}"` por:

```bash
# Vault: --production usa vault real; senao usa test-vault
if [ "${1:-}" = "--production" ]; then
    VAULT="${VAULT_PRODUCTION:-/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki}"
    shift
else
    VAULT="${VAULT:-$STOUT_ROOT/wiki-compiler/test-vault}"
fi
echo "Usando vault: $VAULT"
```

Aplicar mesmo patch em `C:\Projetos\Stout\wiki-compiler\run_post_process.sh`.

- [ ] **Step 2: Smoke test no modo produção (sem esvaziar ainda!)**

```bash
# IMPORTANTE: esta etapa NAO esvazia, so valida que o script aponta corretamente
bash wiki-compiler/run_wiki_work.sh --production
```

Expected: mensagem `Usando vault: /c/Users/victor.bernardi/.../wiki`. Não deve haver erros. Arquivos em `memory/context-agent/sessions/` são copiados para `/c/Users/victor.bernardi/.../wiki/raw/_pending/` (se existir) ou falha pedindo o diretório — criar o `raw/_pending/` se faltar:

```bash
mkdir -p "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/raw/_pending"
mkdir -p "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/_raw"
```

Rodar novamente:
```bash
bash wiki-compiler/run_wiki_work.sh --production
```

Expected: pipeline de entrada roda. O `raw/_pending/` recebe as sessoes.

- [ ] **Step 3: Reverter teste (NAO commitar mudanças no vault ainda)**

```bash
# Remover arquivos do pending que acabou de ser injetado — eles vao entrar via reseed oficial depois
rm -rf "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/raw/_pending/"*.md
rm -rf "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/_raw/"*.md
```

- [ ] **Step 4: Commit mudança no script**

```bash
git -C "$STOUT_ROOT" add wiki-compiler/run_wiki_work.sh wiki-compiler/run_post_process.sh
git -C "$STOUT_ROOT" commit -m "feat: flag --production aponta wiki-compiler para vault real"
```

---

## Task 4: Esvaziar páginas do vault (preservando estrutura)

**Files:**
- Create: `scripts/reseed/empty_vault.sh`

- [ ] **Step 1: Escrever script de esvaziamento controlado**

Criar `C:\Projetos\Stout\scripts\reseed\empty_vault.sh`:

```bash
#!/bin/bash
# Esvazia paginas .md do vault, PRESERVANDO:
# - estrutura de pastas (raw/, _raw/)
# - arquivos de controle (suggestion_ignore.md, PENDENCIAS.md, AUDIT_REPORT.md, SUGESTOES-HOJE.md)
# - configuracao Obsidian (.obsidian/)
# - .git/

set -euo pipefail

VAULT="${1:-/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki}"

if [ ! -d "$VAULT" ]; then
    echo "ERRO: vault nao existe em $VAULT"
    exit 1
fi

# Safe-list de arquivos de controle na raiz
PRESERVE=(
    "suggestion_ignore.md"
    "PENDENCIAS.md"
    "AUDIT_REPORT.md"
    "SUGESTOES-HOJE.md"
    "README.md"
    ".gitignore"
)

echo "Esvaziando paginas em $VAULT ..."

# Remover .md da raiz (exceto preserve list)
for md in "$VAULT"/*.md; do
    [ -f "$md" ] || continue
    fname=$(basename "$md")
    preserve=false
    for p in "${PRESERVE[@]}"; do
        if [ "$fname" = "$p" ]; then
            preserve=true
            break
        fi
    done
    if [ "$preserve" = true ]; then
        echo "  Preservado: $fname"
    else
        rm "$md"
        echo "  Removido:  $fname"
    fi
done

# Remover pastas legadas (concepts/, entities/) se ainda existirem
for legacy in concepts entities; do
    if [ -d "$VAULT/$legacy" ]; then
        rm -rf "$VAULT/$legacy"
        echo "  Pasta legada removida: $legacy/"
    fi
done

echo ""
echo "Vault esvaziado. Preservados: estrutura raw/ e _raw/, arquivos de controle, .obsidian/, .git/"
```

- [ ] **Step 2: Executar esvaziamento (destrutivo!)**

```bash
bash scripts/reseed/empty_vault.sh
```

Expected: lista de arquivos removidos. Arquivos preservados (se existirem): suggestion_ignore.md etc.

- [ ] **Step 3: Commit do estado esvaziado no vault repo**

```bash
cd "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
git add -A
git commit -m "chore: vault esvaziado antes do reseed (Fase 4)"
```

- [ ] **Step 4: Commit do script no Stout**

```bash
git -C "$STOUT_ROOT" add scripts/reseed/empty_vault.sh
git -C "$STOUT_ROOT" commit -m "chore: script empty_vault preservando estrutura e controles"
```

**⚠ Checkpoint humano:** Abrir o vault esvaziado no Obsidian — confirma que a visualização abre sem erros (pode aparecer "vault vazio" e isso é ok). Se Obsidian crashar, investigar o `.obsidian/` corrompido antes de continuar.

---

## Task 5: Preparar conteúdo para re-seed híbrido

**Files:**
- Create: `scripts/reseed/reseed_from_backup.sh`

Estratégia de re-seed (do spec, A-iii):
1. Páginas do backup vão para `cleaned/` com prefixo `wiki-`
2. Sessões do storage unificado já estão em `sessions/`
3. Specs/plans limpos já estão em `cleaned/`
4. Pipeline de entrada normal coleta tudo e manda para `raw/_pending/`, depois `_raw/` do Ar9av

- [ ] **Step 1: Escrever script de preparação**

Criar `C:\Projetos\Stout\scripts\reseed\reseed_from_backup.sh`:

```bash
#!/bin/bash
# Preparacao do re-seed: copia paginas do backup para o storage de cleaned/
# com prefixo wiki- para entrarem no pipeline como entradas separadas.

set -euo pipefail

STOUT_ROOT="${STOUT_ROOT:-/c/Projetos/Stout}"
BACKUP_DIR="${BACKUP_DIR:?BACKUP_DIR precisa estar setado (export BACKUP_DIR=... do backup_vault.sh)}"
CLEANED_DIR="$STOUT_ROOT/memory/context-agent/cleaned"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "ERRO: BACKUP_DIR nao existe: $BACKUP_DIR"
    exit 1
fi

mkdir -p "$CLEANED_DIR"

count=0
# Copiar apenas .md da raiz do backup (ignorar _meta/, pastas internas etc.)
for md in "$BACKUP_DIR"/*.md; do
    [ -f "$md" ] || continue
    fname=$(basename "$md")
    # Pular arquivos de controle
    case "$fname" in
        suggestion_ignore.md|PENDENCIAS.md|AUDIT_REPORT.md|SUGESTOES-HOJE.md|README.md|BACKUP_MANIFEST.txt)
            continue
            ;;
    esac
    # Prefixo wiki- para rastreabilidade
    dst="$CLEANED_DIR/wiki-${fname%.md}.md"
    cp -p "$md" "$dst"
    count=$((count + 1))
done

echo "Copiados $count paginas do backup para $CLEANED_DIR (prefixo wiki-)"
```

- [ ] **Step 2: Executar preparação**

```bash
export BACKUP_DIR=/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/backup/wiki-pre-reforma-YYYY-MM-DD-HHMMSS  # ajustar data real
bash scripts/reseed/reseed_from_backup.sh
```

Expected: print "Copiados N paginas do backup para ..." com N > 0.

Validar manualmente:
```bash
ls "$STOUT_ROOT/memory/context-agent/cleaned/" | grep "^wiki-" | wc -l
```

Expected: valor deve corresponder ao N reportado.

- [ ] **Step 3: Commit script**

```bash
git -C "$STOUT_ROOT" add scripts/reseed/reseed_from_backup.sh
git -C "$STOUT_ROOT" commit -m "chore: script reseed_from_backup copia backup para cleaned/"
```

---

## Task 6: Rodar pipeline completo em produção

- [ ] **Step 1: Executar pipeline de entrada em modo produção**

```bash
bash wiki-compiler/run_wiki_work.sh --production
```

Expected:
- Input pipeline copia sessions + cleaned (incluindo os `wiki-*` do reseed) para pending
- Move de pending para `_raw/` do vault real
- Mensagem pedindo para rodar `/wiki-ingest` no Ar9av

- [ ] **Step 2: Invocar Ar9av `/wiki-ingest`**

Abrir Claude Code em contexto onde ele reconheça skills do Ar9av. Pedir:
> Rode `/wiki-ingest` no vault `/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki/`

Aguardar. Ar9av deve processar todo o `_raw/` e gerar páginas (com frontmatter, possivelmente Title Case).

- [ ] **Step 3: Invocar `/wiki-lint`**

> Rode `/wiki-lint` no mesmo vault.

Expected: relatório de links quebrados, órfãos, taxonomia.

- [ ] **Step 4: Invocar `/cross-linker`**

> Rode `/cross-linker` para descobrir wikilinks ausentes.

Expected: páginas recebem novos `[[wikilinks]]` onde aplicável.

- [ ] **Step 5: Rodar pipeline de saída (post-process)**

```bash
bash wiki-compiler/run_post_process.sh --production
```

Expected:
- Páginas pós-processadas em `$VAULT/_post_processed/`
- AUDIT_REPORT.md gerado na raiz do vault

---

## Task 7: Promover páginas pós-processadas para a raiz do vault

**Files:**
- Create: `scripts/reseed/promote_post_processed.sh`

- [ ] **Step 1: Escrever script de promoção**

Criar `C:\Projetos\Stout\scripts\reseed\promote_post_processed.sh`:

```bash
#!/bin/bash
# Move paginas pos-processadas (_post_processed/*.md) para a raiz do vault.
# Sobrescreve qualquer pagina existente com mesmo nome.

set -euo pipefail

VAULT="${VAULT:-/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki}"
SRC="$VAULT/_post_processed"

if [ ! -d "$SRC" ]; then
    echo "ERRO: $SRC nao existe. Rode run_post_process.sh --production antes."
    exit 1
fi

moved=0
for md in "$SRC"/*.md; do
    [ -f "$md" ] || continue
    fname=$(basename "$md")
    dst="$VAULT/$fname"
    mv "$md" "$dst"
    moved=$((moved + 1))
done

echo "Promovidas $moved paginas para $VAULT"
echo "Removendo _post_processed/ vazio..."
rmdir "$SRC" 2>/dev/null || true
```

- [ ] **Step 2: Executar promoção**

```bash
bash scripts/reseed/promote_post_processed.sh
```

Expected: N páginas movidas para raiz.

- [ ] **Step 3: Limpar pastas intermediárias Ar9av**

```bash
VAULT="/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
# _raw/ foi consumido pelo ingest
rm -rf "$VAULT/_raw/"*
# raw/_pending/ deve estar vazio (pipeline move)
# Deixar estrutura para proximos ciclos
```

- [ ] **Step 4: Commit script**

```bash
git -C "$STOUT_ROOT" add scripts/reseed/promote_post_processed.sh
git -C "$STOUT_ROOT" commit -m "chore: promote_post_processed move paginas para raiz"
```

---

## Task 8: Verificação automatizada do rebuild

**Files:**
- Create: `scripts/reseed/verify_rebuild.py`

- [ ] **Step 1: Escrever verificador**

Criar `C:\Projetos\Stout\scripts\reseed\verify_rebuild.py`:

```python
"""
Verifica saude do rebuild:
- Contagem de paginas >= 70% do backup
- Nenhum arquivo com YAML frontmatter residual
- Nenhum nome com espacos (so kebab-case)
- AUDIT_REPORT.md existe e nao reporta > 20% de orfaos
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def verify(vault: Path, backup: Path) -> tuple[bool, list[str]]:
    errs: list[str] = []

    # Count de paginas
    vault_pages = [
        p for p in vault.glob("*.md")
        if p.name not in {
            "suggestion_ignore.md", "PENDENCIAS.md",
            "AUDIT_REPORT.md", "SUGESTOES-HOJE.md", "README.md",
        }
    ]
    backup_pages = [
        p for p in backup.glob("*.md")
        if p.name not in {
            "suggestion_ignore.md", "PENDENCIAS.md",
            "AUDIT_REPORT.md", "SUGESTOES-HOJE.md", "README.md",
            "BACKUP_MANIFEST.txt",
        }
    ]
    ratio = len(vault_pages) / max(len(backup_pages), 1)
    if ratio < 0.7:
        errs.append(
            f"Contagem baixa: vault tem {len(vault_pages)} paginas vs backup {len(backup_pages)} ({ratio:.0%})"
        )

    # Frontmatter residual
    fm_re = re.compile(r"^---\r?\n", re.MULTILINE)
    for p in vault_pages:
        if fm_re.match(p.read_text(encoding="utf-8")):
            errs.append(f"Frontmatter residual em {p.name}")

    # Kebab-case nos nomes
    name_re = re.compile(r"^[a-z0-9-]+\.md$")
    for p in vault_pages:
        if not name_re.match(p.name):
            errs.append(f"Nome fora do kebab-case: {p.name}")

    # AUDIT_REPORT
    audit = vault / "AUDIT_REPORT.md"
    if not audit.exists():
        errs.append("AUDIT_REPORT.md ausente")
    else:
        content = audit.read_text(encoding="utf-8")
        orphan_match = re.search(r"Links Órfãos \((\d+)\)", content)
        if orphan_match:
            orphans = int(orphan_match.group(1))
            orphan_ratio = orphans / max(len(vault_pages), 1)
            if orphan_ratio > 0.2:
                errs.append(
                    f"Muitos orfaos: {orphans} ({orphan_ratio:.0%} do vault)"
                )

    return len(errs) == 0, errs


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: verify_rebuild.py <vault> <backup>")
        sys.exit(2)
    ok, errs = verify(Path(sys.argv[1]), Path(sys.argv[2]))
    if ok:
        print("REBUILD VALIDO")
        sys.exit(0)
    print("REBUILD INVALIDO:")
    for e in errs:
        print(f"  - {e}")
    sys.exit(1)
```

- [ ] **Step 2: Executar**

```bash
python scripts/reseed/verify_rebuild.py \
    "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki" \
    "$BACKUP_DIR"
```

Expected: `REBUILD VALIDO`.

Se `INVALIDO`:
- Analisar cada erro reportado
- Corrigir manualmente ou rodar de novo com ajustes no pipeline
- **Não fazer commit final enquanto INVALIDO**

- [ ] **Step 3: Commit verificador**

```bash
git -C "$STOUT_ROOT" add scripts/reseed/verify_rebuild.py
git -C "$STOUT_ROOT" commit -m "chore: verify_rebuild valida qualidade do reseed"
```

---

## Task 9: Revisão manual de amostra

**Files:** nenhum (revisão humana)

- [ ] **Step 1: Selecionar amostra de 10 páginas aleatórias**

```bash
VAULT="/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
ls "$VAULT"/*.md | grep -v "^suggestion_ignore\|^PENDENCIAS\|^AUDIT\|^SUGESTOES\|^README" | shuf -n 10
```

- [ ] **Step 2: Revisar cada página**

Abrir cada uma no Obsidian. Para cada:
- [ ] Legível?
- [ ] Preserva decisões / arquitetura da versão original?
- [ ] Wikilinks funcionam (não vermelhos/órfãos)?
- [ ] Sem ruído residual (paths, comandos, fragmentos de terminal)?

- [ ] **Step 3: Revisar 100% das páginas técnicas críticas**

Lista de páginas consideradas críticas (ajustar conforme seu contexto):
- `fabric-*` (Fabric connector)
- `context-agent*` (tudo do context-agent)
- `ar9av*` (tudo do novo motor)
- `llm-wiki*` (próprio tema da reforma)

Para cada uma, aplicar o checklist do Step 2.

- [ ] **Step 4: Corrigir manualmente o que não passar**

Editar diretamente no Obsidian as páginas com problemas. Commit parcial possível:

```bash
cd "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
git add .
git commit -m "fix: corrige paginas X, Y, Z apos reseed"
```

**⚠ Checkpoint humano obrigatório:** só avançar para Task 10 quando você concordar que a qualidade está aceitável.

---

## Task 10: Commit atômico final no repo do vault

- [ ] **Step 1: Verificar estado limpo**

```bash
cd "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
git status
```

Expected: algumas páginas modificadas/novas (do rebuild).

- [ ] **Step 2: Commit**

```bash
cd "/c/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki"
git add .
git commit -m "refactor: rebuild completo via pipeline Ar9av (Fase 4 da reforma)"
```

- [ ] **Step 3: Push para remoto**

```bash
git push origin main
```

- [ ] **Step 4: Criar tag para o marco**

```bash
git tag -a v1.0-rebuild -m "Primeiro rebuild completo apos reforma Ar9av"
git push origin v1.0-rebuild
```

---

## Task 11: Deprecar componentes antigos

**Files:**
- Delete (ou rename para .deprecated): `wiki-compiler/harvest_brain.sh`
- Modify: `librarian_policy.md` (Antigravity)

- [ ] **Step 1: Marcar `harvest_brain.sh` como deprecado**

```bash
mv wiki-compiler/harvest_brain.sh wiki-compiler/harvest_brain.sh.deprecated
```

Adicionar cabeçalho no arquivo renomeado:

Edit `C:\Projetos\Stout\wiki-compiler\harvest_brain.sh.deprecated` — adicionar no topo:

```bash
#!/bin/bash
# DEPRECATED 2026-04-23 pela Fase 4 da reforma do LLM Wiki.
# Antigravity agora usa context-agent para alimentar pending via storage unificado.
# Remover este arquivo apos 2 semanas (2026-05-07) se nada tiver quebrado.
exit 1
```

- [ ] **Step 2: Atualizar `librarian_policy.md` do Antigravity**

Localizar `librarian_policy.md` (provavelmente em `~/.gemini/antigravity/knowledge/knowledge_librarian_policy/artifacts/librarian_policy.md` ou equivalente):

```bash
find /c/Users/victor.bernardi -name "librarian_policy.md" 2>/dev/null
```

Editar o arquivo encontrado — **remover** qualquer seção que instrua a escrever em `raw/_pending/` diretamente via Trigger Gamma. **Manter** seções que:
- Leem SUGESTOES-HOJE.md
- Atualizam suggestion_ignore.md
- Atualizam PENDENCIAS.md

Adicionar nota no topo do arquivo:

```markdown
> **Atualizado 2026-04-23:** o Bibliotecário não escreve mais em `raw/_pending/`.
> Conteúdo do Antigravity entra no wiki via context-agent (skill `context-agent-bridge`).
> Mantém apenas os papéis de leitura/feedback sobre SUGESTOES-HOJE.md.
```

- [ ] **Step 3: Commit no Stout**

```bash
git -C "$STOUT_ROOT" add wiki-compiler/harvest_brain.sh.deprecated
git -C "$STOUT_ROOT" rm wiki-compiler/harvest_brain.sh 2>/dev/null || true
git -C "$STOUT_ROOT" commit -m "chore: deprecia harvest_brain e remove write-role do Bibliotecario"
```

---

## Self-Review

**1. Spec coverage:**
- ✅ Backup completo antes de qualquer coisa → Task 1
- ✅ Git init no vault + remote privado → Task 2
- ✅ Esvaziar vault preservando estrutura → Task 4
- ✅ Re-seed híbrido (backup + sessions + cleaned) → Tasks 5-6
- ✅ Rodar pipeline novo → Task 6
- ✅ Audit engine valida → Task 8 (via verify_rebuild) + AUDIT_REPORT real
- ✅ Revisão manual de amostra → Task 9
- ✅ Commit atômico → Task 10
- ✅ Deprecações (`harvest_brain.sh`, Bibliotecário write) → Task 11

**2. Placeholder scan:** nenhum TBD/TODO. Placeholders de data (`YYYY-MM-DD`) são expectados como tokens a substituir em runtime.

**3. Type consistency:** paths absolutos ou explícitos com env vars em toda linha bash; Python scripts usam `Path` uniformemente.

**4. Reversibilidade em cada etapa:**
- Task 1 → backup existente; rollback = restore do backup
- Task 2 → `git init` é reversível (`rm -rf .git`)
- Task 4 → backup permite restore total
- Task 7 → `_post_processed` é staging; erro antes de promote = rollback trivial

---

## Dependencies

- **Bloqueado por:** Fases 1, 2, 3 completas e validadas
- **Bloqueia:** Fase 5 (INDEX + NLM sync + feedback) — depende de vault estável

---

## Execution Notes

- Reservar pelo menos 2 horas sem interrupções. Fase 4 tem muitos pontos de no-go.
- Testar em horário fora do trabalho crítico — qualquer erro pode levar 30-60min para reverter.
- Se o Obsidian abrir o vault durante o pipeline, fechar antes de rodar — ele pode bloquear arquivos em edição.
- Se `/wiki-ingest` do Ar9av demorar >10min, verificar se a fila de `_raw/` não está absurdamente grande (se sim, processar em batches).
