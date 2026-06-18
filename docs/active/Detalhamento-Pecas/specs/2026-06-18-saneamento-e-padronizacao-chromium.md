# Especificação Técnica — Saneamento de Scripts & Padronização do Chromium (Revisada)

> **Projeto:** Detalhamento-Pecas  
> **Autor:** Antigravity (AI Coding Assistant)  
> **Data:** 18 de Junho de 2026  
> **Fase:** Pesquisa (`/brainstorm`) — Modo Read-Only  

---

## 1. Introdução e Contexto

No decorrer do desenvolvimento do projeto `Detalhamento-Pecas`, foram criadas diversas ramificações de scripts para viabilizar testes, diagnóstico de seletores do Power BI (Chromium/Playwright) e uma migração experimental para a estrutura de estágios ICM (Interpretable Context Methodology).

Essa sobreposição de arquivos gerou:
1. **Redundância e Desalinhamento:** Os scripts localizados nos estágios (ex: `02_extrair/scripts/extract.py`) estão desatualizados em relação ao motor de produção em `src/`. Eles não contêm o isolamento de seletores por container visual para Vendas vs. Devoluções nem o suporte a Devoluções, gerando o risco de download cruzado e quebra de pipeline.
2. **Conflito de Arquivos Temporários:** Scripts de teste como `debug_pbi.py` e imagens residuais de debug (`debug_filter.png`, etc.) poluem o repositório.
3. **Instabilidade do Chromium/Playwright:** Erros frequentes de bloqueio de arquivos (como `Acesso Negado 0x5` no Windows ou `downgrade_utils.cc`) ocorrem devido a:
   * Processos órfãos do Chromium rodando em background que mantêm travas ativas na pasta de perfil persistente.
   * Conflitos de versão de Playwright/Chromium entre diferentes ambientes virtuais (`dashboard-inova-data-export` vs. `Detalhamento-Pecas`) que compartilham a mesma pasta `user_profile`.

Para realizar este saneamento de pastas de forma segura, é de suma importância analisar e sincronizar todos os documentos de governança (`CLAUDE.md`, `GEMINI.md`, `SKILL.md` e os `CONTEXT.md` locais dos estágios) para que nenhuma instrução ou link de referência a caminhos físicos fique desatualizado ou inconsistente.

---

## 2. Inventário de Arquivos e Diagnóstico de Saneamento

### 2.1. Arquivos Oficiais de Produção (A Preservar e Tornar Oficiais)
Estes arquivos compõem o pipeline operacional bem-sucedido que rodou a carga física E2E:
* **Orquestrador:** `run.py` (raiz)
* **Autenticador de Sessão:** `authenticate.py` (raiz)
* **Módulos de Negócio (`src/`):**
  * `src/config.py` (Configurações físicas e caminhos canônicos)
  * `src/extract.py` (Extração de Vendas com isolamento por visual-container)
  * `src/extract_devolucoes.py` (Extração de Devoluções de 2025 até hoje)
  * `src/transform.py` (Limpeza de metadados do PBI e validação de schema)
  * `src/load.py` (Gravação segura em Parquet e leitura de histórico)
  * `src/tools/stout_memory_capture.py` (Rastreamento de sessão e aprendizados)

### 2.2. Arquivos Temporários, Debug ou Desatualizados (A Deletar)
* **Scripts de Debug na Raiz:**
  * `debug_pbi.py` (Script de teste isolado para inspecionar seletores)
* **Imagens de Debug na Raiz:**
  * `debug_initial_page.png`
  * `debug_filter.png`
  * `debug_filter_pos.png`
  * `debug_error_page.png`
  * `debug_devolucoes_error.png`
* **Scripts Duplicados e Desatualizados nas Pastas ICM:**
  * As subpastas de estágio (`01_autenticar/`, `02_extrair/`, `03_transformar/`, `05_persistir/`) contêm subdiretórios `scripts/` com cópias desatualizadas do código. Eles serão saneados, mantendo as pastas de estágios apenas para contexto e logs (`CONTEXT.md` e `output/`).

---

## 3. Diagnóstico e Padronização do Chromium (Gestão de Sessão)

### 3.1. Causa Raiz dos Travamentos
1. **Travas de Arquivo (File Locks) no Windows:** O Chromium com perfil persistente cria arquivos de lock (`lockfile`, `SingletonLock`). Se o script cai de forma abrupta ou o usuário cancela a execução, o processo do Chromium vira um zumbi em segundo plano. Novas execuções recebem `Acesso Negado 0x5` ao tentar ler a pasta `user_profile`.
2. **Poluição de Perfil por Diferentes Venvs:** O script de autenticação do projeto vizinho (`dashboard-inova-data-export`) utiliza a sua própria venv, e este projeto (`Detalhamento-Pecas`) utiliza outra. Se as versões do Playwright diferirem, o Chromium trava ao tentar abrir o perfil devido à incompatibilidade do banco de dados local do navegador.

### 3.2. Padrão Definitivo de Resiliência
Para garantir que o Chromium nunca falhe por concorrência ou chaves travadas, estabeleceremos a seguinte política em código nos scripts de automação:

1. **Auto-Clean de Processos Órfãos (Pre-flight Kill):**
   Antes de disparar o `launch_persistent_context`, o script executará uma rotina em Python que identifica e elimina cirurgicamente processos órfãos do Chrome/Chromium que estejam rodando sob o diretório do Playwright (`ms-playwright`), liberando as chaves.
   * *Código de Implementação:*
     ```python
     import subprocess
     import sys
     import logging
     
     logger = logging.getLogger(__name__)

     def limpar_processos_playwright_zumbis():
         if sys.platform == 'win32':
             logger.info("Executando pre-flight check para encerrar processos zumbis do Playwright Chromium...")
             try:
                 # Comando PowerShell para matar processos chrome.exe executando sob ms-playwright
                 cmd = "Get-Process -Name chrome -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*ms-playwright*'} | Stop-Process -Force"
                 subprocess.run(["powershell.exe", "-Command", cmd], capture_output=True, check=False)
                 logger.info("Zumbis encerrados ou nenhum processo encontrado.")
             except Exception as e:
                 logger.warning(f"Falha ao rodar limpeza de processos zumbis: {e}")
     ```

2. **Unificação da Versão do Playwright:**
   Para garantir estabilidade completa de perfil, as dependências dos projetos devem ser instaladas e alinhadas sob a mesma venv canônica (`C:\Projetos\Inova\.venv`).

3. **Uso Exclusivo de Contexto Persistente com `headless=False`:**
   Dada a restrição do Azure AD SSO na Inova, todas as automações usarão:
   * Navegador visível (`headless=False`).
   * Configuração regional correta de data (`locale="pt-BR"`).
   * Range de slicer de data no formato de tela brasileiro (`DD/MM/AAAA`).
   * Fechamento explícito e seguro do contexto no bloco `finally` da automação para minimizar locks.

---

## 4. Alinhamento da Documentação de Referência

Ao mover e limpar os scripts de estágios, as seguintes atualizações devem ser aplicadas nos arquivos Markdown de documentação de governança:

### 4.1. `CLAUDE.md` (Raiz)
* **Mapa do Workspace:** Ajustar a descrição das pastas `01_autenticar/` a `05_persistir/` para explicitar que elas mantêm apenas os metadados (contratos e logs de execução), e não mais código físico duplicado. Consolidar `src/` como diretório oficial do código-fonte de todos os estágios do pipeline.
* **Regras de Navegação:** Atualizar a Regra 6 para deixar explícito que os scripts oficiais de produção residem unicamente em `src/`, eliminando a duplicação nos estágios.

### 4.2. `01_autenticar/CONTEXT.md` (Estágio 01)
* **Script de Autenticação:** Atualizar o link do script para apontar para o `authenticate.py` local na raiz do projeto (`projects/Detalhamento-Pecas/authenticate.py`), oficializado e configurado com a rotina de auto-clean do Chromium, eliminando o redirecionamento manual para o projeto vizinho `dashboard-inova-data-export`.

---

## 5. Próximos Passos
Após a aprovação desta especificação:
1. Avançaremos para a **Fase de Estratégia (`/plan`)** gerando o plano de tarefas atômicas em `docs/plans/2026-06-18-saneamento-e-padronizacao-chromium-plan.md`.
2. Após aprovação humana do plano, executaremos o saneamento físico dos arquivos, atualizações da documentação de governança e integraremos o script de auto-clean de zumbis do Playwright.
