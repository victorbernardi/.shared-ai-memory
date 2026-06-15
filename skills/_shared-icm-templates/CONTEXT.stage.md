---
stage: <NÚMERO>_<nome-do-estagio>
layer: 2
role: stage_contract
inputs_from: [<estágio_anterior>, <outra_fonte>]
outputs_to: [<próximo_estágio>]
---

# CONTEXT.md — Contrato do Estágio <XX>: <Nome>

## 1. Propósito do Estágio

<Uma frase. Se precisar de duas, divida em dois estágios.>

## 2. Insumos (Inputs)

### Layer 3 — Referência (estável; internalizar como restrição)

- **<convenção/regra>:** `_config/<arquivo>` | `../../shared/<arquivo>`

### Layer 4 — Artefato de execução (per-run; processar como input)

- **<output anterior>:** `../<NN>_<estágio>/output/<arquivo>`

## 3. Tarefa e Processo

### 3.1 <Sub-etapa>

- <Ação específica>

### 3.2 <Sub-etapa>

- <Ação específica>

## 4. Restrições (CAIXA ALTA = fail-fast)

- **<CONSTRAINT>:** <detalhe>
- **Idempotência:** <como garantir que rodar 2x não quebra>

## 5. Artefatos de Saída

| Artefato | Localização | Formato | Critério de Aceitação |
|----------|-------------|---------|----------------------|
| <nome>   | `output/<arquivo>` | Markdown | <condição binária> |

## 6. Critérios de Conclusão

1. <Condição verificável e binária>
2. <Condição verificável e binária>

## 7. Handoff

- Output disponível em `output/` → próximo estágio consome como input
- <Se breakpoint humano: "Aguardar revisão antes de continuar">

## 8. Em Caso de Falha

1. Documentar falha em `output/error_log.md`
2. Sinalizar ao operador com mensagem clara
3. NUNCA propagar artefatos incompletos
