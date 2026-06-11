# Detalhamento de Peças — Especificação Técnica com Perfil Persistente

**Data:** 2026-06-11  
**Versão:** 2.0  
**Status:** Aprovado  
**Autor:** Antigravity (Brainstorming Stout)

---

## 1. Objetivo

Aprimorar o scraper de extração do relatório "Detalhamento de Vendas" do Power BI (página "Detalhamento Peças") para solucionar a expiração frequente de sessões e simplificar a rotina de carga de 2026. As principais diretrizes são:

- **Autenticação:** Utilização de Contexto de Navegador Persistente (`launch_persistent_context`) do Playwright em diretório compartilhado.
- **Carga de 2026:** Substituição completa (carga acumulada de 01/01/2026 a hoje a cada rodada), sem tratamento incremental no Python.
- **Carga de 2025:** Mantém-se imutável (carga histórica de 01/01/2025 a 31/12/2025).

---

## 2. Requisitos

### 2.1 Requisitos Funcionais

| ID | Requisito | Critério de Aceitação |
|----|-----------|-----------------------|
| RF-1 | Carga total de 2025 | Execução fixa de 01/01/2025 a 31/12/2025 salvando em `detalhamento_vendas_2025.parquet` |
| RF-2 | Carga total e atualizada de 2026 | Execução sempre de 01/01/2026 até hoje salvando e sobrescrevendo `detalhamento_vendas_2026.parquet` |
| RF-3 | Limpar metadata do Power BI | Remover linhas finais (Total, vazias, filtros aplicados) a partir da ausência de Nota Fiscal |
| RF-4 | Validação de variação (Threshold) | Bloquear salvamento se a variação do total do novo ano consolidado de 2026 em relação ao parquet anterior for superior a 10% (evita salvar arquivos corrompidos ou vazios) |
| RF-5 | Login Centralizado e Persistente | Gerar cookies e sessões nativamente em um diretório físico compartilhado para estender a validade indefinidamente |

### 2.2 Requisitos Não-Funcionais

| ID | Requisito | Valor/Descrição |
|----|-----------|-----------------|
| NF-1 | Local de Perfil Persistente | Diretório físico `projects/dashboard-inova-data-export/browser_state/user_profile` |
| NF-2 | Headless vs. Headed | `headless=False` na autenticação (`authenticate.py`) e `headless=True` no scraper de produção (`run.py` / `extract.py`) |
| NF-3 | Limite de Exportação | Volume de 2026 estimado abaixo de 150k registros (limite padrão do Power BI) para permitir carga total |
| NF-4 | Timeout e Tolerância | Timeout de 120s na carga de páginas, com retry automático de 3 tentativas |

---

## 3. Arquitetura e Estrutura de Pastas

### 3.1 Diretório Compartilhado de Sessão
```
projects/
├── dashboard-inova-data-export/
│   ├── browser_state/
│   │   └── user_profile/            ← [Perfil de usuário persistente do Chromium]
│   └── authenticate.py               ← [Gera login inicial abrindo a pasta de perfil]
└── Detalhamento-Pecas/
    ├── src/
    │   ├── config.py                 ← [Aponta BROWSER_STATE para o diretório compartilhado acima]
    │   ├── extract.py                ← [Carrega perfil em modo headless]
    │   └── transform.py              ← [Limpa metadados]
    └── run.py                        ← [Orquestra carga de 2025 ou 2026 acumulado]
```

### 3.2 Fluxo de Dados e Autenticação
1. **Autenticação Interativa (`authenticate.py`):**
   Abre a pasta `user_profile` no modo visível. O usuário faz o login, e o Chromium grava os cookies nativamente em disco.
2. **Scraper Headless (`run.py`):**
   Abre o Chromium headless usando a mesma pasta `user_profile`. O Power BI reconhece a sessão ativa. A navegação bem-sucedida atualiza os cookies de sessão de volta no disco, mantendo a autenticação ativa.

---

## 4. Plano de Validação e Testes

### 4.1 Testes Unitários e Locais
* **Validação de Schema:** Verificar se a estrutura de colunas do DataFrame extraído possui `'Nota Fiscal'`, `'Data Emissão'` e `'CNPJ'`.
* **Teste do Scraper (Headless):** Executar em modo headless e assegurar que o navegador acessa o relatório e encontra os elementos do Power BI sem requerer login interativo.
* **Teste do Threshold:** Verificar que a extração falha e o parquet não é modificado caso ocorra uma queda brusca (vazio ou perda > 10% de dados).

### 4.2 Testes Manuais (E2E)
1. **Geração de Perfil:** Executar `authenticate.py`, efetuar login e garantir que a pasta `user_profile/` é preenchida.
2. **Carga Completa 2026:** Executar `python run.py --ano 2026`. Validar a criação do parquet `detalhamento_vendas_2026.parquet` e conferir a soma do Valor Líquido com o Power BI.
3. **Carga Repetida 2026:** Executar o script no dia seguinte e validar que o parquet é atualizado por inteiro, mantendo a sessão do navegador ativa sem nova intervenção humana.
