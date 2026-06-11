# Memória do Projeto: De Volta para a Inova

## Regras de Negócio da Campanha (De Volta para a Inova)
- **Terminologia:** Utilizar sempre o termo **Leads** (substituindo Oportunidades).
- **Modelo de Custo:**
    - **Mão de Obra:** Arcada integralmente pela John Deere (subsídio/aporte financeiro).
    - **Peças/Kits:** Vendas realizadas pela INOVA (objetivo principal de faturamento). Apenas para kit completo.
- **Objetivo Técnico:** Atualização do horímetro das máquinas no sistema **Pops** durante a revisão.
- **Fonte de Verdade (Horímetro):** Utilizar a coluna `forecasted machine hours` (estimativa JDLink).
- **Alavancas Adicionais:** Inspeção visual gratuita, Análise de óleo, INOVA PAY. Meta de +1 Lead cruzado por revisão.

## Playbook de Priorização de Leads
- **A (Ataque Imediato):** Máquinas ativas, alto potencial, sem serviço > 12 meses até 48 meses. (Ação: Ligação + Proposta + Agenda).
- **B (Recuperação):** Clientes compram peças, mas não fazem serviço na Inova.
- **C (Risco de Perda):** Sem compra de peças e sem serviço há mais de 48 meses.
- **D (Baixo Potencial):** Máquinas antigas, baixa utilização, cliente sensível a preço. (Ação: WhatsApp, funil leve).

## Campanhas de Cross-Sell Ativas
- **SEM FOLGA:** Venda de kits de embuchamento com 50% OFF (subsídio JD). Oferecer em todo contato ativo.
- **RECUPERAÇÃO TOTAL:** Componentes e peças para componentes.

## Localização de Arquivos
`C:\Projetos\Inova\projects\De-volta-para-inova`
- **Áudios e Transcrições:** Diversos arquivos `.m4a` e `.md` na pasta raiz do projeto.
- **Preços:** `Preço de peças das revisões.xlsx` (exclusivo para a linha de Construção - C&F).
- **Código Python:** `generate_leads_using_potential.py` (executa a ingestão a partir da base de potencial de ouro).
- **Planilhas de Saída:**
    - `leads_campanha_de_volta_construcao_potencial.xlsx` (planilha definitiva de Construção Civil gerada via Potencial M3).

## Insights Técnicos & Limitações
- **Ingestão via Potencial M3:** Ignoramos `chassis_nao_classificados.parquet` (sujo) e adotamos `dataset_ouro_potencial_chassi_v1.parquet` (dado tratado e limpo, sem ruído) como a única fonte de verdade.
- **Linha de Foco:** Foco exclusivo em Construção Civil (C&F). A frota agrícola e implementos não fazem parte da campanha.
- **Cobertura de Preços:** 100% dos leads de Construção Civil estão precificados com base nos kits de revisão cadastrados.

## Próximos Passos
1. Integrar a classificação (A, B, C, D) no script de Leads.
2. Mapear valores do arquivo `Preço de peças das revisões.xlsx` por modelo/chassi para agilizar as cotações, conforme manda o playbook ("Orçamento Rápido").
3. Obter a tabela de preços de revisão para a linha Agrícola para cobrir os 95% de leads pendentes de precificação.

