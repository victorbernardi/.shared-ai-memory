# Guia de Versionamento — Ecossistema Stout

## Semântica de versões (SemVer)

| Tipo  | Quando usar | Exemplo |
|-------|-------------|---------|
| PATCH | Fix de descrição, trigger, path, typo | 1.0.0 → 1.0.1 |
| MINOR | Novo script, template, exemplo adicionado | 1.0.1 → 1.1.0 |
| MAJOR | Mudança de papel, mudança de interface com outras skills | 1.1.0 → 2.0.0 |

## Regra de ouro
Se a mudança exige que uma skill chamadora mude seu comportamento, é MAJOR.
Em caso de dúvida, suba MINOR.

## Ciclo de vida de uma skill
`draft → beta → active → deprecated`

- **draft**: em desenvolvimento, não usada em produção
- **beta**: funcional mas em validação, pode mudar
- **active**: estável, uso irrestrito no ecossistema
- **deprecated**: substituída ou obsoleta, nunca deletada do registry

## Workflow de atualização segura
1. Melhore a skill com `stout-improve-skill`
2. Bump de versão: `python scripts/register_skill.py --name <nome> --bump-version minor`
3. Teste com os triggers documentados na skill
4. Documente a mudança no campo `notes` do registry

## Categorias permitidas no ecossistema Stout
| Categoria | Descrição |
|-----------|-----------|
| `meta-governance` | Skills que gerenciam o próprio ecossistema |
| `meta-factory` | Skills que criam ou modificam outras skills |
| `data-engineering` | Pipelines, ETL, transformação de dados |
| `notebooklm` | Integração com Google NotebookLM |
| `devops` | Deploy, CI/CD, infraestrutura |
| `writing` | Geração e edição de conteúdo |
| `analysis` | Análise de dados, relatórios, insights |
| `integration` | Conectores com sistemas externos |

## Conflito de papel — como resolver
Se dois papéis parecem iguais, pergunte:
> "Se A mudar, B precisa mudar também?"
Se sim, é o mesmo papel. Se não, são papéis distintos.