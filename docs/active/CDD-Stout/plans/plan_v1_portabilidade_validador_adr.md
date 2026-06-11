# 🚀 Plano de Implementação: Portabilidade & Resiliência na Validação de ADRs (stout-adr)

> **ID do Plano:** `plan_v1_portabilidade_validador_adr`
> **Fase:** `/plan` (Estratégia Técnica)
> **Data:** 2026-05-28
> **Autor:** Gemini Engenheiro de Software / Stout Lab
> **Status:** **STANDBY (Aguardando Aprovação Humana)**

---

## 1. Objetivo e Escopo

Substituir de forma definitiva os scripts em Bash dependentes de comandos UNIX (`grep`, `sed`, `ls`, `head`, `cut`) na skill **`stout-adr`** por rotinas equivalentes em Python nativo 3.10+ built-in (com encoding UTF-8 forçado). A migração sanará as quebras catastróficas em computadores Windows puros e garantirá a conformidade multiplataforma de registro e auditoria das Architecture Decision Records (ADRs).

---

## 2. Estrutura de Alterações de Arquivos

Mapeamento de arquivos criados, alterados e removidos na skill local `skills/stout-adr/` com os respectivos vínculos de requisitos CDD:

### [NEW] [pre_check.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/scripts/pre_check.py)
*   **Vínculo:** `FR-001` (Listagem robusta de arquivos), `FR-002` (Leitura de H1).
*   *Lógica:* Varrer a pasta de decisões `docs/decisions/` listando arquivos via regex `r"^\d{4}-"`, retornando o maior número sequencial para o próximo ADR e capturando títulos `# ` de arquivos sem erros de CP1252.

### [NEW] [update_index.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/scripts/update_index.py)
*   **Vínculo:** `FR-001` (Listagem robusta de arquivos), `FR-005` (Geração do README em UTF-8).
*   *Lógica:* Extrair os números e nomes de arquivos markdown de decisões arquiteturais, gerando dinamicamente a tabela do índice Markdown e atualizando o arquivo de índice principal em UTF-8.

### [NEW] [validate_adr.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/scripts/validate_adr.py)
*   **Vínculo:** `FR-003` (Validação de Blocos H2), `FR-004` (Extração de Frontmatter).
*   *Lógica:* Validar a existência do título H1 inicial, a presença das seções H2 requeridas no padrão MADR v4, e a integridade de chaves do frontmatter de metadados sem dependência de pipes do shell.

### [NEW] [select_adr_template.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/scripts/select_adr_template.py)
*   **Vínculo:** `NFR-001` (Sem dependências externas).
*   *Lógica:* Cópia segura e cross-platform de arquivos de template markdowns de decisões.

### [MODIFY] [SKILL.md](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/SKILL.md)
*   **Vínculo:** `AC-1` (Execução Silenciosa no Windows).
*   *Lógica:* Atualizar todas as definições e instruções operacionais de execução de ferramentas agênticas de `sh scripts/validate-adr.sh` para `python scripts/validate_adr.py`.

### [DELETE] [pre-check.sh](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/scripts/pre-check.sh)
### [DELETE] [update-index.sh](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/scripts/update-index.sh)
### [DELETE] [validate-adr.sh](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/scripts/validate-adr.sh)
### [DELETE] [select-adr-template.sh](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/skills/stout-adr/scripts/select-adr-template.sh)
*   Exclusão dos scripts UNIX originais legados.

---

## 3. Plano de Verificação e Cobertura de Testes

Criaremos testes unitários offline no repositório local do motor de testes em `tests/` para validar a estabilidade cross-platform e garantir não-regressão:

1.  **Caso T-001 (Validação Positiva):**
    Testar que um ADR estruturado válido passa no novo `validate_adr.py` com exit code 0.
2.  **Caso T-002 (Validação Negativa - Seção Ausente):**
    Testar que a ausência de seções H2 mandatórias gera rejeição do arquivo e mensagens descritivas no stderr.
3.  **Caso T-003 (Sequenciamento robusto com lacunas):**
    Testar que se houver arquivos com numeração descontínua (ex: `0001` e `0003`), a descoberta computa corretamente `0004` para o próximo registro.
4.  **Caso T-004 (Resiliência de Encodings e Unicode):**
    Validar que títulos contendo acentuações e caracteres unicode especiais (como `→` ou `ã`) são tratados e impressos sem Mojibake ou erros de página de código.
5.  **Caso NFR-001 / NFR-002 (Compliance de Portabilidade):**
    Validar que nenhuma biblioteca externa do `pip` é importada na execução e todas as rotinas explicitam `encoding="utf-8"` em leituras e escritas.

---

## 4. Trava de Segurança & Próximos Passos

> [!IMPORTANT]
> **STANDBY MODE ATIVO:** Nenhuma alteração física ou exclusão de scripts Bash legados foi efetuada. Respeitando incondicionalmente a nossa governança, aguardamos o seu veredito e aprovação humana explícita deste plano de portabilidade antes de entramos na Fase de Execução (`/build`).

---
*Fim do plano de implementação.*
