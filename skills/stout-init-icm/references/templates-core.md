# Templates de Inicialização ICM

## Template: SKILL.md (Envelope Fino)

```yaml
---
name: <nome-do-projeto>
description: "<Descrição semântica com triggers. Quando usar, palavras-chave.>"
---

# Regras globais: ..\..\GEMINI.md (Regras 1-9, Karpathy Laws)
#                ..\..\CLAUDE.md (princípios de código)
# Caminhos canônicos: ..\..\REFERENCES.md
# Contrato do pipeline: CONTEXT.md (este diretório)
```

Os caminhos `..\..\` sobem do projeto (`Projetos\<projeto>\`) até a raiz do domínio (Stout ou Inova).

## Template: CONTEXT.md (Pipeline)

```markdown
---
pipeline: <nome-do-projeto>
layer: 2
role: pipeline_contract
stages: [<estagio1>, <estagio2>, ...]
---

# CONTEXT.md — Pipeline: <Nome>

## Ordem dos Estágios

| Ordem | Estágio | Propósito |
|-------|---------|-----------|
| 1 | `01_<estagio1>/` | <propósito em uma frase> |
| 2 | `02_<estagio2>/` | <propósito em uma frase> |

## Regras do Pipeline

- **NUNCA** pule estágios. A ordem numérica é absoluta.
- **NUNCA** avance para o próximo estágio sem que o atual atinja todos os critérios de conclusão.
- **SEMPRE** consuma o output do estágio anterior como input do próximo.
- **NUNCA** propague artefatos incompletos entre estágios.
- **SEMPRE** carregue `..\..\GEMINI.md` (Regras 1-9) e `..\..\REFERENCES.md` (caminhos canônicos) antes de iniciar.
- **Se o domínio NÃO tem REFERENCES.md:** usar `src/config.py` como fallback.

## Handoff Final

Após aprovação no último estágio, os artefatos são consolidados e disponíveis para arquivamento.
```

## Template: SKILL.md — Fallback para Domínio sem Infra

```yaml
---
name: <nome-do-projeto>
description: "<Descrição semântica com triggers.>"
---

# Regras: ./GEMINI.md (já existe no projeto)
#         ./CLAUDE.md (já existe no projeto)
# Caminhos: src/config.py (fallback até REFERENCES.md ser criado na raiz do domínio)
# Pipeline: CONTEXT.md (este diretório)
```

Usar quando o domínio ainda não tiver `REFERENCES.md` nem `.GCC/`.

## Template: CONTEXT.md — Estágio 00 (Research / Cold Storage)

```markdown
---
stage: 00_research
layer: 2
role: stage_contract
inputs_from: [operator_curation]
outputs_to: [todos_os_estagios]
---

# CONTEXT.md — Estágio 00: Research (Cold Storage)

## 1. Propósito do Estágio
Fornecer fundamentação teórica e referências para os estágios operacionais. 
Cold storage — nunca carregado automaticamente.

## 2. Insumos (Inputs)
- **Pesquisas curadas:** `references/*.md`

## 3. Tarefa e Processo
### 3.1 Organização
- Agrupar pesquisas por tema em `references/`

### 3.2 Disponibilização
- Estágios operacionais referenciam arquivos específicos sob demanda

## 4. Restrições
- **NUNCA** carregar todo o conteúdo deste diretório de uma vez
- **SEMPRE** referenciar arquivos individuais sob demanda

## 5. Artefatos de Saída
| Artefato | Localização | Formato | Critério de Aceitação |
|----------|-------------|---------|----------------------|
| Referências organizadas | `references/` | Markdown | Arquivos indexados por nome |

## 6. Critérios de Conclusão
1. Pesquisas organizadas em `references/`

## 7. Handoff
- Estágios operacionais consomem arquivos específicos sob demanda

## 8. Em Caso de Falha
- Se arquivo referenciado não existe: sinalizar ao operador

## Template: CONTEXT.md (Estágio)

```markdown
---
stage: <NÚMERO>_<nome-do-estagio>
layer: 2
role: stage_contract
inputs_from: [<estágio_anterior>]
outputs_to: [<próximo_estágio>]
---

# CONTEXT.md — Contrato do Estágio <XX>: <Nome>

## 1. Propósito do Estágio
<Uma frase. Se precisar de duas, divida em dois estágios.>

## 2. Insumos (Inputs)
- **<Fonte>:** <caminho concreto>

## 3. Tarefa e Processo
### 3.1 <Sub-etapa>
- <Ação específica>

## 4. Restrições
- **<CONSTRAINT>:** <detalhe>
- **Idempotência:** <como garantir>

## 5. Artefatos de Saída
| Artefato | Localização | Formato | Critério de Aceitação |
|----------|-------------|---------|----------------------|
| <nome>   | `output/`   | Markdown | <condição binária> |

## 6. Critérios de Conclusão
1. <Condição binária>

## 7. Handoff
- Output → próximo estágio

## 8. Em Caso de Falha
1. Documentar em `output/error_log.md`
2. NUNCA propagar artefatos incompletos
```

## Template: GEMINI.md (com Regras 1-9)

Consultar `@templates/gemini-icm.md` para o template completo com Regras 1-9 incluindo navegação ICM.
