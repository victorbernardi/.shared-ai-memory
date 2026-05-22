# Walkthrough Técnico - Sistema de Governança de Recência Unificado (M3 & M2)

Este documento documenta os testes de homologação, modificações físicas e resultados obtidos na integração da governança de dados e controle de recência analítica para o motor **M3 (Potencial Clientes)** e consolidação retrocompatível do motor **M2 (Faturamento)**.

---

## 🛠️ Mudanças Físicas Implementadas

### 1. Infraestrutura Compartilhada (`/shared`)
*   **Sensor Global:** O utilitário central `governance_sensor.py` foi unificado em [governance_sensor.py](file:///C:/Projetos/Inova/shared/governance_sensor.py), garantindo higiene de encoding (UTF-8), pre-flight checks de ambiente locais e parse do status de recência corporativo.
*   **Ajuste do Relatório Global:** Modificação de [generate_recency_report.py](file:///C:/Projetos/Inova/shared/generate_recency_report.py) para remover a antiga fonte RFM descontinuada e incluir, de forma atômica e resiliente, as duas novas visões de ouro geradas por M3:
    *   **M3 (Potencial Clientes)**
    *   **M3 (Potencial por Chassi)**
    *   Ambos os caminhos foram mapeados diretamente para a pasta `/shared/data/` compartilhada de produção onde o save grava os Parquets.

### 2. Retrocompatibilidade do Motor M2 (`02_Faturamento`)
*   **Higiene Física:** Remoção física do sensor local duplicado `02_Faturamento/src/tools/governance_sensor.py`.
*   **Importação Dinâmica:** Refatoração de [run.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/run.py) no motor M2 para importar o `run_preflight` da biblioteca compartilhada global.

### 3. Integração do Motor M3 (`03_Potencial`)
*   **Pre-flight Check (Decolagem):** Refatoração de [run.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/03_Potencial/run.py) para importar o sensor global e executar a verificação de saúde com tolerância a falhas locais (`fail_fast=False`).
*   **Post-flight Check (Pousagem):** Adição de subprocesso dinâmico no final de `main()` (após o salvamento bem-sucedido dos dados em Excel e Parquet) para re-gerar o relatório de recência corporativo atualizado automaticamente.

---

## 🧪 Resultados de Homologação e Validação

### 📋 Estado Final do Relatório de Recência Global
Após o término das execuções de teste dos motores, o arquivo de governança [recency_status.md](file:///C:/Projetos/Inova/shared/recency_status.md) foi re-gerado contendo as novas linhas do M3 atualizadas com sucesso:

| Fonte de Dados | Arquivo Físico | Status de Recência | Última Modificação |
| :--- | :--- | :--- | :--- |
| **M2 (Faturamento)** | `dataset_ouro_faturamento_v1.parquet` | 🟢 Atualizado Ontem | 2026-05-19 18:50 |
| **M0 (Identidade)** | `dataset_ouro_identidade.parquet` | 🟢 Atualizado Ontem | 2026-05-19 10:47 |
| **M3 (Potencial Clientes)** | `dataset_ouro_potencial_v1.parquet` | **🟢 Atualizado Hoje** | **2026-05-20 11:45** |
| **M3 (Potencial por Chassi)** | `dataset_ouro_potencial_chassi_v1.parquet` | **🟢 Atualizado Hoje** | **2026-05-20 11:45** |

### 🚀 Logs de Execução de Decolagem do Motor M3
O Pre-flight rodou na decolagem do motor de Potencial M3 emitindo com sucesso a governança inteligente:
```text
2026-05-20 11:44:51 [INFO] 03_Potencial — === Motor de Potencial V1 — início ===
2026-05-20 11:44:51 [INFO] GovernanceEngine — === Iniciando Pre-flight Check (Stout Governance) ===
2026-05-20 11:44:51 [INFO] GovernanceEngine — 🟢 Higiene de Encoding: UTF-8 configurado.
2026-05-20 11:44:51 [INFO] GovernanceEngine — 🟢 Ambiente: Conectores e configurações de infraestrutura localizados.
2026-05-20 11:44:51 [WARNING] GovernanceEngine — ⚠️  ALERTA DE RECÊNCIA: Fontes desatualizadas detectadas!
2026-05-20 11:44:51 [WARNING] GovernanceEngine —    - M5 (Estratégico) (🟡 Desatualizado)
2026-05-20 11:44:51 [WARNING] GovernanceEngine —    - M3 (Potencial Clientes) (🔴 Ausente)
2026-05-20 11:44:51 [WARNING] GovernanceEngine —    - M3 (Potencial por Chassi) (🔴 Ausente)
2026-05-20 11:44:51 [WARNING] GovernanceEngine —    - Frota Máquinas (🟡 Desatualizado)
2026-05-20 11:44:51 [WARNING] GovernanceEngine —    - Pontuação Seedz (🟡 Desatualizado)
2026-05-20 11:44:51 [WARNING] GovernanceEngine —    - InovaPay Limites (🟡 Desatualizado)
2026-05-20 11:44:51 [WARNING] GovernanceEngine —    - Feedbacks BUP (🟡 Desatualizado)
2026-05-20 11:44:51 [INFO] GovernanceEngine — ✅ Pre-flight concluído: Motor pronto para processamento.
```

E no encerramento (Pouso), o Post-flight concluiu:
```text
2026-05-20 11:45:04 [INFO] load — Excel salvo: dataset_ouro_potencial_chassi_v1.xlsx (2740 linhas)
2026-05-20 11:45:04 [INFO] load — Excel salvo: dataset_ouro_potencial_v1.xlsx (1180 linhas)
2026-05-20 11:45:04 [INFO] 03_Potencial — [INICIO] Post-flight: Atualizando Relatório de Recência
Relatório Markdown de recência salvo em C:\Projetos\Inova\shared\recency_status.md
2026-05-20 11:45:05 [INFO] 03_Potencial — [OK]    Post-flight: Relatório de Recência
2026-05-20 11:45:05 [INFO] 03_Potencial — === Motor de Potencial V1 — concluído com sucesso ===
```

### 🔁 Logs de Retrocompatibilidade e Execução do Motor M2
O motor de Faturamento M2 foi executado localmente e provou 100% de estabilidade retrocompatível:
```text
2026-05-20 11:47:13,854 INFO [INICIO] Pre-flight Governance Check
2026-05-20 11:47:13,856 [GOVERNANCE] === Iniciando Pre-flight Check (Stout Governance) ===
2026-05-20 11:47:13,856 [GOVERNANCE] 🟢 Higiene de Encoding: UTF-8 configurado.
2026-05-20 11:47:13,856 [GOVERNANCE] 🟢 Ambiente: Conectores e configurações de infraestrutura localizados.
2026-05-20 11:47:13,856 [GOVERNANCE] ⚠️  ALERTA DE RECÊNCIA: Fontes desatualizadas detectadas!
2026-05-20 11:47:13,856 [GOVERNANCE] 🟢 Pre-flight concluído: Motor pronto para processamento.
2026-05-20 11:47:13,856 INFO [OK]    Pre-flight Governance Check — 0.0s
...
2026-05-20 11:47:14,939 INFO [INICIO] Post-flight: Atualizando Relatorio de Recencia
Relatório Markdown de recência salvo em C:\Projetos\Inova\shared\recency_status.md
2026-05-20 11:47:15,040 INFO [OK]    Post-flight: Atualizando Relatorio de Recencia — 0.1s
2026-05-20 11:47:15,040 INFO Motor Faturamento concluido em 1.2s | Grupos: 984 | CAL2025: R$ 186394933.67
```

---

## 📈 Conclusão
A esteira do pipeline `potencial-clientes` foi validada com sucesso. Os motores M2 e M3 estão agora totalmente integrados ao ecossistema global de governança Stout, eliminando o código legado duplicado e garantindo a resiliência operacional da governança de dados.
