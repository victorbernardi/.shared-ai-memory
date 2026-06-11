# Spec: hot.md — Hot Cache de Sessão

**Data:** 2026-04-19  
**Autor:** Victor Bernardi  
**Status:** Aprovado

---

## Objetivo

Criar um arquivo `wiki/hot.md` gerado automaticamente ao fim de cada sessão de trabalho, contendo ~500 palavras com o contexto imediato: o que foi feito, próximos passos e erros a evitar. O arquivo serve de cache de curto prazo para retomada de sessão sem precisar varrer notas da wiki.

---

## Componentes

### 1. `generate_hot_cache(summary, wiki_dir)` — `session_summary.py`

Novo método responsável por:
1. Montar um prompt estruturado com os campos do `SessionSummary`:
   - `topics` — tópicos da sessão
   - `tasks_completed` — tarefas concluídas
   - `files_modified` — arquivos modificados
   - `errors_resolved` — erros resolvidos
   - `tasks_pending` — próximas tarefas
2. Chamar `gemini -p "<prompt>"` em modo headless via `subprocess.run`
3. Capturar stdout e escrever em `wiki_dir/hot.md`
4. Timeout: 30 segundos
5. Falha silenciosa: log de aviso, não interrompe o `save`

**Assinatura:**
```python
def generate_hot_cache(summary: SessionSummary, wiki_dir: Path) -> bool:
    """
    Gera wiki/hot.md via Gemini CLI headless.
    Retorna True se bem-sucedido, False se falhou (best-effort).
    """
```

### 2. `cmd_save` — `context_manager.py`

Adicionar **passo 13** ao final da função `cmd_save`, após o trigger do Wiki Compiler:

```python
# 13. Gerar hot cache (best-effort)
try:
    wiki_dir = Path("C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki")
    success = generate_hot_cache(summary, wiki_dir)
    if success:
        print("  hot.md atualizado")
    else:
        print("  AVISO: hot.md não gerado (Gemini indisponível)")
except Exception as e:
    print(f"  AVISO: Falha ao gerar hot.md: {e}")
```

O `wiki_dir` deve ser lido da variável de ambiente `OBSIDIAN_WIKI_DIR` com fallback para o path hardcoded, seguindo o padrão já existente no arquivo.

### 3. `SESSION_START.md` — protocolo de início de sessão

Adicionar passo 1.5 entre o load do context-agent e o briefing:

```
1.5. Se wiki/hot.md existir → ler e incluir no briefing como "Contexto Imediato"
```

---

## Estrutura do hot.md gerado

```markdown
# Hot Cache — YYYY-MM-DD

## O que foi feito
[resumo das tarefas concluídas e mudanças da última sessão]

## Próximos passos
[itens pendentes + ações recomendadas para a próxima sessão]

## Erros a evitar
[padrões de erro registrados — omitir seção se não houver erros]
```

---

## Prompt enviado ao Gemini

```
Você é um assistente que gera um arquivo hot.md (hot cache) para retomada de sessão de trabalho com IA.
Com base nos dados da sessão abaixo, gere um resumo em português em até 500 palavras com 3 seções:

## O que foi feito
## Próximos passos
## Erros a evitar

Se não houver erros, omita a seção "Erros a evitar".
Responda SOMENTE com o conteúdo markdown (sem bloco de código, sem explicações adicionais).
Comece com: # Hot Cache — {data}

---
Tópicos: {topics}
Tarefas concluídas: {tasks_completed}
Arquivos modificados: {files_modified}
Erros resolvidos: {errors_resolved}
Próximas tarefas: {tasks_pending}
```

---

## Variáveis de Ambiente

| Variável | Descrição | Fallback |
|---|---|---|
| `OBSIDIAN_WIKI_DIR` | Caminho da pasta `wiki/` | `C:/Users/victor.bernardi/Documents/Obsidian-Victor-Global/wiki` |

---

## Comportamento em Falha

- Gemini indisponível → aviso no stdout, `hot.md` não é criado/atualizado, `save` continua normalmente
- Timeout (30s) → mesmo comportamento
- `wiki_dir` não existe → mesmo comportamento
- Hot.md anterior é **sobrescrito** a cada `save` bem-sucedido (não é histórico)

---

## Fora de Escopo

- Hot cache não alimenta o Wiki Compiler (não vai para `_pending/`)
- Hot cache não é versionado via git (arquivo local apenas)
- Hot cache não é gerado pelo Wiki Compiler — apenas pelo context-agent

---

## Testes

- `test_generate_hot_cache_success` — mock do subprocess, verifica que `hot.md` é criado com as 3 seções
- `test_generate_hot_cache_gemini_unavailable` — subprocess lança exceção, verifica que retorna `False` sem crashar
- `test_generate_hot_cache_timeout` — subprocess timeout, verifica comportamento gracioso
