# 📂 PLANO DE ESTRATÉGIA (V4 REVISADO) — VALIDAÇÃO TEMPORAL DESACOPLADA

> **Herança:** GEMINI.md Global & Local (BUP)
> **Versão:** 4.1 (Decoupled Markdown Approach)
> **Criado em:** 2026-05-19
> **Status:** STANDBY MODE — Apoiando Revisão Humana

---

## 🎯 Objetivo
Implementar a validação temporal de recência de fontes de forma totalmente desacoplada, utilizando um script de auditoria centralizado em `shared` que escreve um relatório Markdown, o qual é então interpretado pelo motor BUP para exibição de alertas de recência antes de seguir com a consolidação.

---

## 🏗️ 1. Arquitetura do Fluxo

```
+------------------------------------------+
|  shared/generate_recency_report.py       |  <--- Executa a auditoria das fontes
+------------------------------------------+
                     |
                     v (Escreve)
+------------------------------------------+
|  shared/recency_status.md                |  <--- Relatório tabular em Markdown
+------------------------------------------+
                     |
                     v (Lê & Interpreta)
+------------------------------------------+
|  BUP/scripts/consolidate_bup.py          |  <--- Exibe alertas e executa consolidação
+------------------------------------------+
```

---

## 📅 2. Lógica Comercial de Recência (Calendário Comercial)

A recência esperada (`Target Date`) de cada fonte de dados respeita as regras de calendário comercial do dia atual (`today`):
- **Hoje é Segunda-feira:** Target = **Sexta-feira anterior** (Hoje - 3 dias).
- **Hoje é Terça a Sexta-feira:** Target = **Ontem** (Hoje - 1 dia).
- **Hoje é Sábado ou Domingo:** Target = **Sexta-feira anterior** (Hoje - 1 ou 2 dias).

O script `generate_recency_report.py` mapeará os seguintes 10 arquivos críticos:
1.  `dataset_ouro_identidade.parquet` (M0 - Identidade)
2.  `dataset_final_estrategico_v1.parquet` (M5 - Estratégico)
3.  `cache_vendas_rfm.parquet` (M3 - Vendas)
4.  `dataset_ouro_maquinas_v1.parquet` (Frota Máquinas)
5.  `m0_cache_sa1010_983280b9.parquet` (Cadastro Clientes)
6.  `dados Seedz*.xlsx` (Seedz)
7.  `Relatorio de Clientes INOVA*.xlsx` (InovaPay)
8.  `tabela_orçamentos_abertos.xlsx` (Orçamentos Abertos)
9.  `tabela_orçamentos_cancelados.xlsx` (Orçamentos Cancelados)
10. `BUP_POS_VENDA.xlsx` (Histórico de Feedbacks)

---

## 🛠️ 3. Alterações Físicas Propostas

### A. Novo Script de Auditoria
*   **Arquivo:** `c:\Projetos\Inova\shared\generate_recency_report.py` [NEW]
    *   Faz a leitura física de data de modificação (`os.path.getmtime`), calcula o `Target Date` comercial, determina o status (`🟢 Atualizado Hoje`, `🟢 Atualizado Ontem`, `🟢 Atualizado Sexta`, `🟡 Desatualizado` ou `🔴 Ausente`) e salva a tabela Markdown em `recency_status.md`.

### B. Novo Relatório Markdown
*   **Arquivo:** `c:\Projetos\Inova\shared\recency_status.md` [NEW]
    *   Contém a tabela estruturada com os campos: `Fonte de Dados`, `Arquivo Físico`, `Status de Recência`, `Última Modificação`.

### C. Ajuste no Motor BUP
*   **Arquivo:** `c:\Projetos\Inova\projects\BUP-base-unica-pós-venda\scripts\consolidate_bup.py` [MODIFY]
    *   Importará/lerá `recency_status.md` no início da execução.
    *   Fará um parse de strings buscando linhas com `🟡 Desatualizado` ou `🔴 Ausente`.
    *   Se encontrar algum item fora da recência:
        *   Imprime alerta colorido detalhando os itens desatualizados.
        *   Imprime a tabela Markdown completa para visibilidade do operador.
    *   Segue com a consolidação da BUP normalmente.

---

## 🧪 4. Plano de Verificação

1.  **Geração do Markdown:** Executar `generate_recency_report.py` e verificar se a tabela e o arquivo são criados corretamente em `shared`.
2.  **QA de Leitura do BUP:** Executar `consolidate_bup.py` com bases desatualizadas simuladas para conferir se o alerta é disparado na tela e o processo prossegue com sucesso.

---
> **STANDBY MODE ACTIVATED**
> O Plano v4.1 foi persistido em `docs/plans/plan_v4_validacao_datas_motores.md`.
> Nenhuma linha de código fonte de projeto foi alterada. Aguardando autorização humana para iniciar a execução (/build).
