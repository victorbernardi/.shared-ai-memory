---
name: 2026-06-11-limpeza-e-robustez-headless
description: "Especificação técnica para limpeza de arquivos temporários, migração estável para headless no Playwright e tratamento amigável de expiração de sessão do Power BI."
version: 1.0.0
date: "2026-06-11"
status: "Aprovado"
---

# Especificação Técnica: Limpeza e Robustez do Scraper (Headless & Alertas)

## 1. Contexto & Objetivos
Após a validação da carga de 2026 com o perfil persistente do navegador, o repositório acumulou arquivos temporários e de diagnóstico que precisam ser descartados. Além disso, o script de extração deve ser configurado para rodar headless (ideal para execução em servidores de automação/agendadores de tarefas) e exibir erros amigáveis quando o token de sessão do Power BI expirar.

## 2. Escopo das Alterações

### 2.1 Limpeza do Repositório (Item 1 e Sugestão 1)
- **Descarte de Scripts Temporários**: Remover `projects/Detalhamento-Pecas/debug_pbi.py` e `projects/Detalhamento-Pecas/authenticate.py` (este último foi unificado na pasta global `projects/dashboard-inova-data-export/`).
- **Descarte de Imagens e Planilhas**: Deletar todas as imagens `debug_*.png` da raiz do projeto e as planilhas Excel temporárias `Detalhamento-Pecas-2025.xlsx` e `Detalhamento-Pecas-2026.xlsx`.
- **Atualização do `.gitignore`**: Incluir regras explícitas para ignorar arquivos `debug_*.png`, arquivos `.xlsx` na raiz do projeto e a pasta local `.venv/` ou similares se necessário.

### 2.2 Transição para Headless Estável (Sugestão 2)
- Modificar o parâmetro de inicialização do Playwright em `projects/Detalhamento-Pecas/src/extract.py` para utilizar `headless=True` por padrão.
- Garantir que a chamada de download e cliques do iframe funcione de maneira transparente sem a necessidade de interface gráfica ativa.

### 2.3 Monitoramento e Alerta Amigável de Sessão Expirada (Sugestão 3)
- Adicionar uma verificação no loop de navegação do Playwright em `projects/Detalhamento-Pecas/src/extract.py` para identificar timeout ao carregar a página ou selecionar o relatório.
- Se ocorrer um timeout de carregamento da aba ou do iframe principal, capturar a exceção e retornar um aviso em português claro no console informando que a sessão provavelmente expirou e indicando a execução do script `authenticate.py` unificado.

## 3. Critérios de Aceitação (Testes e Homologação)
1. **Limpeza do Repositório**: `git status` não deve exibir arquivos `.png` or `.xlsx` untracked, nem scripts de debug na raiz.
2. **Headless & Robustez**: A execução de `python run.py --ano 2026` em modo headless deve rodar com sucesso sem abrir a janela do Chromium.
3. **Tratamento de Timeout/Sessão**: Se o script for executado sem cookies ou com cookies inválidos, ele deve levantar uma exceção clara explicando a necessidade de reautenticação.
