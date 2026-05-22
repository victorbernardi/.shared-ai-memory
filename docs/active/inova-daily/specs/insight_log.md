# 📓 INSIGHT LOG — Inova Daily (Mineração de Dados)

> **Criado:** 2026-05-14
> **Fase:** Research (Deep Mining)
> **Objetivo:** Catalogar todo achado relevante extraído dos datasets para alimentar o Relatório de Comando.

---

## INSIGHT #001 — "O Triunfo de Contagem" (Janeiro)
- **Tipo:** Concentração de Receita por Filial
- **Achado:** Contagem faturou R$ 20.4M em Janeiro, representando 66% do total da Inova.
- **Embasamento:** Dois SKUs de chassis (CNN25SED) somaram R$ 5.3M. Ticket médio desses itens: R$ 2.6M vs média geral de R$ 60K.
- **Implicação de Negócio:** Dependência extrema de Contagem e de vendas de projeto. Risco de volatilidade.
- **Status:** ✅ Validado

## INSIGHT #002 — "O Hiato dos Projetos" (Fevereiro)
- **Tipo:** Queda Abrupta de Faturamento
- **Achado:** Queda global de 22% (R$ 30.9M → R$ 23.9M). Contagem caiu 39% (R$ 20.4M → R$ 12.5M).
- **Embasamento:** Sem vendas de chassis de alto valor. Maior venda individual do mês: R$ 1.3M (vs R$ 2.9M em Jan).
- **Implicação de Negócio:** Fevereiro expõe o "chão real" da operação sem projetos especiais.
- **Status:** ✅ Validado

## INSIGHT #003 — "O Fenômeno TMG25SED" (Março)
- **Tipo:** SKU Anomalia (Super-Venda)
- **Achado:** SKU TMG25SED0405 vendido para SEMEP Logística por R$ 5.77M — uma única unidade.
- **Embasamento:** Histórico anterior deste SKU: ZERO vendas. Representou 18.5% de toda a receita de Março.
- **Implicação de Negócio:** Abertura de novo nicho de equipamentos pesados. Oportunidade de recorrência?
- **Status:** ✅ Validado

## INSIGHT #004 — "A Invasão da G-MAIA" (Abril)
- **Tipo:** Sorpasso de Cliente Líder
- **Achado:** Construtora G-MAIA superou a CSN como cliente #1 (R$ 5.77M vs R$ 5.69M).
- **Embasamento:** G-MAIA teve ZERO vendas em Jan/Fev/Mar. Comprou o MESMO SKU TMG25SED que apareceu em Março, porém desta vez faturado em Abril. CSN manteve estabilidade (média R$ 5.8M/mês).
- **Implicação de Negócio:** O SKU TMG25SED é um "cliente rotativo" — cada mês aparece em um comprador diferente. Quem compra em Maio?
- **Status:** ✅ Validado

## INSIGHT #005 — "O Ralo de Cancelamentos" (Acumulado)
- **Tipo:** Vazamento de Pipeline
- **Achado:** R$ 246.9M em orçamentos cancelados no acumulado.
- **Embasamento:** Principal motivo: "Preço menor no concorrente" (R$ 50.2M). Maior perda individual: CSN Mineração (R$ 16.2M).
- **Implicação de Negócio:** A CSN é simultaneamente o maior cliente e o maior "cancelador". Ela usa nossos orçamentos como benchmark?
- **Status:** ✅ Validado

## INSIGHT #006 — "O Churn Silencioso da Tradimaq"
- **Tipo:** Risco de Fidelidade
- **Achado:** Tradimaq S.A. possui GAP de R$ 26M com SOW de apenas 3.5% e 60 máquinas.
- **Embasamento:** Classificada como "Em Risco (<30%)" no motor de fidelidade. Potencial estimado 20x superior ao realizado.
- **Implicação de Negócio:** 60 máquinas com 3.5% de SOW = compra massiva no mercado paralelo ou na concorrência.
- **Status:** ✅ Validado

## INSIGHT #007 — "Os 639 Fantasmas" (Sonda C2: Churn Real)
- **Tipo:** Erosão Silenciosa da Base
- **Achado:** 639 clientes que compraram em Janeiro NÃO compraram mais em Abril/Maio. Faturamento perdido: R$ 4.74M.
- **Embasamento:** O Top 1 foi a **Construtora FPM** (R$ 1.44M em Jan, ZERO desde então). O Top 2 foi a **Valle Sul** (R$ 1.3M — compra de chassis, one-hit-wonder). A Cia. Siderúrgica Nacional (braço da CSN) também aparece com R$ 47K perdidos.
- **Implicação de Negócio:** 639 clientes = ~35% da base ativa de Janeiro. Perda silenciosa e não monitorada. Qual é o custo de aquisição de um cliente novo vs reativar um que saiu?
- **Critério Mina de Ouro:** ✅ Surpreendente | ✅ Acionável | ✅ Quantificável
- **Status:** ✅ MINA DE OURO

## INSIGHT #008 — "O Efeito Quinta-Feira" (Sonda T3: Dia da Semana)
- **Tipo:** Padrão de Sazonalidade Semanal
- **Achado:** Quinta-feira é o dia mais forte (R$ 31.7M acumulado, 4.155 NFs). Segunda-feira é o mais fraco (R$ 15M, 3.204 NFs).
- **Embasamento:** A diferença entre Quinta e Segunda é de **110%** em faturamento. O ticket médio do Sábado é o mais alto (R$ 3.820 vs R$ 1.320 na Segunda), sugerindo que os poucos pedidos de Sábado são de alto valor/urgência.
- **Implicação de Negócio:** O time comercial deveria concentrar ações de prospecção na Segunda (dia fraco) e garantir capacidade logística na Quinta (pico).
- **Critério Mina de Ouro:** ✅ Surpreendente | ✅ Acionável | ❌ Quantificável parcialmente
- **Status:** ✅ Validado

## INSIGHT #009 — "A Margem Escondida no 'Sem Subgrupo'" (Sonda P5: Margem)
- **Tipo:** Anomalia de Margem por Categoria
- **Achado:** O subgrupo "SEM SUBGRUPO" tem a **melhor margem bruta de toda a operação: 51.4%** (R$ 23.8M de margem sobre R$ 46.2M de receita).
- **Embasamento:** Filtros e o subgrupo vazio (genérico) empatam em ~35%. Lubrificantes têm margem de apenas 28.8%. "SEM SUBGRUPO" supera todos os classificados.
- **Implicação de Negócio:** Há R$ 46M faturados em itens SEM CLASSIFICAÇÃO DE SUBGRUPO. Isso é uma falha de cadastro que esconde a verdadeira lucratividade por categoria. Corrigir isso é uma oportunidade de auditoria de alto impacto.
- **Critério Mina de Ouro:** ✅ Surpreendente | ✅ Acionável | ✅ Quantificável
- **Status:** ✅ MINA DE OURO

## INSIGHT #010 — "Os Vendedores de Projeto vs Os de Prateleira" (Sonda V2: Consultores)
- **Tipo:** Perfil de Performance Comercial
- **Achado:** Dois perfis extremos:
  - **Samara:** 2.345 NFs, R$ 21.3M, ticket médio R$ 9.1K — vendedora de VOLUME com diversidade (2.219 SKUs).
  - **Sandro:** 5 NFs, R$ 11.1M, ticket médio R$ 2.2M — vendedor de PROJETO (3 SKUs apenas).
- **Embasamento:** Se Sandro fizer 1 venda a mais, equivale a 1.222 vendas da Samara. Flavio Caricatte com 2 NFs faturou R$ 2.29M (ticket R$ 1.14M).
- **Implicação de Negócio:** O faturamento da Inova é sustentado por 2 pilares totalmente diferentes: Volume (Samara, Arlan) e Projeto (Sandro, Thiago, Flavio). Perder um vendedor de Projeto impacta 10x mais que perder um de Volume.
- **Critério Mina de Ouro:** ✅ Surpreendente | ✅ Acionável | ✅ Quantificável
- **Status:** ✅ MINA DE OURO

## INSIGHT #011 — "A CSN é 48% da Inova" (Sonda C1: Concentração)
- **Tipo:** Risco de Concentração de Carteira
- **Achado:** A CSN Mineração sozinha responde por **47.9%** de todo o faturamento do Top 10.
- **Embasamento:** CSN faturou R$ 25.2M em 5 meses, com 2.365 NFs. O segundo lugar (G-MAIA com R$ 5.7M) tem 1/4 do faturamento e foi ativo em apenas 1 mês. Apenas 5 dos top 10 clientes foram ativos nos 5 meses do ano.
- **Implicação de Negócio:** Se a CSN reduzir compras em 20%, a Inova perde R$ 5M — equivalente a perder os clientes #2 e #3 combinados. Risco existencial de concentração.
- **Critério Mina de Ouro:** ✅ Surpreendente | ✅ Acionável | ✅ Quantificável
- **Status:** ✅ MINA DE OURO

---

## INSIGHT #012 — "Os 36 Gigantes Inertes" (Sonda Z1: Potencial Ouro)
- **Tipo:** Vazamento Massivo de Potencial
- **Achado:** 36 grupos econômicos com potencial > R$ 1M e SOW < 10%. GAP total desses grupos: **R$ 139.4M**.
- **Embasamento:**
  - **Tradimaq:** 60 máquinas, potencial R$ 26.9M, fatura apenas R$ 957K (SOW 3.5%).
  - **INOVA E:** 113 máquinas, potencial R$ 12.5M, faturamento **ZERO**. O maior parque de máquinas sem nenhuma compra.
  - **PH Comércio:** 27 máquinas, potencial R$ 6.3M, faturamento **ZERO**.
- **Implicação de Negócio:** R$ 139M em GAP concentrados em apenas 36 clientes. São os "alvos cirúrgicos" — cada 1% de conversão = R$ 1.39M em receita nova.
- **Critério Mina de Ouro:** ✅ Surpreendente | ✅ Acionável | ✅ Quantificável
- **Status:** ✅ MINA DE OURO

## INSIGHT #013 — "CSN: O Unicórnio do SOW 100%" (Sonda Z2: Frota vs Compra)
- **Tipo:** Benchmark de Excelência
- **Achado:** A CSN Mineração é o ÚNICO cliente do Top 10 de frota com **SOW de 100%** (Fat = Potencial: R$ 36M).
- **Embasamento:** CSN tem 86 chassi em 8 categorias diferentes. A Terrabel tem 70 chassi em 10 categorias mas só converte 23% (R$ 4.1M de R$ 17.8M). Tradimaq com 60 chassi converte 3.5%.
- **Implicação de Negócio:** O modelo de atendimento da CSN é o "padrão ouro" de como atender grandes frotas. O que a CSN tem que a Tradimaq não tem? Replicar esse modelo = potencial de R$ 100M+.
- **Critério Mina de Ouro:** ✅ Surpreendente | ✅ Acionável | ✅ Quantificável
- **Status:** ✅ MINA DE OURO

## INSIGHT #014 — "O Dataset RFM é de Vendas Brutas (Inclui Devoluções)" (Sonda Z4)
- **Tipo:** Descoberta Técnica / Auditoria
- **Achado:** O `cache_vendas_rfm.parquet` contém 162K transações com valores negativos (devoluções). Não é um segmento RFM calculado — é o dado bruto de NFs.
- **Embasamento:** Valores variam de -R$ 331K a +R$ 905K. Um único CNPJ (08902291 = CSN) tem 41.593 registros.
- **Implicação de Negócio:** Precisamos calcular o RFM (Recência, Frequência, Monetário) a partir deste cache, não consumi-lo como se fosse pré-calculado. Oportunidade de criar uma Engrenagem de Scoring de Fidelidade.
- **Status:** ✅ Validado (Descoberta Técnica)

## INSIGHT #015 — "CSN = R$ 93M em Peças (2025+2026)" (Sonda P_OURO)
- **Tipo:** Concentração Extrema de Receita
- **Achado:** O `dataset_ouro_pecas_grupo_v1` revela que a CSN acumula **R$ 93.2M líquidos** em peças (2025 + 2026 parcial).
- **Embasamento:** O segundo colocado (Minérios Nacional) tem R$ 13.6M — **7x menor**. A Tradimaq, com 60 máquinas, faturou apenas R$ 3.9M em peças.
- **Implicação de Negócio:** A CSN sozinha paga a operação de peças. Qualquer perda nesse cliente é catastrófica. Mas também: se a Tradimaq comprasse proporcionalmente ao seu parque, seriam mais R$ 23M/ano.
- **Critério Mina de Ouro:** ✅ Surpreendente | ✅ Acionável | ✅ Quantificável
- **Status:** ✅ MINA DE OURO

---

## PERGUNTAS EM ABERTO (A Investigar)
- [ ] O SKU TMG25SED vai aparecer novamente em Maio? Quem é o próximo comprador?
- [ ] A queda de Fevereiro é sazonal ou foi um evento isolado? Comparar com Fev/2025.
- [ ] CSN cancela R$ 16M mas fatura R$ 5.8M/mês. Qual é a taxa de conversão real?
- [ ] Existe um "cliente invisível" que compra pouco mas nunca cancela?
- [ ] Quais subgrupos de peças estão crescendo vs decaindo em 2026?
- [ ] Algum consultor tem taxa de cancelamento desproporcional?
- [x] O cache_vendas_rfm é RFM pré-calculado? **NÃO** — é dado bruto de NFs.
- [ ] O que a CSN faz de diferente que gera SOW 100%? Modelo de contrato? SLA?
- [ ] INOVA E: 113 máquinas e ZERO faturamento — é cliente fantasma ou está tudo no paralelo?
- [ ] Calcular RFM real a partir do cache para criar scoring de fidelidade.

---
*Log atualizado em 2026-05-14 18:38. Última mineração: Batch #003 (Datasets Ouro).*

