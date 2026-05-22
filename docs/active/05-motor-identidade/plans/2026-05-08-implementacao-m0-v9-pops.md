# Implementation Plan: M0-v9 Soberania POPS (Refined)

> **For Gemini CLI:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reativar a Camada C2 de unificação no Motor de Identidade usando soberania de posse do POPS (Excel Local), com travas rígidas contra Dealer (Inova) e Locadoras.

**Architecture:** Criação do script v9 isolado via CÓPIA e modificação cirúrgica via REPLACE. 
**Fluxo:** Ingestão Protheus + Ingestão POPS (Excel) -> Filtro de Neutralidade Inova -> Filtro Volumétrico de Chassis (Anti-Locadora) -> Grafo de Unificação (C1 + C2 Soberana) -> Auditoria v9.

**Tech Stack:** Python, Pandas, NetworkX, Openpyxl.

---

### Task 1: Setup do Script v9 (Modo Clone)

**Files:**
- Create: `02_Scripts/motor_identidade_m0_v9_pops.py` (via shell copy)
- Reference: `02_Scripts/motor_identidade_m0.py`

**Step 1: Copiar o arquivo original para o novo nome via comando de sistema.**
**Step 2: Ajustar via REPLACE as variáveis de diretório e nome de saída para evitar conflitos.**

### Task 2: Ingestão do POPS (Excel Local)

**Files:**
- Modify: `02_Scripts/motor_identidade_m0_v9_pops.py`
- Source: `C:\Projetos\Inova\Potencial Clientes\cache\Product_details_full.xlsx`

**Step 1: Inserir via REPLACE a função `ingest_pops()` e a constante `PATH_POPS`.**
**Step 2: Adicionar a chamada da ingestão no fluxo principal.**

### Task 3: Trava de Neutralidade Dealer (Inova)

**Files:**
- Modify: `02_Scripts/motor_identidade_m0_v9_pops.py`

**Step 1: Inserir via REPLACE a constante `BLACKLIST_INOVA_RAIZ`.**
**Step 2: Implementar via REPLACE o filtro no POPS para garantir Soberania Zero da Inova.**

### Task 4: Filtro Volumétrico de Chassis (Anti-Bridge)

**Files:**
- Modify: `02_Scripts/motor_identidade_m0_v9_pops.py`

**Logic:** O filtro não olha quantidade de máquinas por cliente, mas sim **quantidade de raízes de CNPJ por chassi**. Se 1 chassi único passou por > 2 raízes distintas na oficina, ele é neutralizado (Chassi Bridge).
**Step 1: Implementar via REPLACE o cálculo de cardinalidade de raízes por chassi.**
**Step 2: Filtrar o grafo de unificação para excluir esses chassis pontes.**

### Task 5: Implementação da Unificação C2 Soberana

**Files:**
- Modify: `02_Scripts/motor_identidade_m0_v9_pops.py`

**Step 1: Substituir via REPLACE a lógica desativada da C2 pela nova lógica baseada no POPS.**
**Step 2: Garantir que a C2 tenha precedência no dicionário de unificação.**

### Task 6: Auditoria e Validação

**Files:**
- Create: `tests/test_unificacao_v9.py`
- Modify: `02_Scripts/motor_identidade_m0_v9_pops.py`

**Step 1: Ajustar via REPLACE os nomes dos arquivos de saída do Audit.**
**Step 2: Validar integridade dos grupos via teste unitário.**

---
*Assinado: Antigravity (Phase: Strategy)*
