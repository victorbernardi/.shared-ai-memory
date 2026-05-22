# Exemplos de Sobreposição — Referência Rápida

## Exemplos de APROVAÇÃO (score < 40%)

| Proposta | Existente | Por que aprova |
|----------|-----------|----------------|
| "Transcrever áudio com Whisper" | stout-create-skill | Domínios completamente diferentes |
| "Monitorar custos de modelos LLM" | stout-skill-registry | Papéis não relacionados |
| "Gerar relatório PDF de pipeline" | stout-data-pipeline | Saída ≠ processo |

## Exemplos de QUESTIONAR (score 40–80%)

| Proposta | Existente | Score | Por que questionar |
|----------|-----------|-------|--------------------|
| "Importar PDFs no NotebookLM" | stout-notebooklm-ingest | 65% | Cobre parte do domínio |
| "Validar scripts de skill" | stout-skill-auditor | 55% | Auditor já checa scripts de forma geral |
| "Criar template de skill de dados" | stout-create-skill | 70% | Overlap com templates de criação existentes |

## Exemplos de REJEIÇÃO (score > 80%)

| Proposta | Existente | Score | Por que rejeita |
|----------|-----------|-------|-----------------|
| "Registrar nova skill no ecosistema" | stout-skill-registry | 95% | Função idêntica |
| "Fazer scaffolding de nova skill" | stout-create-skill | 88% | Mesma responsabilidade (Fábrica) |
| "Checar ambiguidade entre skills" | stout-skill-auditor | 91% | Papel duplicado |

## Regra prática
Se você consegue descrever a proposta usando o nome da skill existente sem perder o significado da ação, é REJEIÇÃO.
> "Quero criar uma skill que **registre skills no ecossistema**"
> → stout-skill-registry já faz isso → REJEIÇÃO