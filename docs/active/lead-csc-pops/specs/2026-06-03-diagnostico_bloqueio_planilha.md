# 🧠 Diagnóstico Técnico: Bloqueio de Atualização na Planilha de Produção

> **Identidade do Documento:** `./docs/specs/2026-06-03-diagnostico_bloqueio_planilha.md`  
> **Data:** 03/06/2026  
> **Status:** Em Revisão (Fase de Brainstorming)  
> **Autor:** Antigravity (Engenheiro de Software)

---

## 🎯 1. Entendimento do Problema

O usuário relatou que não consegue atualizar o arquivo de produção **`leads-csc-pops-peças.xlsm`** localizado no OneDrive porque ele está bloqueado, impedindo que os dados gerados pelo motor Python na planilha de base **`leads-csc-pops-base.xlsx`** sejam integrados.

### Causa Raiz Provável (Arquitetura de Segurança vs. Power Query)
1. **Proteção Ativa:** Para garantir a integridade dos dados e impedir modificações acidentais por parte dos consultores, a planilha de produção `leads-csc-pops-peças.xlsm` protege a aba `"Leads Ativos"` com a senha `"InovaPosVendas2026"`. As colunas estruturais (A até M) são travadas (`Locked = True`) no momento em que o arquivo é aberto via macro `Workbook_Open`.
2. **Conflito com Power Query:** O Power Query é responsável por ler os dados de `leads-csc-pops-base.xlsx` e injetá-los na tabela da aba `"Leads Ativos"` do arquivo de produção. Ao executar uma atualização de dados (Refresh):
   * O Power Query tenta reescrever toda a estrutura da tabela (inclusive as colunas estruturais travadas de A a M).
   * Como a planilha está protegida, o Excel bloqueia a operação e emite um erro de gravação ("planilha protegida").
3. **Atualização Automática ao Abrir:** Se a propriedade da conexão de dados estiver marcada com a opção **"Atualizar dados ao abrir o arquivo"**, o Excel tenta disparar a atualização logo após abrir. Como a macro `Workbook_Open` bloqueia a planilha imediatamente na abertura, o processo entra em conflito e falha, travando o carregamento dos novos leads.

---

## 🛠️ 2. Lógica de Atualização Homologada

Para mitigar o conflito entre a proteção e a escrita do Power Query, o ecossistema possui a macro **`AtualizarDados`** no módulo `ProtecaoPlanilha.bas`:

```vba
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
```

Essa macro realiza o fluxo correto:
1. Remove temporariamente a proteção da planilha (`ws.Unprotect`).
2. Dispara a atualização de todas as conexões (`ThisWorkbook.RefreshAll`).
3. Aguarda a conclusão das consultas assíncronas do Power Query.
4. Reaplica a proteção da planilha (`Call ProtegerPlanilha`), travando as colunas estruturais e deixando abertas apenas as colunas de retorno de contato (`N:O`).

---

## ❓ 3. Perguntas de Alinhamento para o Victor

Para prosseguir com a estratégia de correção física, precisamos confirmar o cenário exato no computador do Victor:

1. **Método de Atualização:** Você está tentando atualizar os dados clicando no botão nativo "Atualizar Tudo" (Data -> Refresh All) do Excel ou clicando no botão customizado que aciona a macro `AtualizarDados()`?
2. **Presença do Código VBA:** O código VBA presente em `docs/power-query/ProtecaoPlanilha.bas` e `EstaPastaDeTrabalho.bas` foi importado/copiado corretamente para dentro do seu arquivo `leads-csc-pops-peças.xlsm`?
3. **Propriedades do Power Query:** A conexão do Power Query está configurada para atualizar automaticamente ao abrir? (Se sim, isso precisa ser desativado para evitar conflito com a macro `Workbook_Open`).
