# Motor de Ativação de Clientes Inativos — CEVAP

**Data:** 02/06/2026 | **Versão:** 1.0  
**Gerente:** Roberto Reis
**Elaborado por:** Victor Bernardi

---

## 1. Resumo Executivo

O Motor CEVAP transforma clientes sem compra há mais de 90 dias em oportunidades consultivas estruturadas, entregando semanalmente ao time comercial uma planilha priorizada com todos os dados necessários para o contato: identidade, potencial, equipamentos e status (Seedz/InovaPay). Cada cliente da fila recebe colunas de controle onde os consultores registram tentativas de contato e resultados, gerando rastreabilidade total do follow-up. O sucesso é medido pela taxa de conversão , clientes que voltaram a comprar após o acionamento.

---

## 2. Objetivos de Negócio

O CEVAP existe para dar previsibilidade e rastreabilidade ao trabalho de reativação de clientes inativos. O indicador primário é a **taxa de conversão** (clientes acionados que voltaram a comprar), mensurada semanalmente. Os objetivos específicos são:

- **Visibilidade:** Garantir que todo cliente inativo seja identificado automaticamente, sem depender da memória ou percepção individual do consultor.
- **Priorização:** Ordenar a fila de acionamento por potencial de receita, direcionando o esforço comercial para onde há maior retorno esperado.
- **Rastreabilidade:** Registrar data e resultado de cada tentativa de contato, permitindo auditar o trabalho realizado e medir a efetividade da abordagem.
- **Integridade:** Preservar o histórico de contatos já realizados a cada nova publicação, sem sobrescrever o trabalho preenchido pelos consultores.

---

## 3. Problema a Resolver

### Situação Atual

Hoje, os consultores de peças não possuem uma lista sistemática de quais clientes deixaram de comprar. O contato acontece de forma reativa, quando o cliente aparece no balcão ou quando o consultor se lembra de ligar. Não há como saber:

- Quais grupos econômicos estão esfriando (nenhuma filial comprando há mais de 90 dias).
- Qual o potencial de receita que está em risco com cada cliente inativo.
- Se o consultor realmente entrou em contato e qual foi o resultado.

### Impacto no Negócio

- **Perda silenciosa de receita:** Clientes migram para concorrentes sem que a Inova perceba a tempo de reagir.
- **Esforço comercial disperso:** Sem priorização por potencial, consultores gastam tempo em clientes de baixo retorno enquanto clientes A1 (acima de R$ 1 milhão/ano) ficam sem abordagem.
- **Impossibilidade de auditar:** A gestão não consegue medir se o trabalho está sendo feito nem qual a taxa de sucesso das abordagens.

---

## 4. Solução Proposta

### 4.1 Como Funciona para o Negócio

1. **Pipeline diário de dados:** O motor consome diariamente dados de faturamento, identidade de clientes, potencial de compra, equipamentos, programa de fidelidade (Seedz) e crédito (InovaPay). Cruza essas informações e aplica a regra de inatividade.
2. **Publicação semanal da planilha:** Toda semana, a planilha CEVAP é atualizada no OneDrive com a fila completa de clientes inativos, ordenada por classificação (A1 a C1).
3. **Consultores registram o contato:** As colunas `Data_Tentativa_1`, `Status_Contato_1`, `Data_Tentativa_2`, `Status_Contato_2` e `Observacao` são preenchidas pelos consultores Filipe Paiva e Katia Almeida.
4. **Preservação do histórico:** A cada nova publicação, o motor lê a planilha anterior do OneDrive e preserva as colunas de controle já preenchidas, nenhum dado de contato é perdido.
5. **Aferição semanal:** A taxa de conversão é mensurada comparando os clientes acionados com os que voltaram a comprar (via dados de faturamento mais recentes).

### 4.2 Quando um Cliente é CEVAP

Um cliente entra na fila CEVAP quando seu **grupo econômico** está há **90 dias ou mais sem nenhuma compra em nenhuma filial**. Ou seja:

- **Entra no CEVAP:** Grupo econômico sem compra ≥ 90 dias em todas as filiais.
- **Sai do CEVAP:** Qualquer filial do grupo volta a comprar → o grupo inteiro sai da fila automaticamente na próxima publicação.
- **Exclusão automática:** Clientes com orçamento aberto há menos de 90 dias são removidos da fila, pois indica que já existe negociação em andamento.

### 4.3 Critérios de Segmentação

Os clientes são classificados de A1 a C1 pelo **Motor de Segmentação** (motor que consolida faturamento, potencial e share of wallet para ranquear cada grupo econômico). O CEVAP apenas consome essa classificação pronta, não recalcula. A ordem da planilha é crescente por classificação (A1 primeiro), orientando os consultores a priorizar os clientes de maior potencial.

| Classificação | Significado |
|---|---|
| A1 | Grupo de altíssimo potencial — prioridade máxima de contato |
| A2 | Grupo de alto potencial |
| B1 | Grupo de potencial médio-alto |
| B2 | Grupo de potencial médio |
| C1 | Grupo de potencial básico |

**Importante:** Todos os clientes inativos entram na planilha, independentemente da classificação. A priorização é uma orientação de trabalho, não há bloqueio ou filtro que impeça o consultor de contatar qualquer cliente da fila.

### 4.4 De Onde Vêm os Dados (Linhagem Completa)

Cada informação da planilha CEVAP é fruto de uma cadeia de processamento que começa nos sistemas de origem da Inova. Nenhum dado é digitado manualmente.

#### Identidade do Cliente (Nome, CNPJ, E-mail, Cidade, Mesorregião)

**Fonte original:** Tabelas do ERP Protheus (cadastro de clientes)

O **Motor de Identidade** consolida os ~126 mil registros brutos do cadastro em ~4 mil grupos econômicos reais, eliminando duplicatas (filiais de uma mesma empresa, variações de grafia como "ABC Ltda" e "ABC Construções S.A."). A classificação por grupo econômico é o que permite tratar todo o grupo como um único cliente.

Cidade e Estado são obtidos diretamente da tabela `SA1010` do Fabric (data warehouse da Inova), enriquecidos com a Mesorregião via mapeamento geográfico (Triângulo Mineiro, Zona da Mata, etc.).

#### Recência (DT_Ultima_Compra, Dias_Inativo)

**Fonte original:** Notas fiscais do ERP Protheus

O **Motor de Faturamento** isola, dentre todas as vendas do ERP, apenas as receitas de peças (exclui máquinas novas, serviços e devoluções). O resultado é um extrato em vendas líquidas de peças, agrupado por grupo econômico.

A data da última compra e o valor acumulado em 12 meses vêm desse motor. Os dias de inatividade são calculados subtraindo a data da última compra da data atual.

#### Potencial e Classificação (Potencial_Grupo, Classificacao, SOW)

**Fonte original:** Frota de máquinas John Deere (PoPS) + Índice Sobratema

O **Motor de Potencial** calcula, para cada máquina, quanto custa mantê-la operando em peças por ano (usando o índice Sobratema, padrão nacional da Associação Brasileira de Tecnologia para Construção e Mineração). A frota vem do PoPS (portal John Deere), atualizada diariamente.

O **Motor de Estratégia** cruza o que o cliente já comprou (faturamento) com o que ele deveria comprar (potencial), gerando o Share of Wallet (SOW), a fatia de mercado que a Inova tem naquele cliente. O **Motor de Segmentação** consolida tudo e gera a classificação A1-C1.

#### Equipamentos

**Fonte original:** PoPS (portal John Deere) + ERP Protheus

Lista de máquinas da frota de cada cliente, extraída do PoPS e vinculada ao proprietário correto pelo mesmo Motor de Identidade. O CEVAP herda essa informação pronta.

#### Seedz (Pontos_Seedz)

**Fonte original:** Planilha de dados Seedz (programa de fidelidade Inova)

Saldo de pontos do programa de fidelidade, consolidado por grupo econômico.

#### InovaPay (InovaPay_Limite_Dis)

**Fonte original:** Relatório de clientes InovaPay (crédito interno)

Limite de compra disponível no crediário próprio da Inova.

#### Orçamentos (N_Orcamento_12m)

**Fonte original:** Metas Peças (base de orçamentos)

Quantidade de orçamentos emitidos nos últimos 12 meses. Além de informar o consultor, esta informação é usada para excluir da fila clientes com orçamento aberto há menos de 90 dias (já estão em negociação).

### 4.5 Fluxo Resumido da Linha de Montagem

```
Protheus/Fabric (ERP) ──→ Motor de Identidade ──→ Grupos Econômicos Consolidados
Protheus/Fabric (ERP) ──→ Motor de Faturamento ──→ Vendas de Peças por Grupo
PoPS (John Deere) ──────→ Motor de Potencial ────→ Potencial de Compra por Grupo
         │                         │
         └──────────┬──────────────┘
                    ▼
          Motor de Estratégia ──→ SOW (Share of Wallet)
                    │
                    ▼
          Motor de Segmentação ──→ Classificação A1-C1
                    │
                    ▼
          ┌─── CEVAP ───┐
          │  Aplica regra de inatividade (≥90 dias)
          │  Aplica exclusão de orçamentos recentes
          │  Enriquece com Seedz, InovaPay, Equipamentos
          │  Consolida Cidade/Mesorregião via Fabric
          │  Preserva controle comercial do OneDrive
          └──────────────┘
                    │
                    ▼
          Planilha de Ativação → OneDrive
```

---

## 5. Guia de Funcionamento

### 5.1 O Que é um Cliente CEVAP

Um cliente CEVAP é um **grupo econômico inteiro**, não uma filial isolada, que está há 90 dias ou mais sem registrar nenhuma compra de peças em nenhuma de suas filiais. O conceito de grupo econômico é fundamental: empresas com múltiplos CNPJs (filiais) que pertencem ao mesmo grupo são tratadas como um único cliente.

Exemplo prático: se a "Construtora ABC" tem filial em Belo Horizonte (CNPJ 12.345.678/0001-00) e filial em Uberlândia (CNPJ 12.345.678/0002-00), e a filial de Uberlândia comprou há 45 dias mas a de Belo Horizonte não compra há 120 dias, o **grupo inteiro está ativo**, a compra de uma filial zera a inatividade de todas.

### 5.2 Como o Motor Decide

1. **Recebe a base consolidada de clientes** (identidade + faturamento + potencial + classificação) processada pelos motores anteriores.
2. **Calcula a inatividade** subtraindo a data da última compra do grupo da data atual.
3. **Filtra apenas grupos com ≥ 90 dias de inatividade.**
4. **Remove grupos com orçamento aberto há < 90 dias** (já em negociação).
5. **Enriquece** com telefones (Seedz + ERP), limite InovaPay, equipamentos e localização.
6. **Consolida por grupo econômico**, selecionando a filial de maior faturamento como referência.
7. **Preserva o controle comercial** preenchido pelos consultores na planilha anterior.
8. **Publica** no OneDrive e no diretório local `data/`.

### 5.3 Ciclo de Vida de um Lead CEVAP

```
[Cliente entra na planilha]
         │
         ▼
[Consultor tenta Contato 1] ──→ Registra data e status
         │
    ┌────┴────┐
    ▼         ▼
[Contato    [Sem Retorno]
 Realizado]      │
    │            ▼
    │     [Consultor tenta Contato 2]
    │            │
    │       ┌────┴────┐
    │       ▼         ▼
    │   [Contato    [Sem Retorno]
    │    Realizado]      │
    │       │            │
    └───────┴────────────┘
            │
            ▼
   ┌─── Resultado ───┐
   │                  │
   ▼                  ▼
[Voltou a         [Não converteu]
 comprar]              │
   │                   │
   ▼                   ▼
[Sai do CEVAP]    [Permanece na fila
                    para próxima semana]
```

Quando o cliente volta a comprar em qualquer filial, o grupo inteiro sai automaticamente do CEVAP na publicação seguinte. Se não houve conversão, o cliente permanece na fila e os consultores podem registrar novas tentativas de contato.

---

## 6. Indicadores de Performance (KPIs)

O resultado do CEVAP é avaliado semanalmente através de três indicadores:

| Indicador | O Que Mede |
|---|---|
| **Taxa de Conversão** | Clientes acionados que voltaram a comprar / total de clientes na fila. É o indicador primário de sucesso. |
| **Cobertura** | Percentual da base inativa que recebeu ao menos uma tentativa de contato. Mede o alcance do trabalho comercial. |
| **Aging** | Tempo médio entre a publicação do lead e o primeiro contato registrado. Mede a agilidade da equipe. |

---

## 7. Matriz de Responsabilidades

| Responsável | Papel |
|---|---|
| **Victor Bernardi** | Manutenção do motor CEVAP, pipeline de dados, atualização do PoPS, publicação semanal da planilha |
| **Roberto Reis** | Gestão da equipe comercial, cobrança de follow-up, análise dos indicadores |
| **Filipe Paiva** | Contato com clientes, preenchimento das colunas de controle na planilha |
| **Katia Almeida** | Contato com clientes, preenchimento das colunas de controle na planilha |
| **Protheus / BI** | Disponibilidade e integridade dos dados fonte (ERP e data warehouse) |

---

## 8. Governança e Segurança dos Dados

### 8.1 Preservação de Controle Comercial

A cada nova publicação, o motor lê a planilha CEVAP existente no OneDrive e preserva as 5 colunas de controle preenchidas pelos consultores (`Data_Tentativa_1`, `Status_Contato_1`, `Data_Tentativa_2`, `Status_Contato_2`, `Observacao`). O merge é feito por CNPJ do cliente, novos clientes entram com valores padrão (campos de data vazios, status "Pendente"). Nenhum preenchimento manual é sobrescrito.

### 8.2 Versionamento e Backup

- **Versionamento local:** Cada execução gera um arquivo com timestamp no diretório `data/` (`CEVAP_ATIVACAO_YYYYMMDD_HHMM.xlsx`), mantendo histórico completo de todas as publicações.
- **Backup do OneDrive:** Antes de sobrescrever o arquivo do OneDrive, o motor cria uma cópia de segurança com timestamp (`CEVAP_ATIVACAO_backup_YYYYMMDD_HHMM.xlsx`).

### 8.3 Validação de Recência das Fontes

Antes de cada execução, o motor verifica se todas as fontes de dados estão atualizadas (via arquivo de controle `recency_status.md`). Se alguma fonte estiver desatualizada ou ausente, um alerta é emitido, o motor continua funcionando, mas a equipe é notificada. O mesmo relatório é atualizado ao final da execução, registrando a data/hora da última publicação.

### 8.4 Rastreabilidade de Consistência

Ao final do merge com o OneDrive, o motor audita e reporta:

- Quantos preenchimentos de controle foram preservados da planilha anterior.
- Se há CNPJs que desapareceram entre uma publicação e outra (possível "solda de identidade", quando o motor de identidade reagrupa empresas de forma diferente).
