# Template: CONTEXT.md — Contrato de Estágio ICM

Copie este template para cada estágio do workspace e preencha as 8 seções.

```markdown
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
- **<Fonte 1>:** <caminho concreto — nunca "o operador vai informar">
- **<Fonte 2>:** <caminho concreto>

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
```

## Regras de Preenchimento

| Seção | Regra |
|-------|-------|
| Propósito | Uma frase. Mais que isso = estágio grande demais |
| Insumos | Caminhos concretos. Input de estágio anterior = `../<estágio>/output/` |
| Restrições | CAIXA ALTA. Máximo 5. Lidas como fail-fast pelo agente |
| Critérios de Conclusão | Binários. "Script executou sem erro" é binário. "Ficou bom" não é |
| Handoff | Sempre explicitar destino. Breakpoint humano deve ser claro |
| Em Caso de Falha | Obrigatório. Sem isso, agente tenta "consertar sozinho" |
