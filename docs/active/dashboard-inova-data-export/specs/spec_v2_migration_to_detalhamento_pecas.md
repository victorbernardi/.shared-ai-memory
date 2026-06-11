# 📋 Especificação Técnica: Migração e Estruturação ICM - Detalhamento Peças

> **Versão:** v2.0.0  
> **Status:** Em Brainstorming / Validação  
> **Data:** 2026-06-02  
> **Autor:** Gemini CLI (Engenheiro de Software)  
> **Origem:** C:\Projetos\Inova\projects\dashboard-inova-data-export  
> **Destino:** C:\Projetos\Inova\projects\Detalhamento-Pecas  

---

## 1. Contexto & Motivação de Negócio

Para garantir a modularidade e a escalabilidade das operações pós-venda, os robôs de exportação do Power BI Embedded devem ser separados por projetos e domínios. A pasta original `dashboard-inova-data-export` será re-utilizada para outros painéis. 

Esta especificação define o processo de migração e a estruturação do projeto **"Detalhamento-Pecas"** utilizando a arquitetura de **Pipeline ICM (Estágios Numerados)** nativa do ecossistema Stout.

- **KPI Impactado:** Modularidade (100% de separação de código por página do Power BI) e conformidade de governança técnica.

---

## 2. Arquitetura de Estágios ICM (Detalhamento-Pecas)

O novo projeto será decomposto de forma procedural nos seguintes estágios sequenciais:

```text
C:\Projetos\Inova\projects\Detalhamento-Pecas\
├── 00_research/        # Cold storage de referências, HTML e screenshots de iFrame
├── 01_export/          # Script Playwright de navegação, aplicação de filtros e download
└── 02_audit/           # Validação física de tamanho, data e integridade do Excel gerado
```

### Contratos e Responsabilidades:

#### 📊 Estágio 00_research:
- **Propósito:** Armazenar os snapshots, referências de classes de acessibilidade e HTML do iFrame interno do Power BI.
- **Entrada:** N/A (Manual/Agente)
- **Saída:** Arquivo `iframe_detalhamento_content.html`, `detalhamento_pecas.png`.

#### 🚀 Estágio 01_export:
- **Propósito:** Executar o robô de navegação Playwright, aplicar os filtros de data (`1/1/2025` a `1/31/2025`) e baixar a planilha.
- **Entrada:** Cookies ativos em `browser_state/state.json`.
- **Saída:** Arquivo Excel exportado.

#### 🛡️ Estágio 02_audit (GATE):
- **Propósito:** Auditar as propriedades físicas do Excel exportado (existência, tamanho > 0 bytes, data de modificação recente).
- **Entrada:** Arquivo gerado em `C:\Projetos\Inova\shared\data\detalhamento_vendas_jan_2025.xlsx`.
- **Saída:** Relatório `audit_status.json` com `passed: true/false`.

---

## 3. Mapeamento de Arquivos a Mover

| Arquivo Origem (dashboard-inova-data-export) | Destino (Detalhamento-Pecas) | Ação |
|---------------------------------------------|------------------------------|------|
| `src/01_login.py` | `src/login.py` | Copiar (Utilidade comum de sessão) |
| `src/07_export_sales.py` | `01_export/scripts/export_sales.py` | Mover & Refatorar |
| `src/config.py` | `src/config.py` | Copiar |
| `browser_state/state.json` | `browser_state/state.json` | Copiar (Preservar cookies ativos) |
| `scratch/check_final_file.py` | `02_audit/scripts/audit_file.py` | Mover & Adaptar para gerar JSON |
| `docs/specs/spec_v1_...md` | `00_research/references/spec_v1.md` | Mover (Histórico) |
| `docs/plans/plan_v1_...md` | `00_research/references/plan_v1.md` | Mover (Histórico) |
| `notes/failure-log.md` | `notes/failure-log.md` | Copiar & Limpar antigos |
| `requirements.txt` | `requirements.txt` | Copiar |

---

## 4. Plano de Limpeza do Projeto Origem

Após a conclusão da cópia e verificação de funcionamento do novo projeto `Detalhamento-Pecas`:
1. Os arquivos `src/07_export_sales.py`, `docs/specs/spec_v1_...` e `docs/plans/plan_v1_...` serão **removidos** da pasta `dashboard-inova-data-export` para evitar poluição visual e lógica.
2. Adicionar uma linha de histórico de migração no `failure-log.md` e `GEMINI.md` de origem.

---

## 5. Critérios de Aceitação da Migração

1. A pasta `Detalhamento-Pecas` deve possuir todos os estágios ICM (00, 01, 02) criados com seus respectivos arquivos `CONTEXT.md` de contrato.
2. O script de exportação em `01_export/scripts/export_sales.py` deve rodar de forma independente e com sucesso.
3. O script de auditoria em `02_audit/scripts/audit_file.py` deve validar o output e passar com sucesso.
4. Os arquivos originais de vendas devem ser removidos do projeto `dashboard-inova-data-export`.
