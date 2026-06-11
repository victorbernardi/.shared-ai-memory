# User Stories — Campanha de Leads Preventivos de Pós-Vendas

**Derivado de:** BRD-20260528-leads-csc-pops.md

> **Data:** 28/05/2026 | **Versão:** 1.0

---

## US-01 — Geração Automática de Alertas de FPS

**Como** Consultor de Vendas,
**eu quero** receber automaticamente uma lista de máquinas que atingiram 200 horas adicionais de operação,
**para que** eu possa abordar o cliente no momento certo, antes que a peça quebre.

### Critérios de Aceitação

- **Dado que** um equipamento da base ativa acumulou +200h desde o último alerta ou marco zero,
- **Quando** o sistema rodar a atualização semanal (toda segunda-feira),
- **Então** uma linha com os dados daquele chassis deve aparecer na planilha do OneDrive com `Motivo = Alerta FPS`.

**INVEST:** I ✅ N ✅ V ✅ E ✅ S ✅ T ✅

---

## US-02 — Geração Automática de Alertas de Rodante (Tratores de Esteira)

**Como** Consultor de Vendas,
**eu quero** ser alertado quando um Trator de Esteira (famílias 700J, 750J, 850J, 1050K) atingir 1.500 horas adicionais de operação,
**para que** eu possa oferecer o kit de material rodante antes de uma parada não planejada.

### Critérios de Aceitação

- **Dado que** um Trator de Esteira acumulou +1.500h desde o último marco,
- **Quando** o sistema rodar a atualização semanal,
- **Então** o chassis deve aparecer na planilha com `Motivo = Alerta Rodante`.

**INVEST:** I ✅ N ✅ V ✅ E ✅ S ✅ T ✅

---

## US-03 — Geração Automática de Alertas de Rodante (Escavadeiras)

**Como** Consultor de Vendas,
**eu quero** ser alertado quando uma Escavadeira (130G, 160G, 200G, 210G, 350G…) atingir 3.000 horas adicionais de operação,
**para que** eu possa contatar o cliente no ciclo correto de desgaste desse tipo de equipamento.

### Critérios de Aceitação

- **Dado que** uma Escavadeira acumulou +3.000h desde o último marco,
- **Quando** o sistema rodar a atualização semanal,
- **Então** o chassis deve aparecer na planilha com `Motivo = Alerta Rodante`.

**INVEST:** I ✅ N ✅ V ✅ E ✅ S ✅ T ✅

---

## US-04 — Registro de Feedback Comercial na Planilha

**Como** Consultor de Vendas / CSA,
**eu quero** registrar o resultado do meu contato com o cliente diretamente na planilha do OneDrive,
**para que** a gestão tenha visibilidade do andamento de cada lead sem precisar me ligar.

### Critérios de Aceitação

- **Dado que** acesso a planilha no OneDrive,
- **Quando** localizo o chassis do cliente,
- **Então** consigo selecionar `Venda`, `Venda Perdida` ou `Sem Contato` no campo de status e salvar uma observação em texto livre — sem conseguir editar os dados de origem do lead.

**INVEST:** I ✅ N ✅ V ✅ E ✅ S ✅ T ✅

---

## US-05 — Reinício do Ciclo de Alerta após Tratativa

**Como** Sistema,
**eu quero** zerar o horímetro de referência de um chassis quando seu lead for marcado como `Venda` ou `Venda Perdida`,
**para que** o próximo alerta seja gerado somente após o novo ciclo de desgaste ser acumulado.

### Critérios de Aceitação

- **Dado que** um lead foi marcado como `Venda` ou `Venda Perdida`,
- **Quando** o sistema processar a atualização seguinte,
- **Então** o horímetro de referência daquele chassis é atualizado para o horímetro atual, e ele só reaparece na lista após acumular +200h (FPS) ou +1.500h/+3.000h (Rodante).

**INVEST:** I ✅ N ✅ V ✅ E ✅ S ✅ T ✅

---

## US-06 — Recebimento do Daily Report com KPIs

**Como** Gabriela (Supervisora Comercial),
**eu quero** receber todos os dias por e-mail um painel com os 5 KPIs da campanha,
**para que** eu possa identificar rapidamente quais consultores estão com leads sem tratativa e cobrar antes que o timing se perca.

### Critérios de Aceitação

- **Dado que** é um dia útil,
- **Quando** o sistema rodar a rotina diária,
- **Então** eu recebo um e-mail com: Adesão Comercial, Taxa de Conversão Real, Aderência de Propostas, Aging médio e Pipeline Financeiro em R$.

**INVEST:** I ✅ N ✅ V ✅ E ✅ S ✅ T ✅

---

## US-07 — Auditoria Automática de Propostas no Protheus

**Como** Roberto (Gerente de Pós-Venda),
**eu quero** que o sistema valide automaticamente se os leads marcados como "Venda" possuem uma proposta real gerada no Protheus,
**para que** eu tenha confiança de que os números de conversão são verdadeiros e não autodeclarados.

### Critérios de Aceitação

- **Dado que** um lead está marcado como `Venda` na planilha,
- **Quando** o sistema rodar a auditoria (cruzamento com tabela VSO do Protheus),
- **Então** o KPI "Aderência de Propostas" reflete apenas os leads com proposta física confirmada no ERP.

**INVEST:** I ✅ N ✅ V ✅ E ✅ S ✅ T ✅

---

## US-08 — Visão de Pipeline Financeiro

**Como** Roberto (Gerente de Pós-Venda),
**eu quero** ver no Daily Report a soma em R$ de todas as propostas abertas no Protheus vinculadas aos chassis ativos na campanha,
**para que** eu saiba o valor financeiro que esta campanha está gerando para o pós-vendas.

### Critérios de Aceitação

- **Dado que** existem propostas abertas no Protheus com chassis presentes na campanha,
- **Quando** o Daily Report for gerado,
- **Então** o KPI "Pipeline Financeiro" exibe a soma correta em R$ dessas propostas.

**INVEST:** I ✅ N ✅ V ✅ E ✅ S ✅ T ✅

---

## Backlog Priorizado

| ID | História | Persona | Prioridade |
|----|----------|---------|------------|
| US-01 | Alertas FPS | Consultor | Alta |
| US-02 | Alertas Rodante — Tratores | Consultor | Alta |
| US-03 | Alertas Rodante — Escavadeiras | Consultor | Alta |
| US-04 | Registro de feedback na planilha | Consultor / CSA | Alta |
| US-05 | Reinício de ciclo após tratativa | Sistema | Alta |
| US-06 | Daily Report por e-mail | Gabriela | Média |
| US-07 | Auditoria Protheus | Roberto | Média |
| US-08 | Pipeline Financeiro | Roberto | Média |

---

*Derivado do BRD-20260528-leads-csc-pops.md | Próxima fase: spec-validation*
