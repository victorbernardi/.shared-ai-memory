# Plano de Implementação: Scraper de Orçamentos Abertos

## Objetivo
Criar um script de web scraping em Python utilizando o Playwright para automatizar o download dos orçamentos abertos no dashboard Power BI Embedded. O script seguirá a mesma arquitetura do projeto `Detalhamento-Pecas`, compartilhando a sessão de autenticação do perfil do Chrome existente e focado na aba "Orçamento em Aberto".

## Arquivos Chave e Contexto
- **Diretório**: `C:\Projetos\Inova\pipelines\potencial-clientes\Motor-orçamentos`
- **Componentes**:
  - `src/config.py`: Configurações de URLs, tempos de espera e caminhos de diretório (apontando para o `browser_state` do dashboard export).
  - `src/extract.py`: Lógica principal do Playwright para navegar, selecionar a aba correta e localizar a tabela para exportação.
  - `run.py`: Arquivo de entrada para executar o processo.
  - `requirements.txt`: Dependências do projeto (Playwright, Pandas, etc.).

## Estratégia e Passos de Implementação

1. **Estrutura de Diretórios**:
   - Criar as pastas `src`, `data/output` e `tests` dentro de `Motor-orçamentos`.

2. **Configuração (`src/config.py`)**:
   - Definir `REPORT_URL` (mesma url base do Inova Power Embedded).
   - Definir caminho do `USER_PROFILE_DIR` apontando para `C:/Projetos/Inova/projects/dashboard-inova-data-export/browser_state/user_profile`.

3. **Extração (`src/extract.py`)**:
   - Iniciar o contexto persistente do Chromium com Playwright.
   - Navegar até o dashboard.
   - **Navegação de Aba**: Localizar o texto "Orçamento em Aberto" no iframe e clicar.
   - **Filtros**: Não há necessidade de filtros adicionais conforme informado.
   - **Localização da Tabela**: Como a tabela não possui título explícito (h3), ela será localizada baseada nos cabeçalhos de coluna, utilizando um seletor robusto como `visual-container` contendo o texto das colunas chave (ex: "Num Orc" e "Orc. em Aberto").
   - Fazer *hover* na tabela, clicar em "Mais opções" (`.vc-menu-trigger`), depois em "Exportar dados".
   - Confirmar exportação no diálogo gerado e aguardar o download, salvando em `data/output`.

4. **Execução (`run.py`)**:
   - Criar o script chamando a função `extrair_orcamentos_abertos()`.
   - Adicionar tratamento de erro elegante para falhas de renderização.

## Verificação e Testes
- Rodar `python run.py`.
- Verificar a criação do arquivo exportado no diretório `data/output/`.
- Inspecionar via log se os localizadores (tanto da aba quanto da tabela e botão de exportar) atuaram corretamente sem timeout.
