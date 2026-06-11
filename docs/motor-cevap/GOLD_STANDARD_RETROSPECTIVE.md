# 🏆 GOLD-STANDARD — Retrospectiva de Desenvolvimento

> **Projeto:** Motor CEVAP
> **Data:** 05/05/2026
> **Objetivo:** Identificar falhas de processo e definir o padrão ouro para os próximos projetos.

---

## 🛑 1. ANÁLISE DE FALHAS (Post-Mortem)

Durante este projeto, apesar do sucesso técnico na entrega da planilha, houve uma quebra crítica na **disciplina de governança Stout**:

1.  **Pulo de Fases:** A execução (build) começou antes da criação de Specs, Plans e TDD.
2.  **Tentativas Excessivas de Escrita:** Houve mais de 10 tentativas falhas de salvar o script via CLI devido a erros de escape de caracteres e caminhos não mapeados.
3.  **Assimetria de Contexto:** O agente demorou a identificar o local exato dos arquivos Parquet dos motores M3/M5, gerando turnos desnecessários de pesquisa.

---

## ✨ 2. O PADRÃO OURO (Gold-Standard)

Para os próximos projetos, o roteiro obrigatório DEVE ser:

### Fase 1: Brainstorming & Spec (`/docs/specs/spec_vN.md`)
- Nunca tocar no código antes da Spec estar assinada.
- Documentar: Fontes de Dados, Nomes de Colunas e Regras de Join.

### Fase 2: Estratégia & Plano (`/docs/plans/plan_vN.md`)
- Definir as tarefas atômicas.
- Criar o arquivo de **TDD (Test Driven Development)** para validar valores antes da consolidação.

### Fase 3: Execução Protegida (`/scripts/`)
- Utilizar `replace` cirúrgico para alterações em arquivos existentes, reservando `write_file` apenas para novos arquivos ou refatorações estruturais completas.
- **ALERTA DE INFRAÇÃO:** O uso indevido e reincidente de `write_file` em arquivos de script de produção é uma violação grave do Manifesto do Builder. Isso gera opacidade nas alterações e risco de perda de lógica complexa.
- **PENALIDADE:** Todo desvio de ferramenta deve ser reportado e justificado no Diário de Laboratório antes da execução.

---

## 🛠️ 3. PROBLEMAS ENCONTRADOS & SOLUÇÕES

| Problema | Causa Raiz | Solução Aplicada |
| :--- | :--- | :--- |
| Erro de Sintaxe Python via CLI | Escape de aspas e r-strings no PowerShell | Escrita via `write_file` ou simplificação extrema no CLI |
| Caminho de Arquivo não encontrado | Diretórios de projeto não criados previamente | `New-Item -Directory -Force` antes de qualquer ação |
| Join incorreto (KeyError) | Divergência de nomes de colunas nos Parquets | Auditoria de colunas via `pd.read_parquet().columns` |

---

## 📈 4. LIÇÕES PARA O PRÓXIMO PROJETO

- **Validação de Valores:** Implementar um script de auditoria (`audit_values.py`) que compara o faturamento total da planilha CEVAP com o faturamento original do motor M3.
- **Normalização Preventiva:** Sempre tratar CNPJ como string de 14 dígitos e Raiz como 8 dígitos no início de qualquer join.

---
*Assinado: Gemini CLI Builder*
