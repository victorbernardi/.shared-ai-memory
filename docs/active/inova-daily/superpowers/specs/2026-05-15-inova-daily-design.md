# Spec: Inova Daily — Briefing Executivo Diário de Vendas de Peças

**Data:** 2026-05-15  
**Prazo de entrega:** 2026-05-18 (segunda-feira, manhã)  
**Stakeholder principal:** Roberto (Gerente de Vendas)  
**Autor:** Victor Bernardi  

---

## 1. Objetivo

Entregar diariamente na caixa de entrada de Roberto um briefing executivo de vendas de peças da Inova. O e-mail deve responder três perguntas em menos de 3 minutos de leitura:

1. **Como foi ontem?** — foto do dia anterior com contexto histórico
2. **Estamos melhorando ou caindo?** — tendência comparativa
3. **O que merece atenção?** — highlights do mês em revisão (semana 1)

A validação dos dados será feita pelo próprio Roberto através do uso diário. Ajustes de calibragem ocorrem iterativamente a partir da segunda entrega (terça-feira 19/05).

---

## 2. Estrutura do E-mail

Cada e-mail é composto por dois blocos fixos:

### Bloco 1 — RECAP DO MÊS *(apenas semana 1, um mês por dia)*

| Dia | Mês em revisão |
|-----|---------------|
| Segunda 18/05 | Janeiro 2026 |
| Terça 19/05 | Fevereiro 2026 |
| Quarta 20/05 | Março 2026 |
| Quinta 21/05 | Abril 2026 |
| Sexta 22/05 | Maio 2026 (parcial) |

Conteúdo do recap:

- Faturamento total do mês vs mesmo mês em 2025 (YoY)
- Melhor dia do mês e valor
- Top 3 vendedores do mês
- Top 3 filiais do mês
- Cliente destaque (maior faturamento)
- Família de produto em destaque
- 1 anomalia notável: dia com faturamento `> 2x` ou `< 0.3x` a média diária do mês (se não houver anomalia, exibir o melhor e o pior dia)

### Bloco 2 — FOTO DE ONTEM *(todos os dias, sempre presente)*

- Faturamento total do dia anterior + quantidade de NFs
- Top 3 vendedores do dia
- Top 3 filiais do dia
- Acumulado do mês atual vs meta do mês (ex: "67% da meta, 12 dias úteis restantes")
- Comparativo YoY: mês atual acumulado vs mesmo período do ano anterior
- Tendência dos últimos 3 dias úteis: **Crescendo ↑ / Estável → / Caindo ↓**

**Cálculo de tendência:**

- Média diária dos últimos 3 dias úteis vs média diária dos 3 dias úteis anteriores
- `> +5%` → Crescendo ↑
- Entre `-5%` e `+5%` → Estável →
- `< -5%` → Caindo ↓

---

## 3. Fonte de Dados

### Motor de Faturamento (M2) — fonte única

**Arquivo principal:** `C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\data\cache_vendas_rfm.parquet`

- 202.881 transações de peças desde Jan/2025
- Colunas: CNPJ/CPF, nome cliente, filial, data NF, TES, centro de custo, grupo econômico, número NF, descrição produto, valor
- Cobre 2025 completo + 2026 até data atual → habilita YoY e recaps mensais

**Verificação de atualização:**

1. Ler última linha do log: `02_Faturamento/data/run.log`
2. Se data do log ≠ hoje → executar `run.py --no-cache` do M2 (~90s)
3. Fallback: usar `os.path.getmtime(cache_vendas_rfm.parquet)` se log não existir

**Janela de execução:** após 18h — nenhuma venda é registrada após esse horário.

**Metas mensais:** lidas diretamente de `C:\Projetos\Inova\projects\metas-pecas\data\Metas de peças John Deere 2026 - Revisão março.xlsx` (Planilha1, linha "Total"). Valores Jan-Mai 2026:

| Mês | Meta |
|-----|------|
| Janeiro | R$ 12.850.235,99 |
| Fevereiro | R$ 12.850.235,99 |
| Março | R$ 13.381.474,99 |
| Abril | R$ 13.466.411,88 |
| Maio | R$ 13.646.411,88 |

Arquivo também tem breakdown por filial (Contagem, Tanguá, Serra, Uberlândia, Pouso Alegre) — disponível para comparativo de filiais vs meta. Caminho configurado em `src/config.py` como `METAS_PATH`.

---

## 4. Arquitetura Técnica

```
run_daily.py --mes <1-5>
    │
    ├── check_and_update_m2()       # verifica log M2, atualiza se necessário
    │
    ├── src/faturamento.py          # carrega cache_vendas_rfm.parquet
    │   └── consultas: por_dia(), por_mes(), por_filial(), por_vendedor()
    │
    ├── src/snapshot_diario.py      # Bloco 2: foto de ontem
    │   └── consome: faturamento.py
    │
    ├── src/recap_mensal.py         # Bloco 1: highlights do mês (--mes 1-5)
    │   └── consome: faturamento.py
    │
    └── src/generator.py            # compõe blocos + preenche template → output
        └── salva: data/outputs/DAILY_ROBERTO_YYYYMMDD_HHMM.md
```

### Módulos

**`src/faturamento.py`** — novo, fonte única de dados
Carrega `cache_vendas_rfm.parquet` uma vez e expõe funções puras de consulta filtradas por data, filial, vendedor. Aplica filtro de TES válidos (`TES_ALL_VALID` do `config.py`).

**`src/snapshot_diario.py`** — novo (substitui `current_history.py`)
Monta o Bloco 2 completo: dia anterior, acumulado do mês, YoY, tendência, top vendedores e filiais.

**`src/recap_mensal.py`** — novo (substitui `recap_2026.py`)
Dado um mês (1–5), extrai highlights do Bloco 1 consultando `faturamento.py`.

**`src/generator.py`** — atualizado
Compõe os dois blocos e preenche o template Markdown. Salva output em `data/outputs/`.

**`run_daily.py`** — novo ponto de entrada na raiz do projeto

```bash
python run_daily.py --mes 1   # semana 1: recap Janeiro + snapshot
python run_daily.py --mes 2   # semana 1: recap Fevereiro + snapshot
python run_daily.py           # após semana 1: apenas snapshot
```

---

## 5. Template de Output

Arquivo: `templates/email_template_v3.md`

Estrutura:

```
[Assunto] Inova Daily — {data} | {faturamento_ontem} | Tendência {sinal}

## {MÊS EM REVISÃO} — Recap
{highlights do mês}

---

## Foto de Ontem — {data_ontem}
{snapshot com comparativos}
```

---

## 6. Entrega e Envio

- **Geração:** toda noite após 18h, executando `run_daily.py`
- **Envio:** manual por Victor (copia output Markdown para Gmail/Outlook)
- **Automação de envio:** fase 2 — não está no escopo desta entrega

---

## 7. Fora de Escopo (Esta Entrega)

- Envio automático de e-mail via SMTP ou API
- Integração com snapshots do dashboard-inova-data-export
- Scanners de anomalia (fidelidade, frota, vazamento) — fase 2
- Alertas de clientes em risco — fase 2
- Dashboard interativo — fase 2

---

## 8. Critério de Sucesso

Roberto recebe o e-mail na segunda-feira 18/05 antes das 9h com:

- Recap de Janeiro 2026 com highlights relevantes
- Foto de sexta-feira 15/05 com faturamento, top vendedores, top filiais, posição vs meta e sinal de tendência
- Conteúdo legível em menos de 3 minutos
- Números que Roberto consegue reconhecer como plausíveis

A calibragem de acurácia ocorre iterativamente a partir da entrega de terça 19/05.
