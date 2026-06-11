# 🧠 Especificação Técnica: Campanha de Leads CSC & Pós-Vendas (Inova Máquinas)

> **Identidade do Documento:** `./docs/specs/2026-05-27-especificacao_leads_csc_pops.md`  
> **Data:** 27/05/2026  
> **Status:** Aprovado em Brainstorming  
> **Autores:** Victor Bernardi (Analista), Antigravity (Engenheiro de Software)

---

## 🎯 1. Objetivo do Projeto

Esta especificação define o desenvolvimento do pipeline de dados preventivo de pós-vendas focado no controle comercial de **Ferramentas de Penetração de Solo (FPS)** e **Material Rodante** da Inova Máquinas. O motor calcula alertas de desgaste das máquinas em operação a partir dos horímetros acumulados, publica semanalmente uma planilha comercial blindada com senha no OneDrive (Excel Online) e realiza uma auditoria diária/mensal ("Ponte da Verdade") com os orçamentos reais abertos no ERP Protheus através do Microsoft Fabric.

---

## ⚙️ 2. Requisitos de Negócio & Funcionais

### RF-01: Cálculo de Alertas FPS (Ferramentas de Penetração de Solo)

* **Gatilho:** Alerta preventivo gerado a cada **200 horas adicionais de operação** a partir do horímetro base (ponto zero ou último tratamento).
* **Escopo:** Aplicado de forma global para **todas as máquinas da base ativa**, independente da família ou modelo do equipamento, devido ao desgaste uniforme do material de sacrifício.

### RF-02: Cálculo de Alertas de Material Rodante

* **Gatilho:** Alerta preventivo gerado em intervalos diferenciados baseados na severidade de deslocamento do ativo:
  1. **Tratores de Esteira (Famílias 700J, 750J, 850J, 1050K):** Alerta a cada **1.500 horas adicionais de operação** a partir do horímetro base.
  2. **Escavadeiras (Famílias 130G, 130P, 160G/P, 180G, 200G/P, 210G/P, 350ZX, 350G):** Alerta a cada **3.000 horas adicionais de operação** a partir do horímetro base.

### RF-03: Marco Zero Inicial & Gatilho de Reentrada

* **Ponto Zero Inicial:** No primeiro processamento da máquina (chassis), o horímetro atual no arquivo de ativos é registrado como o `Horimetro_Base`.
* **Fluxo de Tratativa Comercial:**
  * O consultor comercial preenche a coluna `Retorno do Contato` com uma das opções: `Venda`, `Venda Perdida` ou `Sem Contato`.
  * Quando o lead é marcado como **"Tratado" (`Venda` ou `Venda Perdida`)**, o script de atualização semanal zera o ciclo, atualizando o `Horimetro_Base` do chassis para o horímetro daquele momento de tratamento. Um novo alerta só será gerado após acumular +200h (FPS) ou +1500h/+3000h (Rodante).
  * Se o status for `Sem Contato` ou nulo, o lead permanece na fila e as horas continuam acumulando a partir do horímetro base antigo.

### RF-04: Planilha de Leads Online Semanal (OneDrive)

* **Granularidade:** Uma linha por ativo (chassis), permitindo múltiplos alertas simultâneos para um mesmo cliente.
* **Segurança e Travas de Células (Soberania de Dados):**
  * As colunas estruturais do lead (Chassi, Nome do Cliente, CNPJ, Modelo da Máquina, Motivo do Alerta e Horímetro Atual) serão **bloqueadas com senha para edição e cópia**. Isso evita vazamento acidental de dados da base corporativa e deleções.
  * Os consultores comerciais e CSAs terão permissão de edição **exclusivamente** nas colunas de feedback comercial:
    1. **Retorno do Contato (Status Comercial):** Campo obrigatório com opções restritas via lista suspensa (`Venda`, `Venda Perdida`, `Sem Contato`).
    2. **Observações:** Campo de texto livre para detalhamento do histórico da tratativa.

### RF-05: Report Executivo Diário ("Daily Report") via E-mail

* Envio diário automático para o Roberto (Gerente de Pós-Venda) e Gabriela (Supervisora) contendo os principais indicadores de engajamento comercial da campanha.
* **KPIs Definidos:**
  1. **Adesão Comercial (Contato Ativo):** % de leads gerados na semana que receberam tratamento comercial (leads tratados / total de leads).
  2. **Taxa de Conversão Real:** % de leads tratados que foram fechados com sucesso (status "Venda" / total de leads tratados).
  3. **Aderência de Propostas (Ponte da Verdade):** % de vendas alegadas na planilha que de fato possuem proposta gerada no ERP Protheus.
  4. **Aging do Lead:** Média de dias que os alertas ativos demoram para receber a primeira tratativa comercial.
  5. **Potencial de Receita em Negociação:** Valor somado em R$ dos orçamentos abertos no Protheus vinculados às máquinas em alerta.

### RF-06: Ponte da Verdade (Auditoria com Protheus/Fabric)

* **Objetivo:** Cruzar mensalmente/diariamente os alertas tratados com o ERP Protheus para verificar se as propostas financeiras foram de fato emitidas.
* **Mapeamento Sistêmico (Fabric - Lakehouse `LH_Consumo`):**
  * Tabela **`VS1010`** (Orçamentos de Oficina/Pós-Vendas): O campo `VS1_NUMORC` contém o número do orçamento e `VS1_CHAINT` contém o Chassi Interno do Protheus.
  * Tabela **`VV1010`** (Cadastro de Equipamentos/Máquinas): O campo `VV1_CHAINT` mapeia o Chassi Interno para o Chassi completo de 17 caracteres no campo `VV1_CHASSI`.
  * **Lógica de Junção:**

    ```sql
    SELECT 
        vs.VS1_NUMORC AS Num_Orcamento,
        vv.VV1_CHASSI AS Chassi_Completo,
        vs.VS1_DATORC AS Data_Orcamento,
        vs.VS1_CLIFAT AS Cliente_Faturamento
    FROM dbo.VS1010 vs
    INNER JOIN dbo.VV1010 vv ON vs.VS1_CHAINT = vv.VV1_CHAINT
    WHERE vs.D_E_L_E_T_ <> '*' AND vv.D_E_L_E_T_ <> '*'
    ```

  * O resultado dessa junção será cruzado com o `Serial Number` do alerta e o `Num Orc` informado na planilha/orçamentos abertos para consolidar o indicador de auditoria.

---

## 🛠️ 3. Requisitos Não-Funcionais (Qualidade & Governança)

* **RNF-01: Soberania do Conector Fabric (Regra 1):** O acesso a dados do ERP Protheus é estritamente realizado pela classe `ConexaoFabric` mapeada em `C:\Users\victor.bernardi\Documents\Fabric_Database_Connector\fabric_db.py`, utilizando JVM/JDBC.
* **RNF-02: Preservação de Rede e Cache Estrito (Regra 2):** Queries executadas durante desenvolvimento e teste devem utilizar os parâmetros `use_cache=True` e `save_cache=True` salvando arquivos `.parquet` temporários em um diretório `/cache` dedicado, reduzindo chamadas repetidas ao Fabric.
* **RNF-03: Robustez de I/O em Excel:** A escrita semanal da planilha no OneDrive deve usar a biblioteca `openpyxl` para aplicar bloqueios de células por senha, validação de dados de dropdown e regras de estilo corporativas.
* **RNF-04: Higiene de Dados e Fail-Fast (Regra 5):** Implementação de validações rigorosas (ex: `assert not df.empty`, checagem de CNPJ nulo, validação de chassi com 17 caracteres) antes de exportar dados e disparar o e-mail, forçando interrupção imediata (`sys.exit(1)`) em caso de anomalias estruturais.
* **RNF-05: Orquestração Polyglot (Regra 4):** A extração e regras de negócio rodam em Python; a automação Windows de agendamento de tarefas e envio de e-mails via SMTP corporativo é delegada para PowerShell `.ps1` isolado.

---

## 📐 4. Arquitetura do Sistema

O motor segue o padrão corporativo Inova de 4 camadas:

```
C:\Projetos\Inova\projects\lead-csc-pops\
├── extract.py      # I/O Puro: Carrega dados do Fabric (VS1010/VV1010) e Excel de ativos/orçamentos
├── transform.py    # Lógica Pura: Sem rede/disco. Calcula gatilhos de horímetro, reentradas e cruzamentos
├── load.py         # Persistência: Escreve a planilha protegida na pasta do OneDrive e gera HTML do report
├── run.py          # Orquestrador Geral: Instancia conexões, lê config.py e executa o fluxo
├── docs/
│   └── specs/      # Especificações técnicas e de negócio (Este documento)
└── tests/          # Testes unitários focados na camada de transformação
```

---

## 🧪 5. Plano de Validação & Testes

A conformidade do projeto será comprovada por meio do protocolo Stout de TDD:

1. **Testes de Lógica de Negócio (FPS & Rodante):**
   * Validar se uma máquina com +210h em relação ao horímetro base dispara alerta de FPS.
   * Validar se um trator com +1.600h dispara alerta de rodante e se uma escavadeira com +2.900h não dispara.
   * Validar o gatilho de reentrada (se após registrar status "Venda", o horímetro base é corretamente atualizado).
2. **Testes de Schema e Segurança:**
   * Garantir que as colunas corretas estejam protegidas com senha no arquivo `.xlsx`.
   * Garantir que o dropdown comercial contenha apenas as três opções válidas.
3. **Dry-Run do E-mail e Report:**
   * Executar uma execução piloto salvando o HTML do report diário localmente em `/temp` para validação visual dos KPIs.

---

## 🔗 6. Matriz de Rastreabilidade Técnica (AC ➔ FR ➔ Test)

| ID Negócio (SOW / ATA) | ID Requisito Funcional (Spec) | Descrição do Requisito | Cenário de Teste Associado | Status |
| :--- | :--- | :--- | :--- | :--- |
| **AC-1** (Alerta FPS 200h) | **FR-001** (RF-01) | Régua de alerta FPS global a cada 200 horas adicionais. | `T-001` (Teste de cálculo de alerta FPS a cada +200h) | Coberto |
| **AC-2** (Alerta Rodante Tratores) | **FR-002** (RF-02.1) | Régua de alerta de rodante a cada 1.500 horas para tratores de esteira. | `T-002` (Teste de alerta rodante tratores a cada +1500h) | Coberto |
| **AC-3** (Alerta Rodante Escavadeiras) | **FR-003** (RF-02.2) | Régua de alerta de rodante a cada 3.000 horas para escavadeiras. | `T-003` (Teste de alerta rodante escavadeiras a cada +3000h) | Coberto |
| **AC-4** (Gatilho de Reentrada) | **FR-004** (RF-03) | Atualização de Horímetro Base após tratamento comercial ("Venda"/"Venda Perdida"). | `T-004` (Teste de reentrada e atualização do horímetro base) | Coberto |
| **AC-5** (Planilha Online & Travas) | **FR-005** (RF-04) | Atualização semanal no OneDrive, travas com senha e dropdown comercial. | `T-005` (Teste de integridade e restrições da planilha Excel) | Coberto |
| **AC-6** (KPIs & Daily Report E-mail) | **FR-006** (RF-05) | Envio de e-mail diário com 5 KPIs executivos (Roberto e Gabriela). | `T-006` (Teste de geração e validação de HTML/SMTP de KPIs) | Coberto |
| **AC-7** (Auditoria Protheus Fabric) | **FR-007** (RF-06) | Cruzamento automatizado de chassis e orçamentos do Protheus via Fabric. | `T-007` (Teste de join de auditoria VS1010 e VV1010 no Fabric) | Coberto |

---
*Ata e Transcrição da Reunião de 27/05/2026 consolidadas em regras de engenharia da Inova Máquinas.*
