# Plano de Implementação - Planilha Desbloqueada com Validação de Dados (v2)

Este plano detalha a transição do modelo de proteção de planilha para o modelo de restrições puras por validação de dados em `src/load.py`.

## 1. Alterações em `src/load.py`

### 1.1. Remoção da Proteção da Planilha
Eliminar as seguintes linhas no final da função `exportar_planilha_leads` que ativavam a trava de segurança geral:

```diff
-    # Aplicar Protecao com Senha corporativa
-    ws.protection.sheet = True
-    ws.protection.password = "InovaPosVendas2026"
-    ws.protection.autoFilter = False # FALSE no openpyxl significa "NAO BLOQUEAR" (permitir) o AutoFilter!
-    ws.protection.sort = False       # FALSE significa "NAO BLOQUEAR" (permitir) ordenacao
-    ws.protection.enable()
```

### 1.2. Remoção do Bloqueio de Células no Loop de Dados
As propriedades `.protection = unlocked_protection` e `.protection = locked_protection` aplicadas nas colunas estruturais e editáveis devem ser removidas, pois a planilha inteira estará livre de proteção.

```diff
-    # Protecao
-    locked_protection = Protection(locked=True)
-    unlocked_protection = Protection(locked=False)
```

No loop de dados, remover a atribuição das travas:
```diff
-        c_retorno.protection = unlocked_protection
-        c_obs.protection = unlocked_protection
         
         # ...
-        for col_idx in range(1, 15):
-            cell = ws.cell(row=row_idx, column=col_idx)
-            if col_idx != 11:
-                cell.font = font_body
-            cell.border = box_border
-            cell.protection = locked_protection
```
E reescrever o loop para aplicar apenas a fonte e a borda:
```python
        # Aplicar fonte, borda e alinhamento básico às colunas estruturais (1-14)
        for col_idx in range(1, 15):
            cell = ws.cell(row=row_idx, column=col_idx)
            if col_idx != 11:
                cell.font = font_body
            cell.border = box_border
```

### 1.3. Adição da Validação de Dados de Texto para Observações
Manter a validação do dropdown na coluna O e adicionar uma validação de comprimento de texto na coluna P:

```python
    # Dropdown na coluna O (Retorno do Contato — col 15)
    if row_idx > 2:
        dv_retorno = DataValidation(
            type="list",
            formula1='"Venda,Venda Perdida,Sem Contato"',
            allow_blank=True
        )
        dv_retorno.errorTitle = "Entrada Invalida"
        dv_retorno.error = "Selecione apenas as opcoes da lista: Venda, Venda Perdida ou Sem Contato."
        dv_retorno.showErrorMessage = True
        ws.add_data_validation(dv_retorno)
        dv_retorno.add(f"O2:O{row_idx-1}")
        
        # Limitação de até 250 caracteres na coluna P (Observacoes — col 16)
        dv_obs = DataValidation(
            type="textLength",
            operator="lessThanOrEqual",
            formula1=250,
            allow_blank=True
        )
        dv_obs.errorTitle = "Texto Muito Longo"
        dv_obs.error = "A observacao deve ter no maximo 250 caracteres."
        dv_obs.showErrorMessage = True
        ws.add_data_validation(dv_obs)
        dv_obs.add(f"P2:P{row_idx-1}")
```

---

## 2. Ajustes nos Testes (`tests/test_load_consultor.py`)

Substituir testes de proteção por asserções de validação de dados:
- Verificar que a folha não tem proteção ativada.
- Verificar que existem dois objetos de `DataValidation` associados à planilha.
- Garantir que as fórmulas de validação (valores do dropdown e operador de comprimento de texto `<= 250`) estejam configuradas corretamente.
