# Plano de Desbloqueio e Atualização de Leads no Excel (VBA & Power Query)

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Resolver o bloqueio de atualização da planilha de produção `leads-csc-pops-peças.xlsm` no Excel do usuário, permitindo que os dados da planilha base do OneDrive sejam carregados via Power Query sem violar a proteção de células estruturais.

**Architecture:** O problema ocorre porque o Power Query tenta sobrescrever células bloqueadas na aba `"Leads Ativos"`. A solução é configurar o Power Query para não atualizar automaticamente ao abrir o arquivo e criar/configurar um botão que execute a macro VBA `AtualizarDados`, a qual desprotege a planilha, faz a atualização e re-protege a planilha com a senha `"InovaPosVendas2026"`.

**Tech Stack:** Excel VBA, Power Query M, openpyxl (Python)

---

### Task 1: Ajustar Propriedades da Conexão do Power Query no Excel

**Files:**
- Modify: `C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\leads-csc-pops-peças.xlsm` (Ajuste nas configurações visuais do Excel)

**Step 1: Desproteger a planilha temporariamente para configuração**
- A abrir a planilha `leads-csc-pops-peças.xlsm`, vá na guia **Revisão** -> **Desproteger Planilha**.
- Digite a senha: `InovaPosVendas2026`.

**Step 2: Desativar a opção "Atualizar ao abrir" da conexão**
- Vá na guia **Dados** -> **Consultas e Conexões** (será exibido o painel lateral).
- Clique com o botão direito na consulta (normalmente chamada `Leads Ativos` ou similar) -> **Propriedades**.
- Na guia *Uso*, **desmarque** a opção *"Atualizar dados ao abrir o arquivo"*.
- **Marque** a opção *"Habilitar carregamento rápido (Fast Load)"*.
- Clique em **OK**.

**Step 3: Salvar a planilha**
- Salve o arquivo `leads-csc-pops-peças.xlsm` (ainda desprotegido para os próximos passos).

---

### Task 2: Validar e Vincular a Macro VBA "AtualizarDados"

**Files:**
- Verify/Import: `docs/power-query/ProtecaoPlanilha.bas`
- Verify/Import: `docs/power-query/EstaPastaDeTrabalho.bas`
- Modify: `C:\Users\victor.bernardi\OneDrive - INOVA EQUIPAMENTOS LTDA\Documentos\leads-csc-pops-peças.xlsm` (Editor de VBA)

**Step 1: Abrir o Editor VBA (Alt + F11)**
- No Excel, pressione `Alt + F11` para abrir o editor de código VBA.

**Step 2: Verificar o módulo "ProtecaoPlanilha"**
- No painel da esquerda (*Project - VBAProject*), verifique se existe um módulo chamado `ProtecaoPlanilha`.
- Se não existir: clique com o botão direito na pasta do projeto -> **Inserir** -> **Módulo**. Altere o nome nas propriedades (F4) para `ProtecaoPlanilha` e cole o código de `docs/power-query/ProtecaoPlanilha.bas`.
- Se já existir, certifique-se de que a macro `AtualizarDados()` está presente:
  ```vba
  Public Sub AtualizarDados()
      Dim ws As Worksheet
      On Error GoTo ErrHandler
      Set ws = ThisWorkbook.Sheets(NOME_ABA)
      ws.Unprotect Password:=SENHA
      ThisWorkbook.RefreshAll
      Application.CalculateUntilAsyncQueriesDone
      Call ProtegerPlanilha
      MsgBox "Dados atualizados com sucesso!", vbInformation, "Leads Preventivos"
      Exit Sub
  ErrHandler:
      Call ProtegerPlanilha
      MsgBox "Erro ao atualizar: " & Err.Description, vbExclamation
  End Sub
  ```

**Step 3: Verificar o módulo "ThisWorkbook" (EstaPastaDeTrabalho)**
- Dê dois cliques em `EstaPastaDeTrabalho` (ou `ThisWorkbook`) no menu esquerdo do VBA.
- Garanta que o evento `Workbook_Open` possui apenas a proteção automática na abertura:
  ```vba
  Private Sub Workbook_Open()
      Call ProtecaoPlanilha.ProtegerPlanilha
  End Sub
  ```

**Step 4: Criar o botão de atualização na planilha**
- No Excel, vá para a aba `"Leads Ativos"`.
- Insira uma forma retangular ou um botão de controle na parte superior da planilha (ex: perto da linha 1, que está desbloqueada).
- Formate-o com o estilo corporativo (ex: fundo azul escuro `#1B365D` com texto branco "Atualizar Leads").
- Clique com o botão direito na forma/botão -> **Atribuir Macro...**
- Selecione a macro `AtualizarDados` (ou `ProtecaoPlanilha.AtualizarDados`) e clique em **OK**.

**Step 5: Salvar e testar**
- Clique no botão criado para testar se ele desprotege, executa o Refresh do Power Query, re-protege a planilha e exibe a mensagem "Dados atualizados com sucesso!".
- Salve e feche a planilha.
