# BRD — Campanha de Leads Preventivos de Peças

**Inova Máquinas | FPS & Material Rodante**

> **Data:** 28/05/2026
> **Versão:** 1.0
> **Patrocinador:** Roberto (Gerente de Peças)
> **Elaborado por:** Victor Bernardi

---

## 1. Resumo Executivo

A Inova Máquinas opera uma frota ativa de máquinas John Deere cujos consumidores críticos de peças — **Ferramentas de Penetração de Solo (FPS)** e **Material Rodante** — se desgastam em função das horas trabalhadas, não do calendário. Hoje, o contato comercial para reposição acontece de forma reativa (o cliente liga quando a peça quebra), o que gera perda de receita, risco de parada de equipamento e perda de timing do discurso de venda.

Este projeto entrega um **motor automatizado de geração de leads preventivos**: com base nos horímetros lidos diariamente de cada máquina, o sistema identifica automaticamente os ativos que estão próximos do ponto de desgaste e gera uma lista estruturada de oportunidades para os consultores e CSAs abordarem de forma proativa.

O resultado esperado é transformar peças de peças de um processo reativo para um **processo previsível e auditável**.

---

## 2. Objetivos de Negócio (SMART)

| # | Objetivo | Meta | Prazo |
|---|----------|------|-------|
| 1 | Aumentar a taxa de contato preventivo com clientes de FPS e Rodante | 100% dos alerts gerados com consultor designado | Imediato (semana 1) |
| 2 | Reduzir o tempo médio de tratativa do lead (Aging) | Primeiro contato em até 3 dias úteis do alerta | 30 dias |
| 3 | Garantir auditoria sistêmica das vendas declaradas | 100% das "Vendas" cruzadas com proposta real no Protheus | Contínuo |
| 4 | Gerar visibilidade financeira do pipeline de peças | KPI de pipeline em R$ disponível no Daily Report | Semana 1 |

---

## 3. Problema a Resolver

**Situação atual:**

- Os consultores não têm visibilidade de quais máquinas da base estão próximas do limiar de desgaste de FPS ou Rodante.
- O contato acontece quando o cliente percebe o problema — geralmente tarde demais para uma venda de valor.
- Não há como auditar se o consultor realmente fez o contato e gerou uma proposta, criando risco de falso reporte de resultados.

**Impacto:**

- Perda de oportunidades de venda de peças de alto giro.
- Risco de o cliente comprar de concorrente por falta de abordagem preventiva.
- Relatórios de desempenho sem validação cruzada com o ERP.

---

## 4. Solução Proposta

### Como funciona para o negócio

1. **Monitoramento diário de horímetros:** Os horímetros de todos os equipamentos da base ativa são lidos e processados diariamente pelo sistema.
2. **Publicação semanal da planilha de leads:** Toda segunda-feira, os alertas acumulados são publicados na planilha online compartilhada no OneDrive, com as colunas do lead bloqueadas para proteção dos dados.
3. **Consultores e CSAs registram o contato:** As únicas células editáveis são o status do contato (`Venda`, `Venda Perdida`, `Sem Contato`) e o campo de observações livres.
4. **Daily Report por e-mail:** Gerentes/Coordenadores recebem diariamente um painel de KPIs da campanha com a saúde comercial da equipe.
5. **Auditoria automática via Protheus:** O sistema cruza automaticamente os leads marcados como "Venda" com as propostas reais geradas no ERP — eliminando falsos positivos.

### Réguas de Alerta (Quando o sistema dispara)

| Tipo de Peça | Equipamento | Gatilho |
|---|---|---|
| **FPS** (dentes, lâminas, pontas) | Todos os equipamentos ativos | A cada **+200 horas** de operação |
| **Material Rodante** | Tratores de Esteira (700J, 750J, 850J, 1050K) | A cada **+1.500 horas** de operação |
| **Material Rodante** | Escavadeiras (130G, 160G, 200G, 210G, 350G…) | A cada **+3.000 horas** de operação |

> **Reinício do ciclo:** Após o lead ser tratado (`Venda` ou `Venda Perdida`), o horímetro é zerado e o contador recomeça do zero para aquela máquina. Leads `Sem Contato` continuam acumulando horas.

---

## 5. Como os Alertas Funcionam — Guia Completo

### O que é um alerta?

Um alerta é uma notificação automática gerada pelo sistema quando uma máquina da base ativa acumula horas suficientes de operação para indicar que suas peças de desgaste estão próximas do limite. É o sistema "avisando" o consultor: *"este cliente provavelmente vai precisar de peças em breve — ligue antes que ele precise".*

### Por que gerar alertas preventivos?

Peças como dentes de caçamba, lâminas de trator e material rodante (esteiras, rodas) se desgastam proporcionalmente ao uso do equipamento. Quando a máquina para por quebra, o cliente perde produtividade e pode comprar a peça de qualquer fornecedor. Com o alerta preventivo, o consultor chega antes do problema — no momento em que o cliente ainda está operando e receptivo à negociação.

---

### Régua de Alertas — Carga Inicial (Primeiro Processamento)

Na primeira vez que o sistema processa um chassis, ele **não tem histórico** de quando a última peça foi trocada. Para não gerar alertas imediatos em toda a frota (o que sobrecarregaria a equipe), a regra de carga inicial é:

> **O horímetro atual da máquina é registrado como o ponto de partida (marco zero).** O primeiro alerta só será gerado após acumular as horas definidas pela régua *a partir desse momento*.

**Exemplo prático:**

- Uma escavadeira 200G entra no sistema com 4.200h no horímetro.
- O sistema registra 4.200h como marco zero.
- O próximo alerta de Rodante será gerado quando o horímetro atingir **7.200h** (4.200 + 3.000).
- O próximo alerta de FPS será gerado quando atingir **4.400h** (4.200 + 200).

Isso garante que a campanha começa de forma ordenada, sem gerar ruído desnecessário para a equipe comercial.

---

### Régua de Alertas — Cargas Subsequentes (Ciclo Contínuo)

Após a carga inicial, o sistema opera em ciclo contínuo. A cada atualização semanal (toda segunda-feira), o sistema:

1. Lê o horímetro atual de cada máquina.
2. Compara com o marco zero daquele chassis.
3. Se a diferença atingir ou ultrapassar o limiar da régua, **gera um alerta**.

| Tipo de Peça | Equipamento | Limiar de Alerta |
|---|---|---|
| **FPS** — dentes, lâminas, pontas de caçamba e trator | Toda a frota ativa | +200 horas desde o marco zero |
| **Material Rodante** | Tratores de Esteira (700J, 750J, 850J, 1050K) | +1.500 horas desde o marco zero |
| **Material Rodante** | Escavadeiras (130G, 130P, 160G, 160P, 180G, 200G, 200P, 210G, 210P, 350ZX, 350G) | +3.000 horas desde o marco zero |

> **Por que limiares diferentes para Rodante?** Tratores de esteira se locomovem continuamente — suas esteiras estão em atrito constante com o solo. Escavadeiras trabalham majoritariamente paradas, rodando as esteiras apenas nas transferências entre obras. Por isso, o desgaste do rodante é muito mais rápido nos tratores.

---

### O Ciclo de Vida de um Lead

```
[Máquina atinge o limiar de horas]
          ↓
[Sistema gera o alerta na planilha]
          ↓
[Consultor vê o lead e faz o contato]
          ↓
    ┌─────┴─────┐
    │           │
  Venda    Venda Perdida    Sem Contato / Em branco
    │           │                    │
    └─────┬─────┘                    │
          ↓                         ↓
 [Marco zero atualizado]    [Lead permanece na fila,
 [Novo ciclo recomeça]       horas continuam acumulando]
```

**Quando o consultor marca `Venda` ou `Venda Perdida`:** o sistema registra o horímetro daquele momento como o novo marco zero. O chassis sai da fila e só retorna após acumular as horas do próximo ciclo.

**Quando o consultor deixa em branco ou marca `Sem Contato`:** o lead permanece visível na planilha e as horas continuam acumulando. O aging do lead (tempo sem tratativa) começa a crescer e aparece no Daily Report como alerta para a gestão.

---

## 6. Indicadores de Performance (KPIs) — Daily Report

Estes são os 5 indicadores acompanhados diariamente pela gestão no Daily Report:

| KPI | O que mede | Por que importa |
|---|---|---|
| **Adesão Comercial** | % dos leads da semana com algum feedback registrado | Mede o engajamento e velocidade da equipe em fazer os contatos |
| **Taxa de Conversão Real** | % de leads tratados que resultaram em venda | Mede a eficiência do discurso comercial |
| **Aderência de Propostas** | % de "Vendas" declaradas com proposta real no Protheus | Auditoria sistêmica — garante que o número é verdadeiro |
| **Aging do Lead** | Dias médios de um alerta ativo sem primeiro contato | Alerta quando o timing preventivo está sendo perdido |
| **Pipeline Financeiro** | Soma em R$ das propostas abertas no Protheus vinculadas à campanha | Mede o valor financeiro que a campanha está movimentando |

### Destinatários do Daily Report

O e-mail diário com os KPIs é enviado automaticamente para:

| Nome | E-mail |
|------|--------|
| Pedro Sarnaglia | <pedro.sarnaglia@inovamaquinas.com> |
| Leandro Silva | <leandro.silva@inovamaquinas.com> |
| Marcelo Costa | <marcelo.costa@inovamaquinas.com> |
| Murilo Nunes | <murilo.nunes@inovamaquinas.com> |
| Luciana Borges | <luciana.borges@inovamaquinas.com> |
| Gabriela Rodarte | <gabriela.rodarte@inovamaquinas.com> |
| Roberto Reis | <roberto.reis@inovamaquinas.com> |
| Victor Bernardi *(c/o — Engenharia de Dados)* | <victor.bernardi@inovamaquinas.com> |

---

## 7. Matriz de Responsabilidades

| Papel | Responsável | O que faz na campanha |
|---|---|---|
| **Gerente de Peças** | Roberto Reis | Lidera reunião semanal de revisão de metas (terças-feiras); avalia KPIs consolidados |
| **Gerentes / Coordenadores Regionais** | Pedro Sarnaglia, Leandro Silva, Marcelo Costa, Luciana Borges | Acompanham o Daily Report; gerenciam os consultores de suas respectivas regiões, cobra aging elevado com os consultores |
| **CSA** | Murilo Nunes | Realiza o contato ativo com os clientes da sua carteira; registra o status na planilha |
| **Consultores de Vendas** | A definir — aguardando mapeamento do Murilo | Realizam o contato ativo com os clientes; registram o status na planilha |
| **Engenharia de Dados** | Victor Bernardi | Mantém o motor de cálculo, atualiza a planilha e dispara o Daily Report diariamente |

> **Pendência:** A segmentação de clientes e consultores por CSA (carteira do Murilo) está em definição. Assim que o mapeamento for enviado, a planilha de leads será configurada com o campo "Responsável" preenchido automaticamente por consultor/CSA.

---

## 8. Governança e Segurança dos Dados

- **Soberania de dados:** As colunas de origem do lead (Chassi, Cliente, CNPJ, Modelo, Motivo, Horímetro) são bloqueadas com senha. Consultores não podem editar, copiar ou deletar esses campos.
- **Acesso controlado:** Apenas as colunas de feedback comercial são editáveis pela equipe de vendas.
- **Auditoria mensal:** Cruzamento automático entre a planilha e o Protheus para validar a integridade dos resultados reportados.
- **Snapshot diário:** Antes de cada atualização, o sistema registra um snapshot do estado atual para rastreabilidade histórica.

---

## 9. Fora do Escopo deste Documento

- Implementação técnica do motor ETL (detalhada na Especificação Técnica `2026-05-27-especificacao_leads_csc_pops.md`).
- Regras do motor CEVAP de clientes inativos (projeto paralelo, base TIVAN 590 dias).
- Gestão de metas individuais dos consultores.

---

*Documento elaborado com base na ATA de Reunião e Acordo de Alinhamento de Negócio de 27/05/2026.*
*Para dúvidas ou ajustes, contatar a Engenharia de Dados: <victor.bernardi@inovamaquinas.com>*
