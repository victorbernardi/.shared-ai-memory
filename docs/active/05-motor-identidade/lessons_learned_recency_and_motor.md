# Lições Aprendidas — Integração de Dados & Recência M0
> **Projeto:** Motor Identidade M0 / Recency Status Report
> **Data:** 19 de Maio de 2026

Este documento registra as lições aprendidas, as discrepâncias de schema encontradas e mitigadas, os bugs de infraestrutura resolvidos e as recomendações estratégicas para o avanço da arquitetura **Stout** (Configuration-Driven Development).

---

## 🔍 1. Desvios Técnicos & Onde Poderíamos Ter Feito Melhor

### O Caso da Coluna Oculta de Oficina (`VO1010`)
*   **O Problema:** O script de processamento legado `motor_identidade_m0.py` sugeria o uso da coluna `VO1_PROVEI` na consulta da tabela `VO1010` no Microsoft Fabric. No entanto, o batch principal de unificação `seo_ge_batch_v11_7.py` esperava ler uma coluna chamada `VO1_XCLIEN` do cache Parquet local para renomeá-la para `VO1_PROVEI` em memória.
*   **A Ação:** Em vez de confiar cegamente no código fonte do script legado, criamos e executamos um utilitário de diagnóstico de schema (`check_all_caches.py`) para ler os cabeçalhos físicos dos Parquets ativos. Isso revelou que a consulta em produção real usava `VO1_XCLIEN`.
*   **Lição:** **Nunca assuma o schema de banco a partir de scripts antigos.** Sempre use assinaturas físicas de arquivos e esquemas reais como fonte única da verdade técnica. O diagnóstico de parquet físico antes da escrita do ETL nos poupou de uma quebra silenciosa no batch.

---

## 🐛 2. Bugs Identificados e Corrigidos

### Quebra de Caracteres no Windows Console (`UnicodeEncodeError`)
*   **Bug:** Sistemas Windows utilizam por padrão a codificação `cp1252` na console do PowerShell. Quando os logs do Python tentavam imprimir caracteres UTF-8 e status em Português, o terminal quebrava a execução com `UnicodeEncodeError`.
*   **Correção:**
    *   No Python (`seo_ge_ingest_fabric.py`): Implementamos um encapsulador de stdout que detecta e força a console a operar em UTF-8:
        ```python
        if sys.platform == "win32" and sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        ```
    *   No PowerShell (`seo_ge_update_pipeline.ps1`): Forçamos as variáveis globais de console:
        ```powershell
        $OutputEncoding = [System.Text.Encoding]::UTF8
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        ```

### Proteção de Rate-Limit no Scan PJ (BrasilAPI)
*   **Bug/Risco:** O batch do motor v11.7 detectou 800 novas raízes PJ pendentes de Quadro Societário (QSA). Tentar crawlar todas em uma única execução causaria o bloqueio imediato de IP pela BrasilAPI.
*   **Correção:** A engine v11.7 já implementa um watchdog limitador de delta PJ (máximo 50 consultas por rodada com delay de 1 segundo). Validamos que a automação executou em lotes seguros, integrando novos registros sem estourar quotas.

---

## 🏗️ 3. Como Melhorar o Projeto Stout (Arquitetura CDD)

### Recomendação A: Governança de Schemas por Configuração (Strict CDD)
*   **Ideia:** Atualmente, as colunas esperadas do Protheus estão hardcoded dentro do script de extração (`seo_ge_ingest_fabric.py`). Sob os princípios CDD do Stout, os schemas deveriam residir em um arquivo de contrato declarativo de dados (ex: `data/config/schemas.json`).
*   **Como ficaria:** O script Python leria este arquivo de configuração para construir as queries SQL dinamicamente e aplicar as validações estruturais de forma abstrata. Isso eliminaria código acoplado.

### Recomendação B: Módulo Centralizado de Encodings e Logs
*   **Ideia:** A necessidade de forçar o UTF-8 em terminais Windows ocorre em múltiplos projetos da Inova.
*   **Como ficaria:** Stout deveria disponibilizar um utilitário compartilhado em `/shared/utils/logging.py` que configure automaticamente o TextIOWrapper e os encodings de console do PowerShell ao importar, garantindo conformidade sistêmica e eliminando código duplicado.

### Recomendação C: Padronização de Logs Estruturados (JSON Log)
*   **Ideia:** O orquestrador lê logs textuais padrão (`INFO`, `SUCCESS`).
*   **Como ficaria:** Evoluir os motores locais para emitirem logs estruturados em JSON de linha única. Isso facilitará a ingestão por sistemas corporativos de monitoração e auditoria.
