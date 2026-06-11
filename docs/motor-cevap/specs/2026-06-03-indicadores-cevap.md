# Especificação Técnica — Relatório de KPIs & Automação CEVAP

Este documento consolida a especificação física e os requisitos de design técnico para a padronização do report diário de KPIs do **Motor CEVAP**, a ser gerado no formato do **Lead-CSC**, e as rotinas automatizadas de envio de e-mail e compartilhamento no OneDrive.

---

## 1. Objetivo

Implementar a padronização visual e técnica dos relatórios de indicadores do Motor CEVAP, salvando as saídas em caminhos dedicados (`data/config/` e `data/output/`), e configurar os scripts PowerShell para envio diário de e-mail de performance e compartilhamento dinâmico do arquivo Excel do OneDrive com a equipe comercial correspondente.

---

## 2. Requisitos e Critérios de Aceitação (SOW)

### 2.1 Acceptance Criteria (SOW)
*   **AC-1**: Os indicadores de Cobertura e Conversão acumulada devem ser medidos e exibidos no grão de **Clientes** (Grupo Econômico / CNPJ_Cliente) e não de chassis.
*   **AC-2**: Envio diário de e-mails contendo o HTML de performance disparado via SMTP para **Roberto Reis, Gabriela Rodarte e Victor Bernardi**.
*   **AC-3**: Histórico acumulado de faturamento e vendas validadas extraído diretamente do arquivo local `conversao_audit.json` gerado pelo Protheus/Fabric.
*   **AC-4**: Acesso e compartilhamento OneDrive automáticos concedidos para leitura ("read") usando a distribuição em `emails_compartilhamento.json` e a Graph API.

### 2.2 Requisitos Funcionais (FR)
*   **FR-001**: O script `generate_cevap_kpis.py` calculará a Cobertura e a Conversão sobre a lista consolidada de Grupos Econômicos lidos do Excel. **Implements: AC-1**
*   **FR-002**: O orquestrador `scheduler_daily.ps1` carregará credenciais do `.env` e disparará o HTML por SMTP para a gerência/analistas. **Implements: AC-2**
*   **FR-003**: O gerador de KPIs em Python lerá a base de notas fiscais confirmadas de `conversao_audit.json` para computar faturamento realizado. **Implements: AC-3**
*   **FR-004**: O compartilhador `share_onedrive_leads.ps1` lerá o `emails_compartilhamento.json` e executará o Invite em lote na nuvem do OneDrive. **Implements: AC-4**

### 2.3 Requisitos Não-Funcionais (NFR)
*   **NFR-001**: O tempo de execução total do pipeline de KPIs não deve exceder 15 segundos. **Validates: AC-1, AC-3**
*   **NFR-002**: As senhas e chaves SMTP serão armazenadas localmente em arquivo `.env` e lidas em tempo de execução de forma segura. **Validates: AC-2**
*   **NFR-003**: Se os JSONs de auditoria estiverem ausentes, o HTML deve preencher faturamento como R$ 0,00 e conversão como 0% em vez de quebrar a execução. **Validates: AC-3**
*   **NFR-004**: Todo o pipeline Python deve utilizar exclusivamente o virtualenv local (`.venv\Scripts\python.exe`) (Migração UV). **Validates: AC-1, AC-3**
*   **NFR-005**: Gravação e leitura de arquivos textuais obrigatoriamente especificarão `encoding='utf-8'` (Vacina contra Mojibake). **Validates: AC-3**

---

## 3. Matriz de Rastreabilidade

A matriz abaixo estabelece a relação e a cobertura entre os Critérios de Aceitação (AC), Requisitos Funcionais (FR), Cenários de Testes (T) e Requisitos Não-Funcionais (NFR):

| AC | Requisito Funcional (FR) | Requisito Não-Funcional (NFR) | Cenário de Teste (T) | Status |
|---|---|---|---|---|
| **AC-1** | `FR-001` | `NFR-001`, `NFR-004` | `T-002` | Habilitado |
| **AC-2** | `FR-002` | `NFR-002` | `T-003` | Habilitado |
| **AC-3** | `FR-003` | `NFR-001`, `NFR-003`, `NFR-005` | `T-002` | Habilitado |
| **AC-4** | `FR-004` | - | `T-001`, `T-004` | Habilitado |

---

## 4. Estrutura Proposta & Arquitetura

### 4.1 Mapeamento de Arquivos e Pastas

| Caminho do Arquivo | Função |
|---|---|
| [data/config/emails_compartilhamento.json](file:///C:/Projetos/Inova/projects/motor-cevap/data/config/emails_compartilhamento.json) | Lista de e-mails para compartilhamento em massa do OneDrive. |
| [data/output/daily_report_kpis.html](file:///C:/Projetos/Inova/projects/motor-cevap/data/output/daily_report_kpis.html) | Relatório final diário em formato HTML corporativo responsivo. |
| [scripts/generate_cevap_kpis.py](file:///C:/Projetos/Inova/projects/motor-cevap/scripts/generate_cevap_kpis.py) | Script de processamento e montagem do template HTML. |
| [scripts/scheduler_daily.ps1](file:///C:/Projetos/Inova/projects/motor-cevap/scripts/scheduler_daily.ps1) | PowerShell de agendamento, consolidação de dados e envio SMTP. |
| [scripts/share_onedrive_leads.ps1](file:///C:/Projetos/Inova/projects/motor-cevap/scripts/share_onedrive_leads.ps1) | PowerShell de sincronização de permissões com a Microsoft Graph API. |

### 4.2 Fluxo de Dados de Execução

```
[Execução do scheduler_daily.ps1]
               │
               ▼
[consolidate_cevap.py] ─────────→ Atualiza planilha CEVAP_ATIVACAO.xlsx
               │
               ▼
[cross_reference_protheus.py] ──→ Valida notas no Protheus/Fabric e atualiza conversao_audit.json
               │
               ▼
[generate_cevap_kpis.py] ───────→ Lê dados locais e gera o HTML daily_report_kpis.html
               │
               ▼
[scheduler_daily.ps1] ──────────→ Envia HTML por e-mail via SMTP (Office365) para os gestores
```

---

## 5. Plano de Validação e Cenários de Testes

*   **T-001**: Validar que a estrutura física de diretórios e o parse do arquivo `emails_compartilhamento.json` estão operantes. **FR: FR-004**
*   **T-002**: Executar e atestar que a geração do report HTML `daily_report_kpis.html` em `data/output/` ocorre sem erros e respeita os KPIs no grão de clientes. **FR: FR-001, FR-003**
*   **T-003**: Executar a auditoria de sintaxe do script de agendamento `scheduler_daily.ps1` no PowerShell do Windows. **FR: FR-002**
*   **T-004**: Executar a auditoria de sintaxe do compartilhador OneDrive `share_onedrive_leads.ps1`. **FR: FR-004**

---

## 6. Log de Decisões (Brainstorming Session)

*   **Decisão 1: Grão do Report**: KPIs de performance mostrados em percentuais de **Clientes** (Grupo Econômico/CNPJ_Cliente) e não por Chassis.
    *   *Razão*: Adequação às regras do negócio do CEVAP de ativação focada no cliente consolidado.
*   **Decisão 2: Destinatários**: Report diário enviado para Roberto Reis, Gabriela Rodarte e Victor Bernardi.
    *   *Razão*: Alinhamento com a gestão comercial do pós-vendas e equipe técnica.
*   **Decisão 3: Histórico de Vendas**: Alimentado de forma dinâmica pelas saídas geradas por `cross_reference_protheus.py` (via `conversao_audit.json`) em vez de persistir um histórico incremental paralelo.
    *   *Razão*: A base acumulada do OneDrive e o cruzamento Protheus são auto-corretivos, reduzindo a complexidade de manutenção técnica.
