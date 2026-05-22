# Especificação Técnica: Automação de Nomenclatura e Versionamento de PDF

**Data:** 2026-05-13  
**Status:** Validado  
**Projeto:** historico-de-vendas  

---

## 1. Objetivo
Implementar a geração dinâmica de nomes de arquivos para os relatórios PDF, incluindo versionamento (v5) e carimbo de data/hora (timestamp), seguindo o padrão histórico do projeto e eliminando conflitos de permissão de escrita.

## 2. Requisitos de Negócio
- **Rastreabilidade:** Cada execução deve gerar um arquivo único para histórico de revisões.
- **Padronização:** O nome deve seguir o formato `Relatorio_Estrategico_JD_v5_YYYYMMDD_HHMMSS.pdf`.
- **Governança:** Arquivos devem ser salvos em `docs/business/`.

## 3. Mudanças Propostas

### 3.1. Lógica de Nomenclatura
- **Arquivo:** `src/generate_pdf_report_v2.py`
- **Ação:** 
  1. Obter timestamp atual usando `datetime.datetime.now()`.
  2. Formatar string como `YYYYMMDD_HHMMSS`.
  3. Construir o `pdf_path` dinamicamente.

## 4. Plano de Validação
- [ ] Executar o script e verificar se um novo arquivo foi criado em `docs/business/`.
- [ ] Validar se o nome do arquivo contém a data e hora corretas.
- [ ] Confirmar que o script não falha mesmo que uma versão anterior do PDF esteja aberta.

---
**Próximo Passo:** Gerar o Plano de Implementação (Strategy).
