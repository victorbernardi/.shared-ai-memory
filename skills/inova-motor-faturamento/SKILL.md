---
name: inova-motor-faturamento
version: 1.0.0
description: >
  Use quando precisar executar o processamento e atualizacao do motor de faturamento local M2,
  consolidando o faturamento de pecas 2025 por Grupo Economico.
tools:
  - claude-code
  - antigravity
  - commandcode
tier: 1
category: orchestrator
triggers:
  - atualizar motor faturamento
  - inova-motor-faturamento
  - executar motor faturamento
author: Victor
---

# inova-motor-faturamento

## Objetivo
Prover automação e execução do motor de faturamento M2 para consolidação das notas fiscais do Proteus, garantindo a consistência das regras CDD e geração de outputs consolidados.

<!-- @if platform=claude -->
## Fluxo Detalhado

O fluxo completo de execução do motor de faturamento consiste em validar a governança, rodar o pipeline local de extração, transformação e carga, e auditar os resultados finais.

### 1. Pre-flight Check
Verifique os dados externos e a recência dos arquivos utilizando:
```bash
python scripts/governance_sensor.py
```
Isso garante que os dados fontes não estejam obsoletos.

### 2. Execução do Motor de Faturamento
Roda as três etapas principais (Extração, Transformação e Carga):
```bash
python run.py --stage faturamento
```
Ou sequencialmente:
1. `python extract.py`
2. `python transform.py`
3. `python load.py`

### 3. Validação dos Resultados
Execute a suíte de testes com pytest para garantir que não há regressão nos dados gerados:
```bash
pytest tests/
```

## Examples

### Exemplo 1: Execução Padrão
Input: Comando para rodar todo o pipeline de faturamento.
Output:
```
[INFO] Pre-flight check completo: Dados válidos.
[INFO] Iniciando extract.py...
[INFO] Extração de NFs do Protheus finalizada.
[INFO] Iniciando transform.py...
[INFO] Transformação e consolidação finalizadas.
[INFO] Iniciando load.py...
[INFO] Carga concluída.
[OK] Execução concluída com sucesso.
```

## Referências
- `CONTEXT.md` - Contexto técnico e de negócio do motor M2.
- `docs/plans/` - Planos de execução aprovados.
<!-- @endif -->

<!-- @if platform=antigravity,commandcode -->
## Fluxo

1. **Pre-flight**: Rode `python scripts/governance_sensor.py` para verificar integridade e recência.
2. **Executar**: Execute `python run.py --stage faturamento` (ou `extract.py`, `transform.py`, `load.py`).
3. **Validar**: Rode `pytest tests/` e certifique-se de que os testes passaram.
<!-- @endif -->

## Constraints

- NUNCA execute o motor analítico sem antes rodar o pre-flight check de governança.
- SEMPRE especifique explicitamente `encoding='utf-8'` em todas as operações de leitura/escrita de arquivo.
- SEMPRE valide o faturamento líquido por grupo econômico e salve o resultado na pasta `output/`.

## Scripts

- `run.py` — Script principal de orquestração do pipeline local.
- `extract.py` — Extração de NFs a partir da base Protheus.
- `transform.py` — Transformação e cálculo de ticket médio/faturamento.
- `load.py` — Escrita dos arquivos parquet consolidados.

## Critérios de Conclusão
A skill é considerada concluída quando o processamento de faturamento é executado com sucesso, os parquets consolidados de saída são atualizados na pasta de output correspondente e a suíte de testes valida os resultados com êxito.
