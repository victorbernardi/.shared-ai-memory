# Walkthrough - Implementação de Validação de Recência no Motor CEVAP

Implementamos a validação de recência temporal do ecossistema de motores analíticos no Motor CEVAP, baseando-se no calendário comercial e em total conformidade com o manifesto de CDD e TDD.

---

## 🛠️ O que foi feito

### 1. Injeção da Validação Centralizada

* **Arquivo:** `projects/motor-cevap/Motor CEVAP/scripts/consolidate_cevap.py` [MODIFY]
  * Injetamos a função `check_recency_report()` para fazer o parse inteligente do arquivo de governança centralizado [recency_status.md](file:///c:/Projetos/Inova/shared/recency_status.md).
  * Se houver fontes classificadas como `🟡 Desatualizado` ou `🔴 Ausente`, o console exibirá um aviso destacado e imprimirá a tabela de recência correspondente para conhecimento operacional.

### 2. Integração no Fluxo de Execução

* **Arquivo:** `projects/motor-cevap/Motor CEVAP/scripts/consolidate_cevap.py` [MODIFY]
  * Adicionamos a chamada da validação de recência logo no início da função `run_consolidation()`, antes de qualquer carga física de arquivos e tabelas auxiliares.

### 3. Cobertura Completa de Testes (TDD)

* **Arquivo:** `projects/motor-cevap/Motor CEVAP/tests/test_cevap_recency_alert.py` [NEW]
  * Escrevemos 4 novos cenários de testes unitários e de integração baseados em mocks, cobrindo:
    * Execução quando o arquivo de recência não existe (tolerância robusta).
    * Execução quando todas as fontes estão atualizadas (nenhum alerta).
    * Execução quando existem fontes obsoletas ou ausentes (captura de alertas).
    * Chamada integrada à inicialização da consolidação (`run_consolidation`).

### 4. Correção e Resiliência da Suite de Testes

* **Arquivo:** `projects/motor-cevap/Motor CEVAP/tests/test_columns.py` [MODIFY]
  * Atualizamos o testador de colunas para usar caminhos de arquivos dinâmicos e relativos à raiz do projeto.
  * Ajustamos a lista `expected_cols` para refletir o schema atualizado e alinhado com o BUP CRM (`CNPJ_Cliente`, `Nome_Cliente`, `Dias_Inativo`, etc.), eliminando falhas de regressão locais.

---

## 🧪 Resultados dos Testes

Executamos a suíte inteira de testes para garantir a regressão limpa:

```bash
python -m pytest "Motor CEVAP/tests"
```text

```text
============================= test session starts =============================
platform win32 -- Python 3.13.9, pytest-8.0.0, pluggy-1.5.0
rootdir: C:\Projetos\Inova\projects\motor-cevap
plugins: anyio-4.10.0, cov-7.1.0, typeguard-4.5.1
collected 5 items

Motor CEVAP\tests\test_cevap_recency_alert.py ....                       [ 80%]
Motor CEVAP\tests\test_columns.py .                                      [100%]

============================== 5 passed in 1.25s ==============================
```text

---

## 💾 Versionamento e Commit

As alterações foram salvas utilizando a convenção do projeto:

* **Commit:** `feat(cevap): add recency validation at startup` (Staged files: `consolidate_cevap.py`, `test_cevap_recency_alert.py` e `test_columns.py`).
