# Aprendizados, Erros e Melhorias — Sessão 151 (2026-05-21)

> **Contexto:** Integração de governança de recência no Motor CEVAP + cópia OneDrive com preservação de controle comercial
> **Referência:** Walkthrough da sessão em `docs/walkthrough_2026-05-21.md`

---

## 🛑 1. Onde Errei & Como Melhorar

### A. Cópia OneDrive sem preservação de controle (primeira tentativa)
* **O erro:** Implementei `shutil.copy2` simples, que sobrescrevia o arquivo do OneDrive destruindo as colunas preenchidas pelo Filipe.
* **A correção:** Refatorei para merge por `CNPJ_Cliente` preservando as 5 colunas de controle. Adicionei normalização de tipos (`object` vs `int64`) e auditoria de preservação (contagem antes/depois + identificação de CNPJs órfãos).

### B. Mock de `pathlib.Path.exists` muito agressivo
* **O erro:** Mockar `pathlib.Path.exists` globalmente quebrou o carregamento de dados (M5 não era encontrado).
* **A correção:** Usar side_effect que intercepta apenas caminhos OneDrive e delega o resto para o `Path.exists` real.

### C. `edit_file` com falhas intermitentes
* **O erro:** A ferramenta `edit_file` falhou repetidamente em encontrar strings que existiam no arquivo.
* **A correção:** Usei scripts Python temporários como alternativa, executados via shell.

---

## 🐛 2. Bugs Identificados & Corrigidos

### A. Path do cadastro SA1010 errado
* **O bug:** `PATH_CADASTRO` apontava para `m0_cache_sa1010_983280b9.parquet` (inexistente). Arquivo real é `m0_cache_sa1010.parquet`.
* **A correção:** Corrigido no `consolidate_cevap.py` e no AGENTS.md.

### B. Erro de tipo no merge OneDrive
* **O bug:** `CNPJ_Cliente` era `object` no output e `int64` no OneDrive, causando `KeyError` no merge.
* **A correção:** Normalização com `.astype(str).str.strip().str.zfill(14)` em ambos DataFrames antes do merge.

---

## 🚀 3. O que Funcionou Bem

1. **Padronização de governança:** Pre-flight + Post-flight seguindo exatamente o padrão 03_Potencial/05_Segmentacao
2. **Tabela de recência global:** CEVAP cadastrado como fonte monitorada com suporte a glob
3. **Testes de OneDrive:** 4 cenários cobrindo primeira exportação, merge, defaults e solda
4. **Execução real validada:** Motor rodou completo — 955 clientes, OneDrive atualizado, 2.910/32.759 preenchimentos preservados
