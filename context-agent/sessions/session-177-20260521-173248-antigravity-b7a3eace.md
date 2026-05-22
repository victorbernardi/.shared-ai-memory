# Sessão 177 — 2026-05-20
**Slug:**  | **Duração:** ~52min | **Modelo:** 

## Tópicos
- BUP-AUTO-1: Extração de Orçamentos via Fabric

## Tarefas Pendentes
- [ ] BUP-AUTO-1: Implementar extract_orcamentos.py consultando VS1010 no Fabric para gerar os xlsx de orçamentos abertos e cancelados, eliminando dependência do PowerBI. (prioridade: medium)

## Arquivos Modificados
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\scratch_read_results.py` — write_to_file
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\docs\\specs\\EMAIL_ENTREGA_CAMPANHA_UBERLANDIA.md` — write_to_file
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\src\\main_campanha_uberlandia.py` — replace_file_content
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\skills\\internal-comms\\examples\\campanha-comms.md` — write_to_file
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\skills\\internal-comms\\SKILL.md` — replace_file_content

## Descobertas
- RESUMO: Pendência registrada: substituir exportação manual do PowerBI por script Python que consulta a VS1010 direto no Fabric, gerando tabela_orçamentos_abertos.xlsx e tabela_orçamentos_cancelados.xlsx em shared/data/. Plano detalhado em docs/plans/2026-05-16-bup-auto-1-extrair-orcamentos-fabric.md. Requer exploração dos campos de status/motivo da VS1010 antes da implementação.

## Métricas
- Input tokens: 0
- Output tokens: 0
- Cache tokens: 0
- Mensagens: 72
- Tool calls: 55

---
*Sessão anterior: [session-176](session-176.md)*