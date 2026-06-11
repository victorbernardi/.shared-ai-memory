# Plano de Implementação - Correção de Travas na Planilha de Leads (v1)

Este plano descreve as alterações necessárias em `src/load.py` e nos testes unitários para garantir que as colunas comerciais ("Retorno do Contato" e "Observações") permaneçam desbloqueadas, mantendo o cabeçalho e as demais colunas protegidos.

## 1. Alterações em `src/load.py`

### 1.1. Desbloquear as colunas inteiras
Para garantir que o Excel trate as colunas O (15) e P (16) como editáveis por padrão (mesmo se novas linhas forem adicionadas ou se os dados forem reinseridos via Power Query), aplicaremos a proteção desbloqueada diretamente nas dimensões de coluna:

```python
    # Antes de salvar e após a definição dos estilos de proteção:
    ws.column_dimensions['O'].protection = unlocked_protection
    ws.column_dimensions['P'].protection = unlocked_protection
```

### 1.2. Proteger as células do cabeçalho
Como as colunas O e P estarão desbloqueadas no nível de dimensão de coluna, as células O1 e P1 herdariam esse comportamento. Devemos forçar que o cabeçalho da linha 1 permaneça bloqueado:

```python
    # No loop de escrita do cabeçalho:
    for col_idx, col_name in enumerate(colunas, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        # ...
        if col_name in ["Retorno do Contato", "Observacoes"]:
            cell.fill = fill_editable_header
            cell.protection = locked_protection  # Garante bloqueio do cabeçalho
```

### 1.3. Ajuste do Loop de Dados
Para evitar que a atribuição posterior de bordas afete a proteção no openpyxl, vamos consolidar as definições de estilo de cada célula de dados de uma vez só:

```python
        # Colunas editáveis (15 e 16) — Amarelo Ouro
        c_retorno = ws.cell(row=row_idx, column=15, value=retorno)
        c_retorno.alignment = align_center
        c_retorno.font = font_editable
        c_retorno.fill = fill_editable_cell
        c_retorno.border = box_border
        c_retorno.protection = unlocked_protection

        c_obs = ws.cell(row=row_idx, column=16, value=obs)
        c_obs.alignment = align_left
        c_obs.font = font_editable
        c_obs.fill = fill_editable_cell
        c_obs.border = box_border
        c_obs.protection = unlocked_protection
```
*(Removendo as atribuições de borda redundantes das linhas 196-197)*

---

## 2. Testes de Regressão em `tests/test_load_consultor.py`

Adicionaremos um teste unitário focado na proteção de células para evitar qualquer regressão futura. O teste fará:
1. Gerará a planilha em um arquivo temporário usando dados mockados.
2. Carregará o workbook gerado usando `openpyxl`.
3. Verificará que a aba está protegida: `assert ws.protection.sheet is True`.
4. Validará que as células de dados de A2 a N2 estão bloqueadas: `assert ws.cell(row=2, column=col_idx).protection.locked is True`.
5. Validará que as células de dados de O2 (15) e P2 (16) estão desbloqueadas: `assert ws.cell(row=2, column=15).protection.locked is False` e `assert ws.cell(row=2, column=16).protection.locked is False`.
6. Validará que os cabeçalhos O1 e P1 estão bloqueados: `assert ws.cell(row=1, column=15).protection.locked is True`.
7. Validará que as colunas inteiras O e P possuem proteção desbloqueada: `assert ws.column_dimensions['O'].protection.locked is False`.

---

## 3. Plano de Testes Manuais
- Executar `pytest tests/test_load_consultor.py` para validar a corretude técnica e lógica.
- Rodar o pipeline principal `run.py` para gerar uma planilha de teste.
- Abrir a planilha gerada em um leitor compatível (Excel ou LibreOffice) e tentar alterar dados nas colunas estruturais (deve falhar) e nas colunas de feedback comercial (deve ser permitido).
