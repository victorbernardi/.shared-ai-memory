# 📄 Especificação Técnica: Implementação de Travas de Segurança, Ordenação e Validação Restrita do Dropdown BUP

> **ID da Spec:** 2026-06-03-spec-travas-seguranca-v2  
> **Status:** Em Revisão (Aguardando Aprovação Humana)  
> **Data:** 2026-06-03  
> **Autor:** Antigravity (Engenheiro de Software Inova/Stout)  
> **Contexto:** Ajustes nos filtros de segurança, permitindo ordenação com células bloqueadas, restrição estrita no dropdown de status comercial e proteção contra seleção/cópia de células bloqueadas.

---

## 1. Problemas Identificados e Objetivos

Nesta especificação, abordamos três deficiências identificadas nas travas atuais da planilha do BUP:
1. **Dropdown Sem Bloqueio Estrito:** O dropdown de `Status_Contato_1` e `Status_Contato_2` permite atualmente que o usuário digite textos arbitrários ao invés de limitar rigidamente a escolha às opções permitidas (`Pendente`, `Venda`, `Não Venda`).
2. **Cópia e Seleção Livres de Células Bloqueadas:** O bloqueio por macros VBA pode falhar ou ser ignorado (ex: macros desabilitadas ou Excel Online). Precisamos de uma barreira nativa que impeça a seleção física de células trancadas (impedindo assim o Ctrl+C/Ctrl+V).
3. **Impossibilidade de Ordenação:** Por padrão, o Excel bloqueia a ordenação de tabelas que contenham qualquer célula bloqueada, mesmo que a propriedade `Sort` esteja ativada na proteção. Precisamos permitir que os consultores filtrem e ordenem os dados de forma transparente, sem desproteger a planilha ou permitir alteração direta dos dados estruturais.

---

## 2. Requisitos de Negócio e Funcionais

### RF-01: Validação Estrita de Status (Dropdown)
* As colunas `Status_Contato_1` e `Status_Contato_2` devem aceitar **apenas** os valores oficiais: `Pendente`, `Venda`, `Não Venda`.
* O Excel deve rejeitar qualquer digitação arbitrária exibindo uma caixa de erro informativa do tipo "Parar" (Stop).

### RF-02: Impedimento Nativo de Seleção e Cópia (Sem Depender de VBA)
* Ao proteger a planilha com a senha `PecasInova2026`, o atributo `selectLockedCells` deve ser desativado (`False`).
* Os usuários estarão fisicamente impedidos de selecionar qualquer célula bloqueada (CNPJ, Razão Social, Faturamento, etc.), eliminando a possibilidade de seleção e cópia (Ctrl+C).
* Os usuários continuarão livres para selecionar e digitar nas células desbloqueadas (colunas de feedback, destacadas em laranja).

### RF-03: Permissão de Ordenação e Autofiltro via `AllowEditRanges`
* Toda a região de dados (de `A2` até a última linha e coluna da planilha) deve ser mapeada para um intervalo de edição autorizado (`AllowEditRange`) chamado `"DadosBUP"`, protegido sob a mesma senha `PecasInova2026`.
* O range de edição será adicionado via automação COM (`win32com`) na conversão para `.xlsm`.
* Como o range de edição cobre toda a tabela, o Excel permitirá que as macros e ferramentas nativas de **Ordenação** (Sort) e **Filtros** organizem os dados livremente.
* Como a senha do range é `PecasInova2026`, o usuário comum (que não conhece a senha) continuará impedido de editar células bloqueadas, mas poderá ordená-las normalmente.

---

## 3. Arquitetura e Detalhes de Implementação

### Modificações no `scripts/consolidate_bup.py`

#### A. Ajuste na Validação de Dropdowns (openpyxl)
No método `_aplicar_protecao_excel`, configurar a validação com erro restrito:
```python
dv = DataValidation(
    type="list",
    formula1=opcoes,
    allow_blank=True,
    showErrorMessage=True,
    errorTitle="Valor inválido",
    error="Selecione um status válido da lista: Pendente, Venda ou Não Venda.",
    errorStyle="stop"
)
```

#### B. Bloqueio de Seleção de Células Bloqueadas (openpyxl)
No método `_aplicar_protecao_excel`, desativar a seleção das células bloqueadas:
```python
ws.protection.selectLockedCells = False
ws.protection.selectUnlockedCells = True
```

#### C. Injeção de `AllowEditRanges` e Proteção Avançada via COM (win32com)
No método `_converter_para_xlsm`, após abrir o arquivo `.xlsm`, configurar o range e a proteção estendida:
```python
ws = wb.ActiveSheet

# 1. Desproteger folha para manipulação dos ranges
ws.Unprotect("PecasInova2026")

# 2. Remover range existente para evitar colisões
try:
    for aer in ws.Protection.AllowEditRanges:
        if aer.Title == "DadosBUP":
            aer.Delete()
except Exception:
    pass

# 3. Determinar limite da tabela
max_row = ws.UsedRange.Rows.Count
max_col = ws.UsedRange.Columns.Count

from openpyxl.utils import get_column_letter
last_col_letter = get_column_letter(max_col)
range_str = f"A2:{last_col_letter}{max_row}"

# 4. Adicionar o range com senha (impede edição direta, mas permite ordenação)
ws.Protection.AllowEditRanges.Add("DadosBUP", ws.Range(range_str), "PecasInova2026")

# 5. Restringir seleção apenas às células desbloqueadas
ws.EnableSelection = 1  # 1 = xlUnlockedCells

# 6. Proteger a folha garantindo ordenação e autofiltro
ws.Protect(Password="PecasInova2026", AllowSorting=True, AllowFiltering=True)
```

---

## 4. Plano de Testes (DoD)

| ID do Caso | Descrição do Teste | Resultado Esperado |
| :--- | :--- | :--- |
| **TEST-01** | Validação Estrita do Status | Tentar digitar "Outro Valor" em `Status_Contato_1`; o Excel bloqueia e exibe caixa de erro com botão Cancelar. |
| **TEST-02** | Bloqueio de Seleção | Tentar clicar na coluna "CNPJ" ou "Nome Cliente"; o cursor é forçado para as colunas laranja e a seleção das células bloqueadas é impedida. |
| **TEST-03** | Ordenação de Tabela Protegida | Aplicar classificação de A-Z em qualquer coluna via seta do Autofiltro; a ordenação ocorre com sucesso sem requisição de senha. |
| **TEST-04** | Tentativa de Edição em Célula Bloqueada | Se por qualquer meio o usuário tentar modificar um CNPJ, o Excel exige a senha do range "DadosBUP", impedindo a edição arbitrária. |
