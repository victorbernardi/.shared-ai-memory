# Plano de Ingestão Atômica (Cleanup Wiki)

## 1. Estratégia de Processamento
- Ingestão em blocos lógicos por tema (Identidade, Motores, Segmentação, Auditoria, Sessões).
- Deduplicação ativa: comparar arquivos v1/v2/v3 e manter apenas o mais recente, consolidando pendências.
- Destilação Padrão Stout:
  - Título
  - Categoria (concepts, projects, specs, walkthroughs)
  - Tags
  - Summary (<= 200 chars)
  - Base Confidence
  - Lifecycle
  - Provenance
- Deleção: Uso de `Remove-Item` via `run_shell_command` após sucesso.

## 2. Ordem de Execução
1. Consolidação de identidades e motores (Stout v2, Inova, Motores).
2. Segmentação e filtros (v1 a v6).
3. Auditorias e Match Rate (M2, M3, M4, M5).
4. Sessões e Logs (limpeza final).

## 3. Critérios de Sucesso
- `_raw/` vazio.
- Arquivos destilados no Vault principal.
- Deduplicação completa confirmada.
