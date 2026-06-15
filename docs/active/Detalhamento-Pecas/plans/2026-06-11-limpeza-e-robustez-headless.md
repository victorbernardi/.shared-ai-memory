---
name: 2026-06-11-limpeza-e-robustez-headless
description: "Plano de tarefas sequenciais para limpeza de arquivos temporários, migração estável para headless no Playwright e tratamento amigável de expiração de sessão do Power BI."
version: 1.0.0
date: "2026-06-11"
status: "Aprovado"
---

# Plano de Execução: Limpeza e Robustez do Scraper (Headless & Alertas)

Este plano detalha as etapas atômicas para implementar os requisitos definidos na Spec correspondente.

## Tarefas Sequenciais

### Fase 1: Limpeza do Repositório (Item 1 & Sugestão 1)
- [ ] **Task 1.1: Deletar scripts auxiliares/descartáveis**
  - **Ação**: Excluir `projects/Detalhamento-Pecas/debug_pbi.py` e `projects/Detalhamento-Pecas/authenticate.py`.
  - **Validação**: Verificar com `git status` que os arquivos foram deletados.
- [ ] **Task 1.2: Deletar imagens e planilhas temporárias**
  - **Ação**: Deletar todas as imagens `debug_*.png` e as planilhas `Detalhamento-Pecas-2025.xlsx` e `Detalhamento-Pecas-2026.xlsx` da raiz do projeto.
  - **Validação**: Verificar que a raiz do projeto não possui arquivos `.png` ou `.xlsx`.
- [ ] **Task 1.3: Atualizar o arquivo `.gitignore`**
  - **Ação**: Adicionar regras para ignorar arquivos `debug_*.png`, `.xlsx` na raiz do projeto e outras pastas/arquivos desnecessários.
  - **Validação**: Verificar com `git status` que os arquivos de debug não são mostrados como untracked.

### Fase 2: Configuração do Headless no Playwright (Sugestão 2)
- [ ] **Task 2.1: Modificar `extract.py` para usar `headless=True`**
  - **Ação**: Alterar a linha de inicialização do navegador em `projects/Detalhamento-Pecas/src/extract.py` de `headless=False` para `headless=True`.
  - **Validação**: Executar pytest e certificar-se de que a inicialização headless não quebra a importação.

### Fase 3: Monitoramento e Alerta Amigável (Sugestão 3)
- [ ] **Task 3.1: Implementar detecção de timeout de sessão no `extract.py`**
  - **Ação**: Adicionar um bloco try/catch no início da navegação do Playwright em `projects/Detalhamento-Pecas/src/extract.py`. Se ocorrer um TimeoutError no carregamento do relatório ou iframe, capturar e lançar uma mensagem amigável no console instruindo o usuário a renovar as credenciais usando o script central `authenticate.py`.
  - **Validação**: Forçar erro de autenticação temporariamente (ex: mudando o caminho do profile) e validar que a mensagem exibida no terminal é legível e em português.

### Fase 4: Homologação Final (TDD e Integração)
- [ ] **Task 4.1: Rodar os testes automatizados locais**
  - **Ação**: Executar `.venv/Scripts/pytest` em `Detalhamento-Pecas`.
  - **Validação**: Obter 9/9 testes passando em verde.
- [ ] **Task 4.2: Comitar as alterações e realizar push para a branch remota**
  - **Ação**: Executar `git add .`, comitar com a mensagem seguindo os padrões convencionais e efetuar `git push origin master`.
