Attribute VB_Name = "ProtecaoPlanilha"
' Layout (15 colunas, sem Primeiro Alerta):
'   A:M = dados estruturais (bloqueados)
'   N   = Retorno do Contato (editavel + dropdown)
'   O   = Observacoes (editavel)

Option Explicit

Private Const SENHA As String = "InovaPosVendas2026"
Private Const NOME_ABA As String = "Leads Ativos"

Public Sub ProtegerPlanilha()
    Dim ws As Worksheet
    Dim lo As ListObject
    On Error GoTo ErrHandler
    Set ws = ThisWorkbook.Sheets(NOME_ABA)

    ws.Unprotect Password:=SENHA

    ' Reativa o AutoFilter do Table (Power Query pode desativa-lo ao carregar)
    For Each lo In ws.ListObjects
        lo.ShowAutoFilter = True
    Next lo

    ' Trava todas as celulas
    ws.Cells.Locked = True

    ' Linha 1 desbloqueada para botoes de filtro do Table serem clicaveis
    ws.Rows(1).Locked = False

    ' Desbloqueia colunas de feedback comercial
    ws.Columns("N:O").Locked = False

    Call AplicarDropdownRetorno(ws)

    ws.Protect Password:=SENHA, _
        DrawingObjects:=True, _
        Contents:=True, _
        AllowSorting:=True, _
        AllowFiltering:=True, _
        AllowUsingPivotTables:=False

    Exit Sub
ErrHandler:
    MsgBox "Erro: " & Err.Description, vbExclamation
End Sub

Private Sub AplicarDropdownRetorno(ws As Worksheet)
    Dim ultimaLinha As Long
    ultimaLinha = ws.Cells(ws.Rows.Count, "A").End(xlUp).Row
    If ultimaLinha < 2 Then Exit Sub

    With ws.Range("N2:N" & ultimaLinha).Validation
        .Delete
        .Add Type:=xlValidateList, AlertStyle:=xlValidAlertStop, _
             Formula1:="Venda,Venda Perdida,Sem Contato"
        .IgnoreBlank = True
        .InCellDropdown = True
        .ShowError = True
        .ErrorTitle = "Entrada Invalida"
        .ErrorMessage = "Selecione: Venda, Venda Perdida ou Sem Contato."
    End With
End Sub

Public Sub AtualizarDados()
    Dim ws As Worksheet
    On Error GoTo ErrHandler
    Set ws = ThisWorkbook.Sheets(NOME_ABA)
    ws.Unprotect Password:=SENHA
    ThisWorkbook.RefreshAll
    Application.CalculateUntilAsyncQueriesDone
    Call ProtegerPlanilha
    MsgBox "Dados atualizados!", vbInformation, "Leads Preventivos"
    Exit Sub
ErrHandler:
    Call ProtegerPlanilha
    MsgBox "Erro: " & Err.Description, vbExclamation
End Sub
