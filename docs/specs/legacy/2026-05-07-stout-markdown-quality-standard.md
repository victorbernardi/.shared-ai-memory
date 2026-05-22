# Spec: Padrão de Qualidade Markdown no Stout (PDP)

> **Versão:** v1
> **Data:** 2026-05-07
> **Status:** Aprovado (Brainstorming concluído)
> **Autor:** Victor + Antigravity

---

## 1. Objetivo

Garantir que **todo projeto futuro** do ecossistema Inova/Stout nasça com infraestrutura de qualidade de Markdown pronta para uso, eliminando documentação de baixa qualidade que prejudica a ingestão por sistemas de IA (RAG) e gera retrabalho.

## 2. Requisitos Funcionais

### RF-01: Template `.markdownlint.json` na Golden Copy

- Criar diretório `C:\Motores-LLM\gemini-cli\antigravity\templates\markdown-quality\`.
- Incluir arquivo `.markdownlint.json` com configuração IA-Focused:
  - **Ativas:** MD001, MD003 (atx), MD009, MD012, MD022, MD024, MD025, MD032, MD034, MD036, MD040, MD051.
  - **Desativadas:** MD013 (line length), MD033 (HTML inline), MD041 (first line H1).

### RF-02: Script `md-sanitize.py` genérico

- Criar script reutilizável com as seguintes interfaces CLI:
  - `--init` → Copia `.markdownlint.json` da Golden Copy para o projeto atual.
  - `--fix <arquivo.md>` → Aplica sanitização automática em um arquivo.
  - `--fix-all` → Aplica sanitização em todos os `.md` recursivamente.
  - `--check <arquivo.md>` → Modo dry-run (mostra correções sem aplicar).
- Lógica central baseada no `sanitize_content` validado neste projeto:
  - Offset de hierarquia de cabeçalhos (MD001).
  - Espaçamento ao redor de headings e listas (MD022/MD032).
  - Proteção de bare URLs (MD034).
  - Conversão de ênfase-como-título para heading semântico (MD036).
  - Linguagem em fenced code blocks (MD040).
  - Limpeza de linhas em branco excessivas (MD012).

### RF-03: Modificação da skill `stout-init`

- Adicionar **Fase 2.5: Markdown Quality Setup** ao pipeline de scaffolding.
- Instruções agnósticas de ferramenta (funciona em Gemini CLI e Antigravity).
- Copiar 3 arquivos da Golden Copy para o projeto:
  1. `.markdownlint.json` → raiz do projeto.
  2. `md-sanitize.py` → `scripts/`.
  3. `requirements-md.txt` → raiz do projeto.
- Atualizar checklist de validação (Fase 8).
- Adicionar Regra de Ouro #9: *"Documentação de baixa qualidade é falha técnica."*

### RF-04: Retrofit de projetos existentes

- O comando `python scripts/md-sanitize.py --init` copia o `.markdownlint.json` da Golden Copy para o projeto atual.
- Alternativa manual: `copy` direto do path da Golden Copy.

## 3. Requisitos Não-Funcionais

### RNF-01: Compatibilidade

- O script deve funcionar com Python 3.10+.
- Dependências leves permitidas (`mdformat>=0.7`), listadas em `requirements-md.txt`.
- Compatível com Gemini CLI e Antigravity (mesmos paths, ferramentas diferentes).

### RNF-02: Isolamento

- Todo projeto é auto-contido após o scaffolding.
- Nenhuma dependência em runtime da Golden Copy (apenas no momento da cópia).

### RNF-03: Manutenção

- A Golden Copy é a fonte de verdade única.
- Atualizações no `.markdownlint.json` mestre se propagam apenas para projetos novos.
- Projetos existentes atualizam sob demanda via `--init`.

## 4. Arquitetura

### Golden Copy (Fonte de Verdade)

```
C:\Motores-LLM\gemini-cli\antigravity\
└── templates/
    └── markdown-quality/
        ├── .markdownlint.json
        ├── md-sanitize.py
        └── requirements-md.txt
```

### Projeto Scaffolded (Destino)

```
[NomeProjeto]/
├── .markdownlint.json          ← copiado da Golden Copy
├── requirements-md.txt         ← copiado da Golden Copy
├── scripts/
│   └── md-sanitize.py          ← copiado da Golden Copy
└── ... (estrutura Stout padrão)
```

### Fluxo de Execução

```
stout-init (Fase 2.5)
    │
    ├── Lê templates/markdown-quality/.markdownlint.json
    │   └── Copia para ./
    │
    ├── Lê templates/markdown-quality/md-sanitize.py
    │   └── Copia para ./scripts/
    │
    └── Lê templates/markdown-quality/requirements-md.txt
        └── Copia para ./
```

## 5. Validação (Plano de Testes)

### Teste 1: Template JSON válido

- Verificar que `.markdownlint.json` é um JSON parseável.
- Confirmar presença das regras IA-Critical (MD001, MD024, MD025, MD040).
- Confirmar ausência das regras cosméticas (MD013, MD033, MD041).

### Teste 2: Script de Sanitização

- Criar arquivo `.md` propositalmente "sujo" (sem espaçamento, bare URLs, code blocks sem linguagem).
- Executar `md-sanitize.py --check` e confirmar que todas as violações são listadas.
- Executar `md-sanitize.py --fix` e confirmar que o arquivo resultante tem zero warnings.

### Teste 3: Integração com stout-init

- Simular scaffolding completo de um projeto novo.
- Verificar que os 3 novos arquivos existem nos paths corretos.
- Verificar que o `.markdownlint.json` copiado é idêntico ao da Golden Copy.

### Teste 4: Retrofit

- Em um projeto existente (sem config), executar `md-sanitize.py --init`.
- Confirmar que `.markdownlint.json` aparece na raiz.

## 6. Decision Log

| # | Decisão | Alternativas | Motivo |
|---|---|---|---|
| 1 | Escopo Preventivo (Scaffolding) | Reativo (Gate), Ambos | YAGNI — gate pode ser futuro |
| 2 | Config IA-Focused | Rigoroso, Progressivo | Equilíbrio qualidade/pragmatismo |
| 3 | Dependências leves | Zero-dependency | mdformat agrega valor real |
| 4 | Golden Copy como fonte única | Embutido na skill, Ambos | Evita drift |
| 5 | Direct Copy | Dinâmico, Self-Bootstrap | Previsível, cross-environment |
| 6 | Flag --init para retrofit | Comando manual | UX unificada |

## 7. Riscos

| Risco | Mitigação |
|---|---|
| Golden Copy deletada/corrompida | Backup via Git do diretório `C:\Motores-LLM\` |
| Script falha em edge cases de Markdown | Modo `--check` (dry-run) antes de `--fix` |
| Modificação da `stout-init` quebra projetos | Protocolo `canary-deployment` obrigatório |

---

*Spec gerada via brainstorming — sessão 45acb747*
