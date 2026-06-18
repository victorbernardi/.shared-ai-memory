# Spec: Diagnóstico de Travamento no Carregamento

O dashboard permanece na tela de "Carregando" e não finaliza a inicialização. Este documento detalha as possíveis causas técnicas e o plano de mitigação.

## Causas Prováveis (Hipóteses)

### 1. Erro de Parsing no `data_snapshots.js` [ALTA PROBABILIDADE]
Como o arquivo contém dados reais (caracteres especiais, aspas, etc.), qualquer falha na geração do JSON pelo Python pode resultar em um erro de sintaxe JS, impedindo o carregamento de todos os scripts subsequentes.
- **Sintoma:** Console do navegador exibindo `Uncaught SyntaxError`.

### 2. Race Condition: `dashboardData` Indefinido
Embora o `window.onload` deva esperar todos os scripts, se houver um delay no processamento do arquivo de 332KB pelo motor JS do navegador, a variável `dashboardData` pode não estar disponível no exato momento da verificação.
- **Sintoma:** Mensagem de "Erro Crítico: data_snapshots.js não encontrado" (logado no console).

### 3. Falha em Dependências Externas (CDN)
O dashboard depende de:
- `lucide` (ícones)
- `apexcharts` (gráficos)
- `gsap` (animações)
Se o usuário estiver em uma rede restrita ou sem internet, a chamada `lucide.createIcons()` ou `new ApexCharts()` irá falhar e interromper a função `init()`.
- **Sintoma:** Tela presa em "Carregando" sem erro visível na interface.

### 4. Incompatibilidade de Tipos no Filtro
Se `rawData.performance` contiver registros onde o campo `ANO` é nulo ou não numérico, o método `.filter()` pode gerar uma exceção.

---

## Plano de Ação Imediato

### [Passo 1] Robusteza no Carregamento
Vou encapsular o `init()` em um bloco `try-catch` global e adicionar logs visíveis na tela para que o usuário possa nos informar o erro exato sem precisar abrir o console.

### [Passo 2] Verificação de Integridade dos Dados
Vou sanitizar a exportação no `aggregator.py` para garantir que `NaN` ou `Infinity` (comuns em cálculos financeiros) não sejam exportados para o JSON, o que quebra o JavaScript.

### [Passo 3] Fallback de Bibliotecas
Adicionar verificações de existência para `ApexCharts` e `lucide` antes de chamá-los.

---

## Perguntas para o Usuário
1. Você está visualizando algum erro no **Console do Desenvolvedor** (F12)?
2. A máquina possui acesso à internet para carregar os scripts de gráficos (CDN)?
