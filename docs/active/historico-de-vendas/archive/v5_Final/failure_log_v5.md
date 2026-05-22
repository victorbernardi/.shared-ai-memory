# 🪵 Failure Log - Projeto: Histórico de Vendas

## [2026-05-13] Dissonância Cognitiva e Regressão de Lógica
- **Falha:** Tentativa de exibir rótulos financeiros (R$) em barras de volume (unidades), causando confusão visual sobre a magnitude dos dados.
- **Impacto:** O relatório perdia credibilidade visual, pois barras menores pareciam ter valores maiores.
- **Causa Raiz:** Priorização de "adicionar informação" sem ajustar a base visual (comprimento das barras).
- **Medida Corretiva:** Implementada a unificação de métrica (Eixo X e Rótulo ambos em R$).
- **Regra Stout para o Futuro:** Todo gráfico deve respeitar a **"Paridade Visual-Numérica"**. Se o rótulo é financeiro, o comprimento da barra deve ser financeiro.

## [2026-05-13] Artefatos Visuais em Logos IA
- **Falha:** Uso de logos geradas por IA com fundos brancos/fringe em cabeçalhos coloridos.
- **Causa Raiz:** Limitação de processamento de transparência em tempo de execução via script simples.
- **Medida Corretiva:** Remoção das logos para focar na sobriedade dos dados.
- **Regra Stout para o Futuro:** Protocolo "Data-First". O design deve servir ao dado, nunca o contrário.

## [2026-05-13] Corrupção de Código em Edições Multiline
- **Falha:** Deleção acidental de funções (`draw_kpi`) e variáveis (`df_merge`) ao editar utilitários.
- **Impacto:** Quebra imediata do orquestrador (NameError).
- **Causa Raiz:** Gestão imprecisa de line-ranges em arquivos densos com a ferramenta `replace_file_content`.
- **Medida Corretiva:** Adoção de `write_to_file` para reescritas completas de utilitários pequenos e uso de anchors de texto em `multi_replace`.
- **Regra Stout para o Futuro:** Sempre rodar `python <script> --check` ou similar após modificações em `utils.py`.

## [2026-05-13] Sobreposição Visual em Alta Densidade (Página 1)
- **Falha:** Sobreposição de rótulos de dados (R$) e nomes de subgrupos ao expandir para 20 itens.
- **Impacto:** Relatório ilegível e quebra da autoridade técnica do documento.
- **Causa Raiz:** Auditoria visual insuficiente (IA não "enxergou" a colisão) e parametrização estática insuficiente para a nova densidade.
- **Medida Corretiva:** Implementação de layout dinâmico e redução agressiva de fontes para densidades > 10 itens.
- **Regra Stout para o Futuro:** Auditoria visual deve ser acompanhada de validação de "Collision Detection" (check de distância entre elementos via script) em layouts de alta densidade.
