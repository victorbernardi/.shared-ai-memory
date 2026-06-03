# Checklist de Migração CDD → ICM

Use este checklist ao converter um projeto legado. Marque cada item conforme avança.

## Pré-Migração

- [ ] Projeto legado identificado (caminho, domínio, skills ativas)
- [ ] Estrutura atual mapeada: skills, scripts, configurações, dependências
- [ ] Fluxo de execução documentado (ordem de carregamento, handoffs implícitos)
- [ ] Número de estágios ICM planejado (um por propósito distinto)

## Estrutura

- [ ] Estágios ICM criados DENTRO do diretório do projeto existente
- [ ] Estágios numerados criados: `01_<estagio>`, `02_<estagio>`, ...
- [ ] Cada estágio tem `CONTEXT.md` com as 8 seções obrigatórias
- [ ] Cada estágio tem `output/`
- [ ] Estágios com scripts têm `scripts/`

## Contratos

- [ ] `CONTEXT.md` do pipeline define ordem e regras globais do workspace
- [ ] Regras globais extraídas do SKILL.md original → CONTEXT.md do pipeline
- [ ] Restrições operacionais → CONTEXT.md do estágio específico
- [ ] Nenhuma seção vazia ou placeholder em nenhum CONTEXT.md

## Scripts

- [ ] Scripts copiados (não movidos) para `scripts/` do estágio correto
- [ ] Encoding UTF-8 verificado em todos os scripts
- [ ] Permissão de execução garantida (chmod +x ou equivalente)
- [ ] Scripts originais preservados no local antigo

## Envelope

- [ ] `SKILL.md` fino criado na raiz do workspace
- [ ] YAML frontmatter contém `name` e `description` com triggers semânticos
- [ ] Corpo do SKILL.md tem no máximo 10 linhas (só apontadores)
- [ ] Description contém palavras-chave que correspondem ao uso original

## Roteamento

- [ ] Entrada adicionada em `data/config/skills_catalog.yaml`
- [ ] Campos obrigatórios: `status: migrated`, `icm_workspace`, `legacy_skill: archived`
- [ ] SKILL.md original atualizado com aviso de arquivamento
- [ ] Aviso de arquivamento visível no topo do arquivo (antes do frontmatter)

## Validação Pós-Migração

- [ ] Pipeline ICM executado do início ao fim sem erros
- [ ] Outputs equivalentes aos do fluxo original
- [ ] Nenhum script quebrou (testado isoladamente)
- [ ] Agente descobre o workspace via `SKILL.md` fino
- [ ] Skill original ainda funciona se invocada diretamente
