# Sessão 205 — 2026-05-20
**Slug:**  | **Duração:** ~52min | **Modelo:** 

## Tópicos
- 02_Faturamento — Filtros whitelist + CBIT remap lockdown

## Decisões
- Whitelist substitui blacklist para COD_GRUPO, FILIAL, DESCRICAO_CC. BI e fonte da verdade — tudo que nao esta no BI e removido ou reclassificado como Balcao. LEIC removido: produtos no Fabric (MSC/MMB/KIT) sao diferentes dos codigos no BI. Filiais 0302-0304 removidas: sem dados reais no BI.

## Tarefas Pendentes
- [ ] Investigar JDPC -R$3.77M (imposto filial 203). Investigar EPRC +R$0.68M. Investigar BI grupos NaN R$1.74M. Investigar Balcao delta +/-1.9%. Deploy query para producao apos resolucao das pendencias. (prioridade: medium)

## Arquivos Modificados
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\scratch_read_results.py` — write_to_file
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\docs\\specs\\EMAIL_ENTREGA_CAMPANHA_UBERLANDIA.md` — write_to_file
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\src\\main_campanha_uberlandia.py` — replace_file_content
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\skills\\internal-comms\\examples\\campanha-comms.md` — write_to_file
- `c:\\Projetos\\Inova\\projects\\campanha-lubrificantes-uberlandia-2026\\skills\\internal-comms\\SKILL.md` — replace_file_content

## Descobertas
- RESUMO: Implementacao de whitelists COD_GRUPO (27), FILIAL (02xx+0301), DESCRICAO_CC (24). Remapeamento CBIT no snapshot (3 produtos). Remocao LEIC, filiais 0302-0304, CCs EPIROC/VALLEY. Balcao via CASE WHEN. Delta ex-CBIT +0.53%. 24/24 testes passam.

## Métricas
- Input tokens: 0
- Output tokens: 0
- Cache tokens: 0
- Mensagens: 72
- Tool calls: 55

---
*Sessão anterior: [session-204](session-204.md)*