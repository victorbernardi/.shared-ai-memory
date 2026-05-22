# 🧠 Especificação: Transição de Identidade BUP (Base Única de Pós-Venda)

**Data:** 2026-05-13
**Autor:** Antigravity (IA)
**Status:** Brainstorming Completo

---

## 1. Objetivo
Consolidar a mudança de nome do projeto de `lista-clientes` para `BUP-base-unica-pós-venda`, garantindo a integridade dos dados, caminhos de ingestão/output e a sincronização com a Memória Global.

## 2. Requisitos

### 2.1. Memória Global (.shared-ai-memory)
- Renomear a pasta de histórico em `.shared-ai-memory\.gemini\history\lista-clientes` para `BUP-base-unica-pós-venda`.
- Renomear a pasta temporária em `.shared-ai-memory\.gemini\tmp\lista-clientes` para `BUP-base-unica-pós-venda`.
- Criar a pasta de documentação ativa em `.shared-ai-memory\docs\active\BUP-base-unica-pós-venda` (se ainda não existir).

### 2.2. Estrutura Local (Projeto)
- Recriar a **Junction** da pasta `docs/` local apontando para o novo diretório em `.shared-ai-memory\docs\active\BUP-base-unica-pós-venda`.

### 2.3. Scripts e Automação
- **consolidate_bup.py**: Validar se há referências remanescentes a "lista-clientes" ou caminhos obsoletos.
- **qa_latest_output.py**: Atualizar o caminho fixo do arquivo de validação para o novo padrão BUP.
- **Scripts de Resgate/Polimento**: Atualizar referências ao antigo `Motor CEVAP` para o diretório atual do projeto (usando caminhos relativos).

### 2.4. Documentação de Governança
- **ANTIGRAVITY.md**: Atualizar `Projeto`, `Hierarquia` e `Junction Configurado`.
- **GEMINI.md**: Atualizar referências ao Script Principal (`consolidate_bup.py`).

## 3. Arquitetura de Caminhos Proposta

| Tipo | Caminho Antigo | Novo Caminho |
|------|----------------|--------------|
| Projeto Local | `.../projects/lista-clientes` | `.../projects/BUP-base-unica-pós-venda` |
| Script Principal | `consolidate_cevap.py` | `consolidate_bup.py` |
| Memória Global (Histórico) | `.shared-ai-memory/.../lista-clientes` | `.shared-ai-memory/.../BUP-base-unica-pós-venda` |
| Docs (Junction) | `docs/` -> `.../docs/lista-clientes` | `docs/` -> `.../docs/active/BUP-base-unica-pós-venda` |

## 4. Plano de Validação
1. **Teste de Junction**: Executar `ls docs` e verificar se lista o conteúdo da memória global.
2. **Teste de Ingestão**: Rodar `python scripts/consolidate_bup.py` e verificar se encontra as bases em `data/`.
3. **Teste de Output**: Confirmar se o arquivo `BUP_POS_VENDA_YYYYMMDD_HHMM.xlsx` é gerado na pasta `data/` local.

---
*Aprovado para fase de Estratégia (/plan).*
