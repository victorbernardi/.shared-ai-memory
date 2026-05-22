# Learnings: executive-summary-layout
- **Motor de Insights:** A funcao `calculate_insights` automatizou a deteccao de pontos criticos, reduzindo o tempo de analise humana.
- **Arquitetura Modular:** A reestruturacao do script em funcoes por pagina (`page_executive_summary`, `page_subgroups`, etc.) eliminou debitos tecnicos de indentacao e facilitou a expansao para 4 paginas.
- **Hierarquia Estrategica:** A nova ordem (Resumo -> Macro -> Micro -> Matriz) criou um storytelling mais fluido para o stakeholder.
- **Desafio de Fontes:** Emojis no matplotlib exigem configuracao de fontes externas; optamos por manter a funcionalidade textual em prol da estabilidade.
