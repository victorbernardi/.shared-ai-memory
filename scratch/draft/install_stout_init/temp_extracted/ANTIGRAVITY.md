# 🧠 ANTIGRAVITY.md - Kernel Agêntico

> **Ambiente:** Antigravity (Custom Gemini Environment)
> **Propósito:** Controlar o comportamento operacional do agente em modo autônomo
> **NÃO confundir com GEMINI.md** — este arquivo é específico do ecossistema Antigravity

---

## 1. ARQUITETURA DE MEMÓRIA

O Antigravity opera com uma arquitetura de memória distribuída via junctions:

### Hierarquia de Pastas
```
C:\Projetos\Stout\
├── antigravity\
│   └── skills\                    # Skills e referências técnicas
│       └── process-superantigravity\
│           └── references\
│               └── gemini-tools.md   # 📄 Bíblia de ferramentas
├── memory\
│   └── context-agent\
│       ├── sessions\              # Sessões ativas
│       └── projects\              # Memória persistente por projeto
└── [Projeto Ativo]\
    ├── ANTIGRAVITY.md              # Este arquivo (Kernel)
    ├── GEMINI.md                   # Contexto de negócio (herdado do Plano Executivo)
    └── docs/ -> junction           # Link para memory/context-agent/projects/[ID]/
```

### Regras de Junction
- `docs/` no projeto é um **junction** para `C:\Projetos\Stout\memory\context-agent\projects\[ID]\`
- Nunca mover arquivos manualmente entre caminhos lógicos e físicos
- Sempre usar caminhos absolutos nas ferramentas

---

## 2. FERRAMENTAS DO AMBIENTE ANTIGRAVITY

Você possui as seguintes ferramentas customizadas validadas:

| Ferramenta | Status | Uso |
|-----------|--------|-----|
| `view_file` | ✅ Funcional | Leitura de arquivos (alias de read_file) |
| `write_to_file` | ✅ Funcional | Escrita total de arquivos |
| `replace_file_content` | ✅ Funcional | Edição in-place de conteúdo |
| `grep_search` | ✅ Funcional | Busca de texto em arquivos |
| `run_command` | ✅ Funcional | Execução de comandos shell |

**Referência completa:** `C:\Users\victor.bernardi\.antigravity\skills\process-superantigravity\references\gemini-tools.md`

---

## 3. FRAMEWORK STOUT (Antigravity Edition)

Pipeline de execução para operações autônomas:

### Fase 1: RESEARCH
- Use `grep_search` para mapear arquivos e padrões
- Use `view_file` para leitura profunda de alvos identificados
- Documentar descobertas na seção State Tracking abaixo

### Fase 2: STRATEGY
- Formular plano modular baseado nos dados reais encontrados
- Validar alinhamento com KPIs do projeto (ver GEMINI.md local)
- Documentar estratégia na seção State Tracking

### Fase 3: EXECUTION
- Aplicar soluções usando `write_to_file` ou `replace_file_content`
- Preferir `replace_file_content` para edições precisas (menor risco)
- Documentar progresso na seção State Tracking

### Fase 4: VALIDATION
- Verificar resultado com `view_file`
- Executar testes via `run_command` quando aplicável
- Atualizar status de conclusão

---

## 4. STATE TRACKING (Memória Ativa)

> **ATENÇÃO:** Atualize esta seção via `replace_file_content` ao final de cada ciclo STOUT para evitar degradação de contexto.

### 🛠️ Status do Framework STOUT
- [ ] **Research:** [Documentar descobertas iniciais, arquivos chave, limitações]
- [ ] **Strategy:** [Plano de ação técnico, etapas de execução]
- [ ] **Execution:** [Progresso das tarefas, o que ficou pendente]
- [ ] **Validation:** [Resultados dos testes, confirmação de sucesso]

### 📝 Notas de Contexto Recentes
- *Adicione variáveis, caminhos importantes, nuances de dados descobertas*

---

## 5. DIRETRIZES DE SEGURANÇA

- Sempre confirmar caminhos absolutos antes de `write_to_file`
- Nunca executar `run_command` com comandos destrutivos sem validação
- Credenciais sempre via variáveis de ambiente, nunca hardcoded
- Backup automático antes de operações de replace em arquivos críticos

---

## 6. INTEGRAÇÃO COM GEMINI.md

Este arquivo (ANTIGRAVITY.md) controla **COMO** o agente opera tecnicamente.
O GEMINI.md (local ou global) controla **O QUÊ** o agente deve construir e **POR QUÊ**.

- ANTIGRAVITY.md = Motor/Kernel
- GEMINI.md = Mapa/Destino

Nunca misturar instruções técnicas de ferramentas (Antigravity) com instruções de negócio (Gemini).
