# Plano de Execução — Indicadores & Automação CEVAP (Baseado no Lead-CSC)

Este documento descreve o plano detalhado de estratégia técnica para a criação e automação do report diário de KPIs em HTML e o compartilhamento automático no OneDrive para o **Motor CEVAP**, espelhando o padrão homologado no **Lead-CSC**.

---

## 📅 Contexto e Objetivos

O Motor CEVAP atualmente gera o relatório `data/dashboard_cevap_kpis.html` contendo indicadores importantes de ativação de clientes inativos. Contudo, precisamos:
1. Padronizar a entrega visual e a estrutura com o que foi implementado no projeto [lead-csc-pops](file:///C:/Projetos/Inova/projects/lead-csc-pops), consolidando o report HTML final na pasta `data/output/daily_report_kpis.html`.
2. Criar a configuração de e-mails de compartilhamento para o CEVAP.
3. Disponibilizar os scripts de automação de envio de e-mails diários (SMTP) e compartilhamento automático no OneDrive para a equipe do comercial.

---

## 🛠️ Etapas do Plano de Implementação

### Passo 1: Estrutura Física de Diretórios
* Criar a pasta [data/config/](file:///C:/Projetos/Inova/projects/motor-cevap/data/config) e [data/output/](file:///C:/Projetos/Inova/projects/motor-cevap/data/output).
* Os outputs gerados passarão a residir na pasta `data/output/` para manter a paridade com a arquitetura Stout Camada 3/4.

### Passo 2: Configuração de E-mails do CEVAP
* Criar o arquivo [data/config/emails_compartilhamento.json](file:///C:/Projetos/Inova/projects/motor-cevap/data/config/emails_compartilhamento.json) contendo os e-mails dos envolvidos.
* A estrutura unificada de JSON seguirá o padrão do lead-csc:
```json
{
  "comentarios": "Lista unificada de e-mails para compartilhamento da planilha CEVAP (consultores e gerência)",
  "consultores_bup_pecas": [
    {
      "nome": "Filipe Paiva",
      "email": "filipe.paiva@inovamaquinas.com.br"
    },
    {
      "nome": "Katia Almeida",
      "email": "katia.almeida@inovamaquinas.com.br"
    }
  ],
  "coordenadores_gerentes_outros": [
    {
      "nome": "Roberto Reis",
      "email": "roberto.reis@inovamaquinas.com.br"
    },
    {
      "nome": "Victor Bernardi",
      "email": "victor.bernardi@inovamaquinas.com.br"
    }
  ]
}
```

### Passo 3: Atualização do Gerador de KPIs HTML
* Modificar o script [generate_cevap_kpis.py](file:///C:/Projetos/Inova/projects/motor-cevap/scripts/generate_cevap_kpis.py):
  * Mudar o caminho de escrita `OUTPUT_PATH` para `ROOT / "data" / "output" / "daily_report_kpis.html"`.
  * Ajustar a codificação de escrita com `encoding='utf-8'` (Vacina de Encoding).
  * Harmonizar o design visual do HTML com o estilo corporativo premium do `daily_report_kpis.html` do lead-csc, mantendo os KPIs específicos do CEVAP:
    * **Cartões de KPI**: Cobertura, Conversão Acumulada, Aging Médio, Faturamento Realizado.
    * **Desempenho por Consultor**: Estatísticas detalhadas de contatos e vendas do Filipe Paiva e Katia Almeida.
    * **Metodologia/Aging**: Tabela comparativa e status do envelhecimento dos contatos comerciais.
    * **Alertas de Inconsistência**: Caixa vermelha de atenção caso existam vendas declaradas sem nota validada no Protheus.

### Passo 4: Automação do Agendamento Diário (SMTP)
* Criar o script PowerShell [scripts/scheduler_daily.ps1](file:///C:/Projetos/Inova/projects/motor-cevap/scripts/scheduler_daily.ps1):
  * Carregar as variáveis de credenciais SMTP corporativas e caminhos absolutos baseados no virtualenv do CEVAP (`.venv\Scripts\python.exe`).
  * Executar a consolidação e a geração do HTML.
  * Ler o `daily_report_kpis.html` gerado e enviá-lo por e-mail automaticamente a Roberto Reis e demais destinatários configurados no `.env`.

### Passo 5: Automação do Compartilhamento de Planilhas (OneDrive)
* Criar o script PowerShell [scripts/share_onedrive_leads.ps1](file:///C:/Projetos/Inova/projects/motor-cevap/scripts/share_onedrive_leads.ps1):
  * Ler os e-mails definidos em `data/config/emails_compartilhamento.json`.
  * Autenticar via Microsoft Graph API com Device Code e efetuar o convite de leitura de forma silenciosa para o arquivo `CEVAP_ATIVACAO.xlsx` no OneDrive do usuário.

---

## 🔒 Regras de Segurança e Conformidade
* **Edição Cirúrgica**: Modificar o script Python de KPIs usando substituição cirúrgica com `replace`, preservando todas as lógicas de leitura de dados existentes.
* **Standby Mode**: Após a aprovação deste plano, iniciaremos a etapa de construção (`/build`).
* **Vacina de Encoding**: Garantir que toda abertura/leitura/escrita use explicitamente `encoding='utf-8'`.
