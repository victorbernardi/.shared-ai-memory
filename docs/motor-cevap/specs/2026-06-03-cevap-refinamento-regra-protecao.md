---
spec: cevap-refinamento-regra-protecao
date: 2026-06-03
status: aprovado
author: Victor Bernardi
---

# Spec: Refinamento de Regra CEVAP + Proteção de Planilha

## Objetivo

Três melhorias independentes no pipeline CEVAP:

1. Refinar a regra de orçamento no BUP para exigir data ≥ 2026
2. Remover colunas desnecessárias do relatório operacional
3. Proteger a planilha com edição restrita às colunas do consultor

## Arquitetura (Decisão Confirmada)

O CEVAP é um escoamento do BUP: `df_bup[df_bup["Consultor"] == "CEVAP"]`.
Qualquer mudança de regra de classificação ocorre **exclusivamente no BUP**.
O CEVAP herda automaticamente via o output pré-classificado.

---

## Requisitos Funcionais

### RF-01: Regra de Orçamento com Filtro de Ano

**Arquivo:** `BUP/scripts/status_consultor.py`

Regra atual:

- `orc_aberto = "ABERTO" in status_orc` → qualquer data

Nova regra:

- `orc_aberto = "ABERTO" in status_orc AND data_ultimo_orc.year >= 2026`
- Orçamentos abertos anteriores a 2026 **não** evitam classificação como CEVAP
- Regra dos 90 dias de inatividade: **inalterada**

Assinatura nova da função:

```python
def calcular_status_e_consultor(
    dias_inativo_ativo: int,
    consultor_venda: str | None,
    status_orc: str,
    consultor_orc: str | None,
    dias_ultimo_orc: int = 999,
    data_ultimo_orc=None,   # novo: date | None
) -> tuple[str, str]:
```

**Arquivo:** `BUP/scripts/consolidate_bup.py`

Passar `data_orc` (objeto `date`, não apenas `dias`) para `calcular_status_e_consultor`:

```python
data_orc = row.get("Data_Ultimo_Orcamento")
status, consultor = calcular_status_e_consultor(
    ...,
    data_ultimo_orc=data_orc if pd.notnull(data_orc) else None,
)
```

### RF-02: Remoção de Colunas no CEVAP

**Arquivo:** `motor-cevap/scripts/consolidate_cevap.py`

Colunas a remover do output final:

- `Telefones`
- `E-mail`
- `Valor_12m`
- `Status_Conflito`
- `Status_Ultimo_Orcamento`
- `Potencial_Grupo`

### RF-03: Proteção da Planilha com openpyxl

**Arquivo:** `motor-cevap/scripts/consolidate_cevap.py`

Após `df_final.to_excel(output_path, index=False)`, pós-processar com openpyxl:

1. **Autofilter:** todas as colunas da linha 1
2. **Proteção de sheet:** senha `PecasInova2026`, `sheet=True`
3. **Células bloqueadas por padrão:** todas
4. **Células editáveis (unlock):** todas as células das colunas abaixo (excluindo cabeçalho):
   - `Data_Tentativa_1`
   - `Status_Contato_1`
   - `Data_Tentativa_2`
   - `Status_Contato_2`
   - `Observacao`
5. **Dropdowns (DataValidation):** colunas `Status_Contato_1` e `Status_Contato_2`
   - Opções: `Pendente`, `Venda`, `Não Venda`
   - Aplicar em todas as linhas de dados (linha 2 até última linha)

A proteção deve ser aplicada tanto no arquivo local (`data/CEVAP_ATIVACAO_YYYYMMDD_HHMM.xlsx`) quanto na cópia OneDrive.

---

## Requisitos Não-Funcionais

- Retrocompatibilidade: BUP continua gerando todas as colunas (remoção só no CEVAP)
- Orçamentos de anos anteriores a 2026 que estavam classificando clientes como CONVERSÃO passam a ser CEVAP após a mudança
- Senha hardcoded no script (não é segredo operacional — é proteção de UX contra edição acidental)

---

## Plano de Validação

1. Após mudança no BUP: rodar `python -m pytest tests/` — todos os testes devem passar
2. Verificar no output BUP que clientes com orçamento aberto de 2025 estão agora como `CEVAP`
3. Verificar no output CEVAP que as 6 colunas não aparecem
4. Abrir planilha CEVAP no Excel: confirmar que apenas as 5 colunas editáveis aceitam edição
5. Confirmar dropdowns em `Status_Contato_1` e `Status_Contato_2`

---

## Decision Log

| Decisão | Alternativa considerada | Motivo |
|---|---|---|
| Regra de orçamento com filtro de ano no BUP | Filtrar no CEVAP | Fonte única de verdade; CEVAP é escoamento |
| Passar `data_ultimo_orc` como `date` | Passar só o ano | Mais flexível para futuras regras temporais |
| Senha hardcoded no script | Variável de ambiente | Proteção de UX, não de segurança |
| 3 opções no dropdown (Pendente/Venda/Não Venda) | 2 opções | Manter `Pendente` como estado inicial existente |
