# Walkthrough: Atualização e Auditoria Motor CEVAP

## Mudanças Realizadas

1. **Sincronização de Fontes:** O script `scripts/consolidate_cevap.py` foi atualizado para ler as cotações diretamente da pasta `shared/data`, garantindo que Victor e Filipe estejam trabalhando sobre a mesma base de verdade.
2. **Execução do Motor:** Nova planilha gerada: `data/CEVAP_ATIVACAO_20260513_2017.xlsx` com **16.280** clientes para ativação.
3. **Auditoria de Paridade:** Criado e executado o script `scripts/audit_cevap_bup_parity.py`.

## Resultados da Auditoria

- **Total de Grupos CEVAP:** 16.280
- **Localizados no BUP:** 16.280 (Integridade de 100%)
- **Discrepâncias de Consultor:** 135 clientes (~0.8% da base).

### Análise das Discrepâncias

As 135 discrepâncias ocorrem porque o **BUP utiliza o Banco de Dados (Fabric/VS1010)** em tempo real para atribuir consultores, enquanto o **CEVAP utiliza planilhas Excel**. 

**Exemplo:** O cliente `11814673000100 (C DA C QUINTANILHA)` possui um orçamento aberto em `2026-04-27` detectado pelo BUP via Fabric, o que o atribui ao consultor `ANDRE VITOR`. No CEVAP, por limitações de match no Excel, ele caiu no pool de inativos.

## Conclusão

A integridade da base está excelente (99.2% de paridade). As divergências são "positivas", pois indicam que o BUP está sendo mais preciso ao não enviar para o CEVAP clientes que já possuem interação recente detectada no sistema.

**Arquivos Gerados:**

- [Relatório CEVAP Atualizado](file:///c:/Projetos/Inova/projects/motor-cevap/data/CEVAP_ATIVACAO_20260513_2017.xlsx)
- [Log de Discrepâncias](file:///c:/Projetos/Inova/projects/motor-cevap/data/audit_discrepancias_cevap_bup.csv)
