# GCC Learnings - Dashboard Branding JD

## O que funcionou e por quê
- **Relative Path Assets:** O uso de caminhos relativos (`../imagens/JD_logo.png`) para carregar os logos funcionou perfeitamente, mantendo o dashboard auto-suficiente dentro da estrutura de pastas do projeto.
- **Brand Consistency:** Aplicar as cores hexadecimais exatas da John Deere (`#367C2B` e `#FFDE00`) transformou instantaneamente a percepção de valor do dashboard, saindo de uma ferramenta genérica para um produto institucional "ready to present".

## Decisões técnicas validadas
- **Image Filters:** O uso de filtros CSS (`brightness-0 invert opacity-80`) para o logo da Inova permitiu que ele se integrasse suavemente ao modo escuro sem precisar de edição manual do arquivo original.
- **Color Mapping:** Mapear o Verde JD para a safra 24/25 e o Amarelo JD para a safra atual (25/26) criou uma hierarquia visual clara, onde a cor mais "brilhante" (amarelo) destaca a performance mais recente.

## Padrões descobertos
- **Theming via Template:** Centralizar as cores em variáveis CSS no template HTML facilitou a atualização global da paleta sem precisar tocar na lógica de injeção de dados.
