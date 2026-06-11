# Spec: Registro de Data de Entrada no CEVAP

**Data:** 2026-06-09  
**Status:** Aprovado  
**Projeto:** BUP-base-unica-pós-venda

---

## Objetivo

Registrar a data em que cada grupo econômico entrou pela primeira vez no CEVAP durante o ciclo atual, sem poluir a planilha operacional `BUP_POS_VENDA.xlsx`. Essa data serve como âncora temporal para cálculo de aging no `generate_cevap_kpis.py`.

---

## Requisitos Funcionais

1. O arquivo `data/logs/cevap_entrada_dates.json` é criado na primeira execução e atualizado a cada run do `consolidate_bup.py`
2. Chave: `CNPJ_Grupo` (8 dígitos, zero-padded); Valor: data ISO `YYYY-MM-DD`
3. **Novo no CEVAP:** entrada criada com a data da execução atual
4. **Já no CEVAP:** data original preservada (não sobrescrita)
5. **Saiu do CEVAP:** entrada removida do JSON
6. **Re-entrada:** como a entrada foi removida na saída, a re-entrada gera uma nova data — cada ciclo no CEVAP é independente
7. A planilha `BUP_POS_VENDA.xlsx` não contém nenhuma coluna relacionada a esta feature

## Requisitos Não-Funcionais

- Falha na leitura ou escrita do JSON é não-bloqueante — o pipeline continua com aviso no console
- CNPJs já chegam normalizados pelo pipeline upstream; sem revalidação necessária aqui
- Único escritor: `consolidate_bup.py`
- Leitores atuais: `generate_cevap_kpis.py` (a ser implementado no item 3)

---

## Arquitetura

### Arquivo de estado

```
data/logs/cevap_entrada_dates.json
```

```json
{
  "12345678": "2026-06-09",
  "98765432": "2026-05-15"
}
```

### Fluxo dentro de `consolidate_bup.py`

**Leitura — início de `run_consolidation()`:**

```python
cevap_log_path = DATA_DIR / "logs" / "cevap_entrada_dates.json"
cevap_entrada = {}
try:
    if cevap_log_path.exists():
        with open(cevap_log_path, "r", encoding="utf-8") as f:
            cevap_entrada = json.load(f)
except (json.JSONDecodeError, OSError) as e:
    print(f"AVISO: cevap_entrada_dates.json ilegível, iniciando do zero: {e}")
    cevap_entrada = {}
```

**Atualização — após `df_final` pronto, antes do export:**

```python
grupos_cevap_atual = set(
    df_final[df_final["Consultor"] == "CEVAP"]["CNPJ_Grupo"].dropna()
)
hoje_str = hoje.date().isoformat()

cevap_entrada = {
    g: cevap_entrada.get(g, hoje_str)
    for g in grupos_cevap_atual
}

try:
    with open(cevap_log_path, "w", encoding="utf-8") as f:
        json.dump(cevap_entrada, f, indent=2, ensure_ascii=False)
except OSError as e:
    print(f"AVISO: Não foi possível salvar cevap_entrada_dates.json: {e}")
```

### Reversões necessárias em `consolidate_bup.py`

| Localização | Ação |
|---|---|
| `cols_feedback` | Remover `"Data_Entrada_BUP"` |
| Bloco `_get_data_entrada_bup` | Remover inteiro |
| `cols_finais` | Remover `"Data_Entrada_BUP"` |
| `cols_data_leitura` | Remover `"Data_Entrada_BUP"` |

### Reversões necessárias em `test_bup_output_invariants.py`

| Teste | Ação |
|---|---|
| `test_data_entrada_bup_cevap_sempre_preenchida` | Remover |
| `test_data_entrada_bup_nao_cevap_sempre_vazia` | Remover |

---

## Validação — Plano de Testes

**Arquivo:** `tests/test_cevap_entrada_dates.py`

| Caso | Setup | Esperado |
|---|---|---|
| Novo CEVAP | grupo ausente do JSON | entrada criada com data de hoje |
| CEVAP existente | grupo presente no JSON com data anterior | data original preservada |
| Saiu do CEVAP | grupo no JSON mas fora do conjunto CEVAP atual | entrada removida |
| JSON corrompido | arquivo com conteúdo inválido | fallback para dict vazio, sem exceção |
| Primeira execução | arquivo inexistente | JSON criado do zero sem erro |

---

## Decision Log

| Decisão | Alternativas consideradas | Motivo da escolha |
|---|---|---|
| JSON em `data/logs/` | `data/config/`, `data/` | Dado de estado de execução, não configuração nem output |
| Chave = `CNPJ_Grupo` (8 dígitos) | `CNPJ_Cliente` (14 dígitos) | A filial campeã pode mudar entre runs; a chave de grupo é estável |
| Ciclos independentes (re-entrada = nova data) | Preservar data original mesmo após saída | Cada ciclo CEVAP é distinto; misturar ciclos distorceria o aging |
| Falha não-bloqueante | Falha bloqueante | O JSON é auxiliar; não justifica parar a geração da planilha |
| Feature fora da planilha BUP | Coluna `Data_Entrada_BUP` no output | Planilha operacional não deve carregar dados de estado do motor |
