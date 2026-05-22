# SPEC: 2026-05-12 - Delta QSA Scanner Integration

## 1. Objetivo
Automatizar a detecção e coleta de dados societários (QSA) para novos clientes identificados no pipeline do Motor de Identidade (M0), eliminando a necessidade de execução manual do scanner e garantindo que o cruzamento de holdings (C9) esteja sempre atualizado.

## 2. Requisitos

### 2.1 Funcionais
- **Detecção de Delta:** Identificar CNPJs presentes no cache (`SA1010`) que não constam na base local de sócios (`qsa_base.json`).
- **Coleta On-the-fly:** Consultar o QSA via API para os novos registros identificados.
- **Persistência Incremental:** Atualizar o `qsa_base.json` sem sobrescrever dados existentes.
- **Não-Bloqueante (Opcional):** Se a API falhar, o batch deve continuar o processamento (Graceful Degradation).

### 2.2 Não-Funcionais
- **Performance:** Limitar a coleta síncrona a um threshold (ex: max 50 novos registros por batch) para não atrasar a geração do Excel oficial.
- **Estabilidade:** Respeitar limites de rate-limit das APIs públicas (ex: BrasilAPI).

## 3. Arquitetura Proposta

### 3.1 Componentes
- **Trigger:** Integrado ao início do `run_seo_ge_batch` em `seo_ge_batch_v11_7.py`.
- **Worker:** Reaproveitamento da lógica de crawler de `seo_ge_qsa_crawler.py`.
- **Storage:** `scripts/knowledge/qsa_base.json`.

### 3.2 Fluxo de Dados
1. Batch carrega `df_sa1`.
2. Extrai raízes únicas de CNPJ do `df_sa1`.
3. Carrega `qsa_base.json`.
4. `delta = master_raizes - qsa_raizes`.
5. Se `delta` não vazio:
    - Executa `run_delta_scan(delta_list)`.
    - Salva atualizações.
6. Continua unificação normal.

## 4. Validação (Plano de Testes - TDD)
- **Caso 1 (Detecção):** Fornecer lista com 1 CNPJ novo e validar que ele é identificado como delta.
- **Caso 2 (Coleta):** Mock da API para o novo CNPJ e verificar se o retorno é integrado ao dicionário de saída.
- **Caso 3 (Persistência):** Validar que o `qsa_base.json` cresceu após a execução.
- **Caso 4 (Threshold):** Validar que o scanner respeita o limite máximo de consultas por batch.
