# Plano de Ingestão Massiva e Finalização Stout

## Objetivo
Processar os 154 arquivos restantes no diretório `_raw/`, aplicando o padrão de alta fidelidade Stout (frontmatter, proveniência, summary, tags) e garantindo a remoção atômica dos originais pós-destilação.

## Blocos de Execução
1. **Bloco 1: Motores (v1-v6)** - Normalização e consolidação das versões de motores (CEVAP, M3, M4).
2. **Bloco 2: Diagnóstico e Infraestrutura** - Saneamento restante (encoding, bridges, linter, test reports).
3. **Bloco 3: Histórico de Sessões (Restantes)** - Sumarização seletiva das sessões 203+.
4. **Bloco 4: Finalização e Auditoria** - Limpeza de `_raw/`, validação de Grafo e emissão do relatório de integridade.

## Critérios de Qualidade (Alta Fidelidade)
- **Atômico:** Cada arquivo processado é movido para o Vault com metadata completa (base_confidence, provenance, summary <= 200 caracteres).
- **Sem Fallbacks:** Substituição automática de qualquer página genérica de "Fallback" encontrada no processo.
- **Zero-Pending:** A pasta `_raw/` deve terminar vazia.
- **Auditoria:** Relatório final de consistência de links e integridade de frontmatters.

## Validação
- Auditoria pós-ingestão verificando a ausência de arquivos em `_raw/` e a integridade de todos os links criados.
