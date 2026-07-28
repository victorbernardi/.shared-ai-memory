---
name: superpowers-update
version: 1.0.0
tier: 2
category: meta-governance
description: Use when checking or updating installed Superpowers skills against obra/superpowers main, especially after a public repository change or when local skills may be stale.
triggers:
  - superpowers-update
  - atualizar superpowers
  - sincronizar skills
  - skills modificadas
  - obra main
tools:
  - python
  - git
  - filesystem
author: Victor
---

# Superpowers Update

Sincroniza as skills locais usando `https://github.com/obra/superpowers.git`, branch `main`, como fonte da verdade.

## Uso

Execute a partir deste diretório:

```powershell
python scripts/superpowers_update.py check
python scripts/superpowers_update.py apply
```

`check` baixa uma cópia temporária, compara todas as pastas públicas `skills/<nome>` que possuem `SKILL.md` e informa skills novas, modificadas, iguais, skills locais extras e arquivos extras. `apply` repete a verificação e atualiza somente as skills divergentes. Uma skill local que não existe na fonte não é presumida como removida, pois pode ser uma skill própria do ecossistema.

## Garantias

- Diferenças CRLF/LF são ignoradas; qualquer outra diferença é considerada.
- Os destinos padrão são `.shared-ai-memory\skills`, `.agents\skills`, `.codex\skills`, `.claude\skills` e `.commandcode\skills` dentro da home do usuário.
- Arquivos extras locais nunca são apagados.
- Skills locais fora da fonte pública são reportadas como `extra_skills`, não como divergências a atualizar.
- A operação usa backup temporário, rollback em falha e verificação pós-cópia.
- Sem diferenças, `apply` retorna `NO_OP` e não grava arquivos.
- O relatório só é persistido quando `--report CAMINHO` é informado; o relatório interno fica em um diretório temporário removido ao final.
- A skill não faz commit, push, merge, reset, clean ou exclusão de branches.

Para destinos adicionais, repita `--target PATH`. `--source-root PATH` existe para testes offline e deve apontar para uma raiz que contenha `skills/`; no uso normal, a fonte pública é clonada automaticamente.

## Instalação

A skill deve permanecer no catálogo canônico `skills/superpowers-update`. A propagação para `.agents\skills`, `.codex\skills`, `.claude\skills` e `.commandcode\skills` deve usar o instalador global do ecossistema. Não edite cópias instaladas como fonte.

## Governança

O repositório público `obra/superpowers/main` é a autoridade. A skill faz apenas comparação e cópia seletiva; não publica alterações no Git, não remove extras e não cria relatórios persistentes sem solicitação explícita. Falhas interrompem a operação e restauram os destinos já processados.

## Referências

- Fonte: `https://github.com/obra/superpowers/tree/main`
- Design: `docs/superpowers/specs/2026-07-28-superpowers-update-design.md`
- Plano: `docs/superpowers/plans/2026-07-28-superpowers-update.md`
