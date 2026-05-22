# 📐 Spec: Interface CLI SEO_GE (Maestro v11.7)

**Data:** 2026-05-11
**Status:** DRAFT
**Contexto:** Evolução do Motor Identidade para permitir consultas rápidas e auditorias seguras no ambiente Gemini CLI.

---

## 1. OBJETIVO
Criar uma interface de linha de comando que permita investigar o ecossistema de grupos econômicos sem depender de inputs interativos (input()), garantindo compatibilidade total com o Gemini CLI e automações.

## 2. REQUISITOS TÉCNICOS (GEMINI-FRIENDLY)
- **Non-Blocking:** Proibido uso de prompts interativos no fluxo padrão.
- **Flags Explícitas:** Todas as ações (WELD, DISCARD, AUDIT) devem ser acessíveis via argumentos de linha de comando.
- **Output Estruturado:** Logs claros com separadores visuais para facilitar a leitura do Agente e do Usuário.
- **Modo Batch:** Suporte para processar múltiplos pares de auditoria em um único comando.

## 3. ARQUITETURA DE COMANDOS

O script central será o scripts/seo_ge_cli.py (ou evolução do scanner.py), com os seguintes modos:

### 3.1 Busca e Diagnóstico (--busca)
Exibe os integrantes do grupo e sugere elos potenciais.
`ash
python scripts/seo_ge_cli.py --busca "NOME OU CNPJ"
`

### 3.2 Auditoria Automática (--audit)
Realiza o Deep Dive multidimensional entre dois IDs e sugere um veredito.
`ash
python scripts/seo_ge_cli.py --a ID_A --b ID_B --audit
`

### 3.3 Registro de Decisão (--decide)
Persiste uma decisão na Knowledge Base.
`ash
python scripts/seo_ge_cli.py --a ID_A --b ID_B --decide WELD --reason "Motivo..."
`

## 4. LAYOUT VISUAL (ANSI/TEXT)
- **Cores:** Uso moderado de cores (via colorama ou similar) para destacar Scores.
- **Tabelas:** Uso de tabulate ou formatação manual de strings para exibir os integrantes.

---

## 5. PLANO DE IMPLEMENTAÇÃO
1.  **Refatoração:** Migrar a lógica interativa do `seo_ge_scanner.py` para um core de funções puras.
2.  **CLI Wrapper:** Criar o `seo_ge_cli.py` utilizando `argparse` robusto.
3.  **Validation:** Testar todos os comandos via Gemini CLI para garantir que não há `hangs`.
