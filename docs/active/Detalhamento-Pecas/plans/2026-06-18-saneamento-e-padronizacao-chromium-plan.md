# Plano Executivo — Saneamento de Scripts & Padronização do Chromium (Revisado)

> **Projeto:** Detalhamento-Pecas  
> **Autor:** Antigravity (AI Coding Assistant)  
> **Data:** 18 de Junho de 2026  
> **Fase:** Estratégia (`/plan`) — Standby Mode (Aguardando Aprovação Humana)  

---

## 1. Objetivo
Executar a limpeza do repositório removendo códigos temporários de debug, móbiles duplicados e desatualizados das pastas ICM, atualizar todas as documentações de governança e referência (`CLAUDE.md`, `01_autenticar/CONTEXT.md`), e implementar o padrão de auto-clean de processos zumbis do Chromium para estabilizar os logins contra travamento de chaves (`Acesso Negado 0x5`).

---

## 2. Tarefas Atômicas de Implementação

### [Fase 1: Saneamento Físico de Arquivos]

* **Task 1.1: Deletar Scripts e Imagens de Debug na Raiz**
  * Remover os arquivos:
    * `debug_pbi.py`
    * `debug_initial_page.png`
    * `debug_filter.png`
    * `debug_filter_pos.png`
    * `debug_error_page.png`
    * `debug_devolucoes_error.png`
  * *Verificação:* O diretório raiz não deve mais conter estes arquivos.

* **Task 1.2: Remover Cópias Desatualizadas nos Estágios ICM**
  * Deletar as pastas de scripts obsoletas:
    * `01_autenticar/scripts/` (e subpastas)
    * `02_extrair/scripts/`
    * `03_transformar/scripts/`
    * `05_persistir/scripts/`
  * *Verificação:* As pastas numéricas de estágios manterão apenas `CONTEXT.md` e a pasta `output/` correspondente.

---

### [Fase 2: Padronização do Chromium (Resiliência contra Locks)]

* **Task 2.1: Implementar a Rotina de Auto-Clean de Zumbis em `src/extract.py`**
  * Adicionar a função `limpar_processos_playwright_zumbis()` no início de `src/extract.py` (ou em módulo compartilhado).
  * Chamar essa função logo no início de `extrair_detalhamento_pecas()`.
  * *Código da Rotina:*
    ```python
    import subprocess
    import sys
    import logging

    logger = logging.getLogger(__name__)

    def limpar_processos_playwright_zumbis():
        if sys.platform == 'win32':
            logger.info("Executando pre-flight check para encerrar processos zumbis do Playwright Chromium...")
            try:
                # Mata processos do chrome rodando da pasta ms-playwright
                cmd = "Get-Process -Name chrome -ErrorAction SilentlyContinue | Where-Object {$_.Path -like '*ms-playwright*'} | Stop-Process -Force"
                subprocess.run(["powershell.exe", "-Command", cmd], capture_output=True, check=False)
                logger.info("✓ Processos zumbis limpos com sucesso.")
            except Exception as e:
                logger.warning(f"Falha ao rodar limpeza de processos zumbis: {e}")
    ```

* **Task 2.2: Implementar a Rotina no Scraper de Devoluções (`src/extract_devolucoes.py`)**
  * Importar e chamar `limpar_processos_playwright_zumbis()` no início da função `extrair_detalhamento_devolucoes()`.

* **Task 2.3: Atualizar o Script de Autenticação na Raiz (`authenticate.py`)**
  * Importar e chamar `limpar_processos_playwright_zumbis()` no início da execução de `authenticate.py` (antes de instanciar o context persistente).

---

### [Fase 3: Sincronização e Atualização da Documentação]

* **Task 3.1: Atualizar o `CLAUDE.md` na Raiz**
  * Ajustar a arquitetura visual no Mapa do Workspace para remover referências a scripts nas pastas numéricas (explicitar que mantêm apenas metadados/logs).
  * Modificar a Regra de Navegação nº 6 para esclarecer que os scripts oficiais de produção residem unicamente em `src/`.

* **Task 3.2: Atualizar o `01_autenticar/CONTEXT.md`**
  * Alterar o link de referência do Script de Autenticação para apontar para o `authenticate.py` local da raiz do projeto (`projects/Detalhamento-Pecas/authenticate.py`), que está oficializado e atualizado.

---

### [Fase 4: Verificação e Validação E2E]

* **Task 4.1: Executar Testes Automatizados**
  * Rodar o framework de teste na venv para confirmar que os testes continuam passando.
  * *Comando:* `pytest` na raiz do projeto.
  * *Critério de Sucesso:* 100% de testes bem-sucedidos.

* **Task 4.2: Executar um Dry-run de Autenticação**
  * Executar `python authenticate.py` para testar se a rotina de auto-clean executa de forma limpa e abre a janela do navegador.

---

## 3. Estado de Standby
Em conformidade com a trava de segurança da **Fase de Estratégia**, o agente permanece em **STANDBY** aguardando a revisão e aprovação deste plano pelo usuário para avançar para a **Fase de Execução (`/build`)**.
