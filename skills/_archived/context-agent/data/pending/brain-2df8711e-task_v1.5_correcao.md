# Task: Wave 8.2 - Correção Cirúrgica e Simplificação

## 1. Cleanup de Estilo (CSS)
- [ ] Remover classes `.card-shell` e `.card-core` (reverter para `.glass-card` simples).
- [ ] Corrigir `.glass-card` para `height: auto` (resolve o erro do menu cobrindo a tela).
- [ ] Reduzir altura das barras de progresso de 16px para **8px**.
- [ ] Ajustar barras para ocuparem 100% da largura disponível no card (remover `width: 100px` fixo).
- [ ] Refinar `.nav-island` para ser novamente uma pílula compacta no topo.

## 2. Restauração Estrutural (HTML)
- [ ] Remover wrappers de "Double-Bezel" em todos os componentes.
- [ ] Simplificar o Hero KPI (Faturamento Mensal) para exibir a barra total e a barra do segmento sobreposta de forma limpa.
- [ ] Reorganizar o card de Acumulado do Ano para incluir Meta/Realizado do Segmento sem poluição visual.

## 3. Ajustes Lógicos (JavaScript)
- [ ] Remover títulos dos eixos no gráfico de evolução (Chart.js/Apex).
- [ ] Corrigir a injeção do nome do segmento nos cards das filiais.
- [ ] Garantir que o atingimento (%) do segmento apareça ao lado da barra nas filiais.
- [ ] Validar a sobreposição (z-index) das barras `main` e `segment`.

## 4. Auditoria Final
- [ ] Validar visualmente o menu de filtros.
- [ ] Verificar integridade matemática via Scanner (se o ambiente permitir).
- [ ] Gerar Walkthrough de encerramento.
