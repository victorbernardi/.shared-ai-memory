# 🛡️ Registro de Qualidade de Dados (DQR) - Motor M6

Este documento registra falhas de dados identificadas e as correções implementadas para evitar que erros conhecidos retornem ao sistema.

---

## 🛑 Histórico de Erros e Soluções

### 1. Corrupção de Código de Filial (Float Conversion)
*   **Data de Identificação:** 2026-04-29
*   **Sintoma:** Filiais aparecendo como `FILIAL 201.0` ou `FILIAL 0nan`.
*   **Causa Raiz:** O Excel/CSV lida com códigos numéricos como floats. Ao converter para string, o pandas adiciona `.0`.
*   **Correção:** Implementada conversão forçada via `astype(int)` antes do `astype(str).str.zfill(4)`.
*   **Status:** ✅ RESOLVIDO (Wave 7.2)

### 2. Duplicidade Semântica (Transacional)
*   **Data de Identificação:** 2026-04-29
*   **Sintoma:** 14.7% de duplicados no `ydata-profiling`.
*   **Causa Raiz:** Omissão de `ID_TRANSACAO` e `PRODUTO` na exportação final, causando colapso de múltiplas vendas idênticas em uma só.
*   **Correção:** Adição de chaves de auditoria na camada transacional.
*   **Status:** ✅ RESOLVIDO (Wave 7.2)

### 3. Filtro de Depósito Fechado (0205)
*   **Data de Identificação:** 2026-04-28
*   **Sintoma:** Inflação de faturamento com transferências internas.
*   **Causa Raiz:** Movimentações na filial 0205 não devem compor o BI de vendas.
*   **Correção:** Filtro global aplicado no orquestrador.
*   **Status:** ✅ RESOLVIDO (Wave 7.1)

---

## 📈 Próximas Auditorias Planejadas
- [ ] Validação de Clientes com CNPJ inválido (zfill 14).
- [ ] Checagem de Centros de Custo não mapeados (Segmento: Peças e acessórios).
