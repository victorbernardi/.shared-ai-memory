# Spec: Auditoria de KPIs e Arquitetura de Ciclos de Alertas

**Data:** 2026-06-03
**Projeto:** lead-csc-pops
**Status:** Aprovada — pronta para implementação
**Revisão:** v2 — escopo reduzido após `stout-spec-validation` (P0 fechados por redução; entrega autossuficiente sem dependência de Fabric)

---

## Objetivo

Corrigir os indicadores do Daily Report com dados reais, substituir a arquitetura de rastreamento de tratativas por um modelo de ciclos de alerta, e eliminar bugs de dados fictícios no pipeline — tudo de forma autossuficiente (sem depender da expansão da query Fabric, adiada para a fase 2).

---

## Contexto

O pipeline atual rastreia tratativas comerciais em `historico_tratativas.json` a nível de chassi. Isso impede calcular aging real e distinguir ciclos de alerta. Além disso, o KPI `aging_medio` é hardcoded em 3.2 e o faturamento usa um fallback fictício de R$15k por venda quando o Fabric não retorna valor — número inventado exibido para a diretoria.

A validação de spec (v1 → v2) identificou que três KPIs (Aderência, Valor Orçamentos, Valor Faturado) e o fechamento de ciclo por tipo dependiam de dados do Protheus/Fabric não disponíveis nesta entrega. Esses itens foram movidos para **Evolução Futura** para fechar os achados P0 e entregar valor real agora.

---

## Requisitos Funcionais

### RF-01 — `ciclos_alertas.json` como fonte de verdade única

Substituir `historico_tratativas.json` por `ciclos_alertas.json`. Cada registro representa um ciclo de alerta por chassi + tipo (FPS ou Rodante).

**Schema (17 campos — campos de orçamento/NF reservados como `null` para a fase 2):**

```json
{
  "Chassi": "1T01050KLRD458782",
  "Tipo_Alerta": "FPS",
  "Data_Inicio_Ciclo": "2026-05-29",
  "Horimetro_Inicio": 200.0,
  "Data_Fechamento": null,
  "Horimetro_Fechamento": null,
  "Resultado": null,
  "Consultor": "Andre Alves",
  "Observacoes": "",
  "Orcamento_Protheus": null,
  "Data_Orcamento": null,
  "Valor_Orcamento": null,
  "Tipo_Resolucao": null,
  "Status_Orcamento": null,
  "Data_Conversao_NF": null,
  "NF_Numero": null,
  "Valor_Faturado": null
}
```

**Campos:**

- `Tipo_Alerta`: `"FPS"` | `"Rodante"`
- `Resultado`: `"Venda"` | `"Venda Perdida"` | `null` (em aberto)
- `Tipo_Resolucao`, `Status_Orcamento`, `Data_Orcamento`, `Valor_Orcamento`, `Data_Conversao_NF`, `NF_Numero`, `Valor_Faturado`: **reservados como `null` nesta entrega.** Serão populados na fase 2 (ver Evolução Futura). O schema já os contempla para evitar nova migração.

### RF-02 — Ciclos independentes por tipo, fechamento por chassi

Um chassi com `Alerta FPS e Alerta Rodante` abre **dois registros** em `ciclos_alertas.json` — um para cada tipo. Isso é estrutural e vale desde já.

**Regra de fechamento nesta entrega (sem resolução por tipo):**

- `Resultado = "Venda"` → fecha **todos** os ciclos ativos do chassi.
- `Resultado = "Venda Perdida"` → fecha **todos** os ciclos ativos do chassi (standby).
- `"Sem Contato"` → **não fecha** nenhum ciclo, não reseta `Horimetro_Base`.

> **Nota de escopo:** o fechamento seletivo por tipo (fechar só FPS mantendo Rodante) depende de `Tipo_Resolucao`, que exige os itens do orçamento no Fabric — **adiado para a fase 2**. Até lá, qualquer venda fecha todos os ciclos ativos do chassi; eles reabrem no próximo disparo de horímetro.

### RF-03 — Reset correto de `alertas_ocorrencias.parquet`

Quando um chassi é tratado com "Venda" ou "Venda Perdida", seu registro em `alertas_ocorrencias.parquet` deve ser **removido**. No próximo ciclo, quando o alerta disparar novamente, o chassi entra como `Primeiro_Alerta = True` e ganha nova `Data_Primeiro_Alerta`.

Isso garante que o parquet rastreia "está em alerta agora pela primeira vez neste ciclo", não "já foi alertado alguma vez na vida".

### RF-04 — "Sem Contato" não reseta horímetro

`aplicar_reentrada` em `transform.py` deve resetar `Horimetro_Base` apenas para `["Venda", "Venda Perdida"]`. "Sem Contato" mantém o horímetro base e o lead permanece na planilha como pendente.

### RF-05 — Aging real calculado do `ciclos_alertas.json`

```
aging_medio = média(Data_Fechamento − Data_Inicio_Ciclo) em dias
              para ciclos com Resultado != null
```

Fallback: exibir `"N/A"` se não houver ciclos fechados.

### RF-06 — Migração dos 31 registros existentes

Script de migração pontual: converter registros de `historico_tratativas.json` para o schema de `ciclos_alertas.json`. O `Tipo_Alerta` dos registros migrados será inferido do campo `Gatilho` existente. Os campos de orçamento/NF migrados preservam o que já existe no legado; os ausentes ficam `null`. Após validação, `historico_tratativas.json` é deprecado.

### RF-07 — Remoção de dados fictícios

Eliminar o fallback de R$15k por venda em `load.py` (linhas 278-279 da versão atual) e o `aging_medio` hardcoded de 3.2. KPIs com dados insuficientes exibem `"N/A"` ou `R$ 0,00` — nunca valor inventado.

---

## KPI Set Final (5 indicadores — todos autossuficientes)

| # | Indicador | Cálculo | Fonte | Exibição |
|---|-----------|---------|-------|----------|
| 1 | Adesão Comercial (Semana) | `(Venda + Venda Perdida) / total_leads` | `df_leads_final` | Card |
| 2 | Conversão Acumulada | `Vendas / (Vendas + Venda Perdida)` | `ciclos_alertas.json` | Card |
| 3 | Leads Pendentes | sem feedback **ou** com "Sem Contato" | `df_leads_final` | Card |
| 4 | Potencial Financeiro | `sum(Potencial Peças Anual)` | M3 parquet | Card |
| 5 | Aging Médio | `média(Data_Fechamento − Data_Inicio_Ciclo)` | `ciclos_alertas.json` | Tabela |

Nenhum KPI depende do Fabric. Todos são populados por código presente nesta entrega (sem métrica de código morto).

---

## Requisitos Não-Funcionais

| ID | Requisito | Racional |
|----|-----------|----------|
| NFR-01 | Sem novas colunas na planilha Excel | Todo rastreamento via JSON; não poluir o relatório do consultor |
| NFR-02 | Nenhum valor fictício no HTML | Dados insuficientes exibem `"N/A"` / `R$ 0,00`; e-mail vai para diretoria |
| NFR-03 | Antifragilidade | Falha ao ler/gravar JSON não para o pipeline (try/except com warning) |
| NFR-04 | Migração validada antes de deprecar | `ciclos_alertas.json` só substitui o legado após conferência dos 31 registros |
| NFR-05 | Schema forward-compatible | Os 17 campos já contemplam a fase 2; nenhuma migração adicional será necessária |

---

## Arquitetura — Mudanças por Arquivo

### `src/history.py`

- Criar `abrir_ciclo(chassi, tipo_alerta, horimetro_inicio, consultor)`
- Criar `fechar_ciclo(chassi, tipo_alerta, resultado, horimetro, orcamento, valor)` — `tipo_alerta=None` fecha todos os ciclos ativos do chassi
- Criar `carregar_ciclos()` — substitui `carregar_historico()`
- Deprecar `carregar_historico()` e `atualizar_historico()`
- **Fora desta entrega:** `atualizar_status_orcamento()` (fase 2)

### `src/transform.py`

- `aplicar_reentrada`: apenas `["Venda", "Venda Perdida"]` resetam `Horimetro_Base`
- `aplicar_reentrada`: chamar `fechar_ciclo(chassi, None, retorno, h, None, 0.0)` para cada chassi tratado (fecha todos os ciclos do chassi)

### `run.py`

- Após `aplicar_reentrada`: remover chassi tratados de `alertas_ocorrencias.parquet`
- Ao gerar leads ativos: chamar `abrir_ciclo()` para cada tipo de alerta presente no `Gatilho_Alerta`
- **Sem reordenação do fluxo Fabric** (a auditoria existente segue como está)

### `src/load.py`

- `calcular_kpis_dashboard`: reescrever usando `ciclos_alertas.json` + `df_leads_final` (5 KPIs)
- Remover fallback fictício de R$15k
- Remover `aging_medio` hardcoded
- "Sem Contato" excluído de `leads_tratados`/`taxa_adesao`; incluído em `leads_pendentes`
- CSS `success` condicional: aplicar apenas se valor > 0
- HTML: 4 cards (Adesão, Conversão, Pendentes, Potencial) + tabela com Aging

### `src/extract.py`

- **Sem mudança nesta entrega.** A expansão da query (status orçamento + NF) é fase 2.

---

## Matriz de Rastreabilidade (RF → Teste)

| RF | Cobertura de Teste |
|----|--------------------|
| RF-01 | `test_abrir_ciclo_fps`, `test_abrir_dois_ciclos_mesmo_chassi`, `test_carregar_ciclos_vazio` |
| RF-02 | `test_fechar_ciclo_fecha_todos_do_chassi`, `test_aplicar_reentrada_fecha_ciclos` |
| RF-03 | `run.py` reset (validação manual + `test_aplicar_reentrada`) |
| RF-04 | `test_aplicar_reentrada` (Sem Contato mantém base) |
| RF-05 | `test_aging_medio_real`, `test_aging_nenhum_ciclo_fechado` |
| RF-06 | `scripts/migrar_historico_para_ciclos.py` (validação de saída: 31 registros) |
| RF-07 | `test_sem_fallback_ficticio`, `test_aging_nenhum_ciclo_fechado` |

---

## Plano de Testes

- [ ] Abrir ciclo FPS grava registro com `Resultado=null` e campos de orçamento `null`
- [ ] Chassi com FPS+Rodante abre dois registros independentes
- [ ] `fechar_ciclo(tipo=None)` fecha todos os ciclos ativos do chassi
- [ ] "Sem Contato" não fecha ciclo, não reseta `Horimetro_Base`, permanece pendente
- [ ] `alertas_ocorrencias.parquet` remove chassi tratados corretamente
- [ ] Chassi tratado reaparece com `Primeiro_Alerta = True` no ciclo seguinte
- [ ] Aging calculado corretamente para ciclos com `Data_Fechamento` preenchida
- [ ] Aging exibe "N/A" quando não há ciclos fechados
- [ ] Adesão conta apenas Venda + Venda Perdida (Sem Contato fora)
- [ ] Leads Pendentes inclui Sem Contato e vazios
- [ ] Migração: 31 registros convertidos sem perda de dados
- [ ] Nenhum valor fictício (R$15k) aparece no HTML gerado
- [ ] Cards verdes apenas quando valor > 0

---

## Evolução Futura (Fase 2 — fora desta entrega)

Depende de exploração e expansão das tabelas Protheus no Fabric:

| Item | O que destrava |
|------|----------------|
| Expandir query Fabric (`VS1010` status + `SF2010` NF) | KPIs Valor Total de Orçamentos e Valor Faturado |
| Wire auditoria → `fechar_ciclo` / `atualizar_status_orcamento` | KPI Aderência de Propostas (Ponte da Verdade) |
| Mapear itens do orçamento (FPS vs Rodante) | `Tipo_Resolucao` → fechamento seletivo por tipo (RF-02 completa) |
| Rastrear ciclo do orçamento até a NF | `Status_Orcamento`: Aberto → Convertido / Cancelado |

## Fora do Escopo (permanente)

- Fluxo de compartilhamento via `emails_compartilhamento.json` (outro projeto; grupo `coordenadores_gerentes_outros`)
- Expansão de destinatários do e-mail diário além de Roberto e Gabriela
