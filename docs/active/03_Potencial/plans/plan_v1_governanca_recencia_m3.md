# Plano de Estratégia: Alinhamento de Governança de Recência (M3 & M2 Centralizado)

> **Versão:** v1.1 (Auditada e Sincronizada)  
> **Data:** 2026-05-20  
> **Status:** STANDBY (Aguardando Aprovação Humana)  
> **Autor:** Stout Architect Engine

---

## 🎯 1. Escopo e Objetivos

Este plano detalha as atividades para a centralização física do sensor de governança na pasta `/shared` e a implementação das travas de decolagem (**Pre-flight**) e pouso (**Post-flight**) no motor **M3 (Potencial Clientes)**, além do refactoring e homologação do motor **M2 (Faturamento)**.

Este planejamento está 100% integrado à especificação técnica `spec_v1_governanca_recencia_m3.md` através de sua Matriz de Rastreabilidade.

---

## ⚙️ 2. Decisões de Design Consolidadas (Grilling Session)

1. **Centralização do Sensor:** O script `governance_sensor.py` será migrado do M2 para `/shared/governance_sensor.py`, tornando-se um utilitário global consumível por todos os motores. *(AC-1)*
2. **Fail-Fast Tolerante (M3):** A verificação de recência na inicialização do M3 (`Pre-flight`) emitirá alertas robustos no console em caso de obsolescência, mas não interromperá a execução local (`fail_fast=False`). *(AC-4)*
3. **Monitoramento Atômico (M3):** Ambos os arquivos de ouro de saída do M3 (`dataset_ouro_potencial_v1.parquet` e `dataset_ouro_potencial_chassi_v1.parquet`) serão adicionados individualmente à esteira de governança no `/shared/generate_recency_report.py`. *(AC-2)*
4. **Post-flight Resiliente (M3):** O disparo do atualizador do relatório no final da pipeline do M3 tolerará falhas externas de I/O do Windows rodando com `check=False` envelopado em bloco `try/except`. *(AC-5)*

---

## 🛠️ 3. Arquitetura Física de Modificações

### 📁 Componente: Central (Infraestrutura /shared)

#### [NEW] [governance_sensor.py](file:///C:/Projetos/Inova/shared/governance_sensor.py)
*   Mover a lógica de validação de ambiente, encoding e parsing de recência do M2 para esta localização global. *(FR-001, NFR-001)*

#### [MODIFY] [generate_recency_report.py](file:///C:/Projetos/Inova/shared/generate_recency_report.py)
*   Remover a fonte morta `"Vendas M3 RFM"`.
*   Inserir as fontes críticas reais do M3:
    *   `"M3 (Potencial Clientes)"` ➔ `dataset_ouro_potencial_v1.parquet`
    *   `"M3 (Potencial por Chassi)"` ➔ `dataset_ouro_potencial_chassi_v1.parquet` *(FR-002)*

---

### 📁 Componente: Motor M2 (Faturamento)

#### [DELETE] [governance_sensor.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/src/tools/governance_sensor.py)
*   Remoção do arquivo local redundante para evitar duplicação e desvios de versão. *(AC-1)*

#### [MODIFY] [run.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/run.py)
*   Atualizar a importação do sensor:
    ```python
    # De:
    from src.tools.governance_sensor import run_preflight
    # Para:
    from governance_sensor import run_preflight
    ```
    *(FR-003)*

---

### 📁 Componente: Motor M3 (Potencial)

#### [MODIFY] [run.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/03_Potencial/run.py)
*   Inserir chamada ao `run_preflight(str(_shared_dir), fail_fast=False)` no início do bloco `main()`. *(FR-004)*
*   Inserir execução de subprocesso para `/shared/generate_recency_report.py` com `check=False` e tratamento explícito de exceção ao final da gravação com sucesso dos dados. *(FR-005, NFR-002)*

---

## 🚦 4. Plano de Verificação Analítica

### Testes de Integração Manual
1.  **T-001 (Sintaxe e Compilação):** Executar `python -m py_compile` em todos os arquivos modificados e criados.
2.  **T-002 (Geração do Relatório):** Confirmar a gravação correta de `C:\Projetos\Inova\shared\recency_status.md` contendo as saídas M3 marcadas com o ícone temporal apropriado baseado na data do arquivo Parquet.
3.  **T-003 (Execução do Motor M2):** Executar `C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\run.py` localmente e assegurar compatibilidade retroativa (exit code 0).
4.  **T-004 (Homologação Pipeline):** Rodar a esteira integrada local `python validate_pipeline.py --skip-run` para atestar a integridade e ausência de falhas estruturais nos diretórios de cache.
