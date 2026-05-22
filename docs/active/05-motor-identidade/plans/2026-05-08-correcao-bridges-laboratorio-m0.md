# Implementation Plan: M0-v9.2 Correção de Bridges e Script Lab Explorer

> **For Gemini CLI:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Corrigir os mega-bridges no Motor M0 e criar uma ferramenta de auditoria interativa (Lab Explorer) para validar grupos com > 5 integrantes.

**Architecture:** 
1.  **Refino de Unificação:** Bloqueio de raízes inválidas e Dealers.
2.  **Lab Engine:** O Motor M0-v9.2 exportará um "Snapshot de Estudo" (Parquet).
3.  **Lab Explorer:** Novo script Python para consulta rápida via terminal.

---

### Task 1: Correção de Âncoras e Segurança M0

**Files:**
- Modify: `02_Scripts/motor_identidade_m0_v9_pops.py`

**Step 1: Impedir unificação via C2 se `CNPJ_RAIZ` for "0", vazio ou pertencer à `BLACKLIST_INOVA_RAIZ`.**
**Step 2: Adicionar validação na C8 para descartar elos em raízes triviais.**

### Task 2: Geração do Snapshot do Laboratório

**Files:**
- Modify: `02_Scripts/motor_identidade_m0_v9_pops.py`

**Step 1: Implementar lógica que identifica grupos com cardinalidade > 5.**
**Step 2: Salvar `03_Resultados_v9_POPS/m0_lab_snapshot.parquet` com o detalhamento desses grupos.**

### Task 3: Criação do Script `maestro_lab_explorer.py`

**Files:**
- Create: `02_Scripts/maestro_lab_explorer.py`

**Step 1: Desenvolver script que lê o `m0_lab_snapshot.parquet`.**
**Step 2: Criar interface CLI simples: o usuário digita parte do nome (ex: "CAMAJO") e o script lista todos os vizinhos do grupo, CNPJs e como foram soldados.**

---
*Assinado: Antigravity (Phase: Strategy)*
