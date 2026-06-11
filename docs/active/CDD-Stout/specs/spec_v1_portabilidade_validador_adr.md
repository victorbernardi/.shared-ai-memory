# 📑 Especificação Técnica: Portabilidade & Resiliência na Validação de ADRs (stout-adr)

> **ID da Especificação:** `spec_v1_portabilidade_validador_adr`
> **Fase:** `/brainstorm` (Pesquisa e Diagnóstico de Sistema)
> **Data:** 2026-05-28
> **Autor:** Gemini Engenheiro de Software / Stout Lab
> **Status:** **READY FOR DEV (Aprovado na Validação CDD)**

---

## 1. Contexto de Negócio & Risco do Sistema

A skill **`stout-adr`** gerencia os Architecture Decision Records (ADRs) do ecossistema Stout Lab, aplicando o padrão estruturado MADR v4 local. Toda decisão importante de design ou alteração de escopo técnico DEVE ser documentada em um arquivo markdown numerado e validada antes de sua consolidação no diretório `docs/decisions/`.

### O Incidente do Sistema
Em ambientes baseados em Windows nativo (sem sub-camadas ativas de Git Bash no PATH global), a execução das rotinas de auditoria, preflight e verificação da skill `stout-adr` quebra fatalmente devido a dependências UNIX acopladas aos scripts de shell Bash.
> *Erro do Sistema:* `in step execution: exec: "grep": executable file not found in %PATH%`

*   **Risco Técnico:** Alto. Paradas e abortos de validação de design em pipelines automatizados de preflight no Windows.
*   **Impacto de Negócios:** Média-Alta. Prejudica a rastreabilidade arquitetural e impede a integridade de commits, pois desenvolvedores ou agentes em computadores Windows nativos não conseguem registrar ou validar ADRs de forma íntegra.

---

## 2. Matriz de Rastreabilidade de Requisitos (SOW ➔ Spec ➔ Teste)

Para garantir que cada Critério de Aceitação de Negócio (AC) esteja mapeado para requisitos funcionais (FR) específicos e validado por cenários de testes (T), estabelecemos a Matriz de Rastreabilidade CDD:

### 2.1 Critérios de Aceitação (SOW)

| ID | Categoria | Descrição do Critério de Aceitação | Sinal Observável (Observable Signal) |
| :--- | :--- | :--- | :--- |
| **AC-1** | `portabilidade` | Portabilidade e Execução Silenciosa em Windows Nativo. | Execução das rotinas de ADR no Windows completa com exit code 0 sem exigir `grep.exe`, `sed.exe` ou `ls` no PATH. |
| **AC-2** | `validacao` | Conformidade Estrutural das ADRs (MADR v4). | O validador rejeita ADRs sem cabeçalho H1 ou com seções H2 mandatórias ausentes, reportando falhas claras no console. |
| **AC-3** | `indexacao` | Atualização Automática de Índices Markdown. | A tabela do índice Markdown de ADRs é atualizada de forma incremental preservando a ordenação sequencial e caracteres acentuados. |

### 2.2 Requisitos Funcionais (Spec)

| ID | Implements | Descrição do Requisito Funcional (SHALL) | Componente Alvo |
| :--- | :--- | :--- | :--- |
| **FR-001** | AC-1, AC-3 | O sistema deve descobrir a lista de ADRs no diretório usando `os.listdir()` e filtrar via expressão regular `r"^\d{4}-"` para identificar ordenação e números sequenciais livres de chamadas de shell `ls`. | `pre_check.py` |
| **FR-002** | AC-1, AC-3 | O sistema deve ler o cabeçalho H1 primário de cada ADR abrindo o arquivo markdown em UTF-8 e capturando a primeira linha iniciada com `# `, descartando dependências de `sed` ou `grep`. | `pre_check.py` |
| **FR-003** | AC-2 | O sistema deve validar a presença das seções obrigatórias MADR v4 (como `## Context and Problem Statement` e `## Decision Outcome`) carregando o texto completo do arquivo e checando a existência das strings correspondentes. | `validate_adr.py` |
| **FR-004** | AC-2 | O sistema deve isolar o bloco do frontmatter e extrair pares chave-valor para validação das tags e metadados requeridos sem pipes ou rotinas do shell do SO. | `validate_adr.py` |
| **FR-005** | AC-3 | O sistema deve gerar e salvar a tabela markdown compilada do índice principal no arquivo `docs/decisions/README.md` forçando codificação UTF-8 rígida. | `update_index.py` |

### 2.3 Cenários de Teste (Coverage)

| ID | References | Descrição do Cenário de Teste Unitário | Critério de Sucesso do Teste |
| :--- | :--- | :--- | :--- |
| **T-001** | FR-003, FR-004 | Teste de Validação Positiva de ADR Válido. | Injeta um arquivo markdown MADR v4 estruturado corretamente; o validador deve retornar sucesso (exit code 0). |
| **T-002** | FR-003 | Teste de Validação Negativa por Seção Mandatória Ausente. | Injeta um markdown sem a seção `## Decision Outcome`; o validador deve rejeitar o arquivo com mensagem descritiva no stderr. |
| **T-003** | FR-001 | Teste de Sequenciamento de Novo ADR com Lacunas. | Cria ADRs numeradas fora de ordem (ex: `0001`, `0003`); a função de cálculo do próximo índice deve computar corretamente o valor `4`. |
| **T-004** | FR-002, FR-005 | Teste de Resiliência de Caracteres Especiais (Unicode). | Lê e processa títulos contendo acentuações e caracteres unicode especiais (como `→` ou `ã`); os dados devem ser gravados sem mojibake ou quebra de encode. |

### 2.4 Requisitos Não-Funcionais (NFR)

| ID | Validates | Descrição do Requisito Não-Funcional (SHALL) | Racional Técnico (Rationale) |
| :--- | :--- | :--- | :--- |
| **NFR-001** | AC-1 | Utilizar apenas bibliotecas embutidas na biblioteca padrão do Python (`os`, `sys`, `re`, `shutil`). | Preserva o sandbox nativo livre de instalações adicionais ou pacotes externos. |
| **NFR-002** | AC-3 | Todas as operações de leitura/escrita de arquivos Markdown devem definir explicitamente o parâmetro `encoding="utf-8"`. | Previne erros fatais de encodificação causados por páginas de código locais legadas (CP1252/Windows). |

---

## 3. Localização das Invocações UNIX Dependentes Legadas

As quebras de sistema no Windows são provocadas por quatro scripts em shell UNIX (`.sh`) localizados sob a pasta de scripts da skill `stout-adr`:

*   **Diretório Alvo:** `C:\Projetos\Stout\Projetos\Configuration-Driven Development\skills\stout-adr\scripts\`
    *   `pre-check.sh`
    *   `update-index.sh`
    *   `validate-adr.sh`
    *   `select-adr-template.sh`

---

## 4. Análise e Equivalência Técnica

### 4.1 Script: `pre-check.sh`
*   **Comando UNIX Legado:**
    ```bash
    MAX_NUM=$(ls "$ADR_DIR" 2>/dev/null | grep -E '^[0-9]{4}-' | sort -r | head -1 | cut -d'-' -f1 || true)
    ```
    *   *Equivalência Python (FR-001):*
        ```python
        import os
        import re
        adr_files = os.listdir(adr_dir)
        num_patterns = [int(f.split("-")[0]) for f in adr_files if re.match(r"^\d{4}-", f)]
        max_num = max(num_patterns) if num_patterns else 0
        ```

### 4.2 Script: `update-index.sh`
*   **Comando UNIX Legado:**
    ```bash
    NUMBER=$(echo "$FILENAME" | grep -oE '^[0-9]{4}')
    ```
    *   *Equivalência Python (FR-001):*
        ```python
        match = re.match(r"^\d{4}", filename)
        number = match.group(0) if match else ""
        ```

### 4.3 Script: `validate-adr.sh`
*   **Comando UNIX Legado:**
    ```bash
    if grep -q "## $section" "$ADR_FILE"; then
    ```
    *   *Equivalência Python (FR-003):*
        ```python
        with open(adr_file, "r", encoding="utf-8") as f:
            has_section = f"## {section}" in f.read()
        ```

---

## 5. Próximos Passos (Transição de Fase)

*   [x] Conclusão da Fase `/brainstorm` com a especificação formalizada e matriz de rastreabilidade CDD validada.
*   [x] Inicialização da Fase `/plan` (`process-writing-plans`) com plano estratégico cross-platform pronto e em **STANDBY MODE** de segurança aguardando aprovação explícita do usuário.

---
*Fim da especificação técnica.*
