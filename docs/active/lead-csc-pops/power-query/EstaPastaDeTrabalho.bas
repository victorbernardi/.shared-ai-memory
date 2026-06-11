Attribute VB_Name = "EstaPastaDeTrabalho"
' =============================================================================
' EstaPastaDeTrabalho.bas — colar no módulo "EstaPastaDeTrabalho" (ThisWorkbook)
'
' ATENÇÃO: este código NÃO deve ser importado via Arquivo > Importar.
' Copie o conteúdo abaixo e cole diretamente no módulo ThisWorkbook do Editor VBA.
' =============================================================================

Private Sub Workbook_Open()
    ' Aplica proteção automaticamente ao abrir o arquivo
    Call ProtecaoPlanilha.ProtegerPlanilha
End Sub
