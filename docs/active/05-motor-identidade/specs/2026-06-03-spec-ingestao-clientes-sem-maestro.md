# Spec: Ingestão de Clientes Sem ID_GRUPO_MAESTRO no M0

**Data:** 2026-06-03
**Origem:** Análise cross-stage M3 × M0 × RFM
**Status:** Proposta — implementar em sessão dedicada

---

## 1. Contexto

Durante a sessão de 2026-06-03, ao adicionar `ID_GRUPO_MAESTRO` aos datasets do M3, foram identificados **589 clientes individuais** com CNPJ válido mas sem correspondência no M0.

Esses clientes têm `CNPJ_GRUPO` como 8 dígitos (fallback do M3 quando não há match em `CNPJ_ORIGINAL` do M0) e representam **R$ 56.569.179** de potencial de peças.

### Perfil dos 589

| Categoria | Qtd | Potencial |
|---|---|---|
| Nunca compraram da Inova (sem RFM) | 585 | R$ 55.438.747 |
| Compradores com grupo já no M0 (CNPJ_ORIGINAL faltando) | 4 | R$ 1.130.432 |

Os 585 são máquinas identificadas via PoPS/oficina de terceiros cujos proprietários nunca tiveram transação com a Inova — portanto não estão no SA1010 (ERP Protheus). O caminho de ingestão é via **Receita Federal** (CNPJ público), não via cache de vendas.

---

## 2. Objetivo

Fazer o M0 capturar e catalogar os 589 CNPJs pendentes, gerando `ID_GRUPO_MAESTRO` para todos eles e reduzindo o gap de identidade no M3.

---

## 3. Fonte dos CNPJs Pendentes

Arquivo gerado pelo M3 a cada execução:

```
C:\Projetos\Inova\pipelines\potencial-clientes\03_Potencial\data\fila_ingestao_m0_pendente.xlsx
```

- **576 grupos** (CNPJ-raiz de 8 dígitos) sem cadastro no M0
- Gerado automaticamente pelo `build_exports` do M3

---

## 4. Mecanismo de Ingestão no M0

O M0 já possui a infraestrutura de ingestão via QSA/Receita Federal:

| Script | Função |
|---|---|
| `scripts/seo_ge_batch_v11_7.py` | Batch de enriquecimento de novos CNPJs |
| `scripts/seo_ge_qsa_crawler.py` | Crawler QSA (Receita Federal) |
| `scripts/seo_ge_scanner.py` | Scanner de grupos econômicos |

O fluxo esperado:

1. Ler `fila_ingestao_m0_pendente.xlsx` como input
2. Para cada CNPJ-raiz: buscar razão social e sócios na Receita Federal
3. Aplicar lógica de agrupamento do M0 (C1-C8)
4. Incorporar novos registros no `dataset_ouro_identidade.parquet`

---

## 5. Requisitos

1. **Leitura da fila:** M0 deve aceitar `fila_ingestao_m0_pendente.xlsx` como fonte de entrada adicional
2. **Enriquecimento QSA:** buscar razão social + CNPJ completo para os 576 CNPJ-raiz
3. **Agrupamento:** aplicar regras C1-C8 do Maestro para detectar grupos econômicos
4. **Saída:** novos registros adicionados ao `dataset_ouro_identidade.parquet`
5. **Não destrutivo:** não alterar registros existentes — apenas append de novos

---

## 6. Critério de Sucesso

Após execução:

```python
# Rodar M3 e verificar redução
clientes_sem_maestro_antes = 589
clientes_sem_maestro_depois = ?  # esperado: < 100
```

Redução dos 589 para menos de 100 clientes sem maestro.

---

## 7. Casos de Teste (Prioritários por Potencial)

| Cliente | CNPJ | CNPJ_GRUPO | Potencial |
|---|---|---|---|
| RODOCON CONSTRUCOES | 30090575000166 | 30090575 | R$ 406.950 |
| USINA DELTA UNIDADE DELTA | 13537735000109 | 13537735 | R$ 404.326 |
| JBS CONFINAMENTO | 02916265000160 | 02916265 | R$ 169.458 |
| CLEALCO ACUCAR ALCOOL | 45483450000110 | 45483450 | R$ — |
| LINS AGROINDUSTRIAL | 35637796000172 | 35637796 | R$ — |

---

## 8. Dependências

- Conexão ao Fabric ativa (autenticação MSAL device code)
- Acesso à Receita Federal / QSA (pode exigir proxy ou rate limiting)
- `fila_ingestao_m0_pendente.xlsx` gerado por execução recente do M3

---

## 9. Referências

- Análise original: sessão 2026-06-03 (M3 × M0 × RFM lab)
- Script de ingestão existente: `00_Motor_Identidade/scripts/seo_ge_batch_v11_7.py`
- Fila pendente: `03_Potencial/data/fila_ingestao_m0_pendente.xlsx`
- Parquet M0: `shared/data/dataset_ouro_identidade.parquet`
