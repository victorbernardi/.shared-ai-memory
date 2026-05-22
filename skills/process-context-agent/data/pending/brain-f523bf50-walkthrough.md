# Walkthrough: Automação do Pipeline Inova M6 Dashboard (v1.2)

Este documento resume a implementação do pipeline de deployment automatizado para o Inova M6 Executive Dashboard, focando na performance e integridade financeira.

## Mudanças Implementadas

### 1. Orquestração One-Page
- **Script**: [Wave9_Deployment_OnePage.py](file:///c:/Projetos/Inova/Metas%20Pe%C3%A7as/03_Scripts_Rascunhos/Wave9_Deployment_OnePage.py)
- **Função**: Centraliza a execução do Motor M6, Auditoria, Extração e Agregação.
- **Segurança**: Implementa o conceito de *Atomic Swap* (Staging -> Production) apenas após aprovação da auditoria.

### 2. Auditoria Fonte da Verdade (v1.2 Lean)
- **Script**: [Wave8_Auditoria_Fonte_Verdade.py](file:///c:/Projetos/Inova/Metas%20Pe%C3%A7as/03_Scripts_Rascunhos/Wave8_Auditoria_Fonte_Verdade.py)
- **Critério**: Paridade financeira absoluta entre CSVs originais e Excel agregado.
- **Otimização**: Removida a aba de detalhe transacional para agilizar o consumo pelo BI.

## Resultados da Validação

### Paridade Financeira
- **Target (CSV)**: R$ 262.936.311,32
- **Excel (Aggregated)**: R$ 262.936.311,32
- **Diferença**: R$ 0,00 (100% de paridade)

### Performance do Pipeline
- **Tempo de Execução**: ~60-90 segundos (reduzido pela remoção da aba de 15MB).
- **Status de Duplicidade**: Auditado indiretamente via paridade (qualquer duplicidade afetaria a soma final).

## Como Executar
Basta rodar o comando abaixo no terminal do projeto:
```powershell
python "c:\Projetos\Inova\Metas Peças\03_Scripts_Rascunhos\Wave9_Deployment_OnePage.py"
```

## Próximos Passos
- Agendamento automático via Cron/Task Scheduler.
- Monitoramento de logs em `05_Resultados`.
