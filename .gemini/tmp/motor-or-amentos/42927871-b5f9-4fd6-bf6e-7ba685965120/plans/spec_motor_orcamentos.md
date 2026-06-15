# Especificação Técnica (Spec): Scraper Motor-orçamentos

## 1. Visão Geral
O projeto **Motor-orçamentos** tem como objetivo extrair automaticamente a tabela de orçamentos abertos de um dashboard do Power BI Embedded. Ele reaproveitará a arquitetura e a infraestrutura de sessão persistente já consolidadas no projeto `Detalhamento-Pecas` e `dashboard-inova-data-export`.

## 2. Escopo de Funcionalidades
- **Autenticação Reutilizável**: Utilizar o perfil de navegador persistente já existente para evitar prompts repetitivos de login (SSO).
- **Navegação**: Acessar o relatório Power BI e navegar especificamente para a aba lateral "Orçamento em Aberto".
- **Extração Sem Filtros**: Conforme regra de negócios atual, a tabela já apresenta a visão desejada, dispensando o preenchimento de *date slicers*.
- **Identificação Dinâmica do Visual**: Como a matriz/tabela alvo não possui um título em `<h3>` (diferente da tabela de Vendas), o robô deve identificá-la pela presença de seus cabeçalhos ("Num Orc", "Filial", "Cliente", "Orc. em Aberto") dentro de um `<visual-container>`.
- **Download Resiliente**: Interceptar o evento de download após acionar os menus do Power BI ("Mais opções" -> "Exportar dados" -> "Exportar") e salvar o arquivo resultante na pasta do projeto.

## 3. Arquitetura de Diretórios
```text
C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos\
├── data/
│   └── output/                 # Destino do arquivo exportado (.xlsx ou .csv)
├── src/
│   ├── __init__.py
│   ├── config.py               # Variáveis de ambiente, caminhos e seletores globais
│   ├── extract.py              # Classe/funções do Playwright
│   └── transform.py            # (Futuro) Tratamento de colunas do Pandas, se necessário
├── tests/                      # Scripts soltos de depuração e visualização (se necessário)
├── run.py                      # Orquestrador da extração
└── requirements.txt            # Dependências (playwright, pandas, openpyxl)
```

## 4. Estratégia de Identificação da Tabela (DOM)
Como o visual não possui cabeçalho `<h3 title="...">`, usaremos as seguintes alternativas combinadas para localizar a matriz:
1. Buscar o container com base nas palavras-chave do cabeçalho da tabela:
   ```python
   # Exemplo de seletor no Playwright
   tabela = pbi_iframe.locator('visual-container').filter(has_text="Num Orc").filter(has_text="Orc. em Aberto").first
   ```
2. Garantir que a tabela está visível.
3. Acionar o gatilho flutuante (`.vc-menu-trigger` ou botão com `aria-label="Mais opções"`).

## 5. Tolerância a Falhas
- **Timeout no Carregamento**: Esperas customizadas para frames e visuais pesados (até 60-120s no PBI).
- **Fallback de Clique**: Uso de cliques forçados (`force=True`) para suplantar divs invisíveis que interceptam cliques (ex: `cdk-overlay-backdrop`).
- **Renovação de Sessão**: Se não for possível achar a aba, exibir log amigável instruindo o usuário a rodar o script base de autenticação (`authenticate.py`).