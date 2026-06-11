# 📄 Especificação Técnica: Implementação de Travas de Segurança e Formatação Visual da BUP

> **ID da Spec:** 2026-06-03-spec-travas-seguranca  
> **Status:** Aprovada pelo Usuário (Fase de Brainstorming Concluída)  
> **Data:** 2026-06-03  
> **Autor:** Antigravity (Engenheiro de Software Inova/Stout)  
> **Contexto:** Alinhamento de segurança do BUP pós-venda com os padrões comerciais da planilha CEVAP.

---

## 1. Objetivo do Projeto

Implementar mecanismos robustos de segurança contra vazamento e modificação indevida de dados, validações de integridade no preenchimento de feedback e formatação de experiência do usuário (UX) na planilha de saída do pipeline da Base Única de Pós-Venda (BUP). A planilha de entrega final no OneDrive passará a ser gerada como `.xlsm` (VBA habilitado) ou `.xlsx` protegida (como fallback).

---

## 2. Requisitos de Negócio e Funcionais

### RF-01: Proteção e Bloqueio de Células
* A planilha gerada pelo pipeline do BUP deve ser protegida por senha padrão do ecossistema: `PecasInova2026`.
* Todas as colunas contendo dados estruturais (CNPJ, Nome, Consultor, Faturamento, InovaPay, Seedz, etc.) devem ser protegidas contra edição e seleção acidental.
* Apenas as 5 colunas de feedback comercial editáveis pelos consultores devem estar desbloqueadas para edição:
  1. `Data_Tentativa_1`
  2. `Status_Contato_1`
  3. `Data_Tentativa_2`
  4. `Status_Contato_2`
  5. `Observacao`

### RF-02: Liberação de Filtros e Ordenação
* Mesmo com a planilha sob proteção ativa, o Excel deve permitir livremente que o usuário aplique **Filtros** e realize **Ordenação** (Sort) nas linhas de dados para fins de navegação comercial.

### RF-03: Bloqueio Físico de Cópia e Colagem (VBA)
* O arquivo de entrega final deve conter um projeto VBA injetado que neutralize atalhos e mecanismos de cópia massiva dos dados:
  * Atalhos bloqueados: `Ctrl+C`, `Ctrl+X`, `Ctrl+V`, `Ctrl+Insert`, `Shift+Insert` e `Shift+Delete`.
  * Desativação do menu de contexto de clique direito nas células bloqueadas para prevenir cópia visual.
  * O arquivo deve ser salvo como `.xlsm` no OneDrive.

### RF-04: Validação de Dados de Entrada (Excel)
* **Validação de Data (`Data_Tentativa_1` e `Data_Tentativa_2`):**
  * O Excel deve recusar qualquer digitação de data fora da janela dinâmica de `[hoje - 30 dias, hoje + 30 dias]`.
  * As datas já preenchidas historicamente (recuperadas de rodadas anteriores) que eventualmente estejam fora dessa janela devem ser mantidas intocadas (sem deleção ou saneamento forçado).
* **Validação de Lista/Dropdown (`Status_Contato_1` e `Status_Contato_2`):**
  * O preenchimento deve ser limitado aos valores oficiais: `Pendente`, `Venda`, `Não Venda`.

### RF-05: Destaque de UX das Células Editáveis
* As 5 colunas editáveis devem receber estilo visual explícito para sinalizar onde o consultor pode digitar:
  * **Cor de Fundo (Fill):** Hexadecimal `FFFFC000` (Laranja/Amarelo vibrante, padrão leads-csc-pops).
  * **Bordas:** Estilo pontilhado (`dotted`) em tom cinza médio (`808080`) demarcando claramente as células editáveis.

### RF-06: Tratamento de Concorrência e Escrita no OneDrive
* Ao tentar salvar o arquivo no OneDrive, caso ele esteja aberto por outro usuário (concorrência):
  * O script deve capturar a falha imediatamente e encerrar de forma limpa (sem retentativas demoradas em loop).
  * O log cumulativo de agendamento local (`bup_scheduler.log`) deve registrar um aviso explícito de arquivo ocupado.
  * Os dados gerados devem ser salvos com segurança localmente em `data/BUP_POS_VENDA.xlsx`.

---

## 3. Requisitos Não-Funcionais e Restrições Técnicas

* **Desempenho:** O tempo de processamento das validações via `openpyxl` e conversão VBA via `win32com` não deve acrescentar mais do que 15 segundos ao tempo total do pipeline.
* **Resiliência e Fallback:** Caso a biblioteca `win32com` ou o ambiente de execução não suportem o Excel COM (como servidores Linux sem interface gráfica), o script deve registrar um aviso no log e realizar o fallback automático salvando o arquivo como `.xlsx` protegido por senha e com as validações de dados ativas (mas sem a injeção do VBA anti-cópia).
* **Consistência de Formatos:** O script deve assegurar que os formatos das datas nas colunas editáveis permaneçam como `DD/MM/YYYY` após qualquer manipulação do interpretador Excel COM.

---

## 4. Arquitetura e Engenharia de Software

### Componentes de Código a Modificar no `scripts/consolidate_bup.py`

1. **Definição de Constantes Globais:**
   * Configuração de variáveis com códigos macros em VBA (`_VBA_THISWORKBOOK` e `_VBA_MODULO_BLOQUEIO`).
   * Configuração da senha `SENHA_PROTECAO = "PecasInova2026"`.

2. **Novas Funções do Pipeline:**
   * `_aplicar_protecao_excel(xlsx_path)`: Responsável por carregar o workbook local com openpyxl, aplicar estilos de bordas pontilhadas (`dotted`), cores de fundo (`FFFFC000`), DataValidation de datas e listas, e travar a planilha com exceção de filtros/ordenação.
   * `_converter_para_xlsm(xlsx_path, xlsm_path)`: Responsável por instanciar a API do Excel via `win32com.client.Dispatch`, salvar no formato `.xlsm` (FileFormat=52) e injetar os blocos de código VBA.
   * `_corrigir_formato_datas_tentativa(xlsm_path)`: Repassa o arquivo `.xlsm` após o salvamento COM para certificar o formato `DD/MM/YYYY`.

3. **Log de Auditoria:**
   * Gravação de logs específicos em `data/logs/bup_scheduler.log` detalhando o sucesso da proteção e eventuais avisos de arquivos bloqueados ou fallbacks adotados.

---

## 5. Plano de Validação e Testes (DoD)

Para garantir que o objetivo da especificação foi atingido antes de dar a tarefa por concluída, os seguintes testes serão executados e validados empiricamente:

| ID do Caso | Descrição do Teste | Resultado Esperado |
| :--- | :--- | :--- |
| **TEST-01** | Validação de Células Protegidas | Células estruturais (ex: Nome do Cliente, CNPJ) recusam digitação com aviso de planilha protegida por senha. |
| **TEST-02** | Validação de Células Editáveis | As células de `Observacao` e `Data_Tentativa_1` aceitam edições normalmente. |
| **TEST-03** | Validação de Filtros/Ordenação | Os filtros de coluna funcionam perfeitamente mesmo com a planilha bloqueada. |
| **TEST-04** | Validação de Validade de Datas | Ao digitar uma data fora do intervalo de 30 dias em `Data_Tentativa_1`, o Excel exibe a mensagem de erro informativa e rejeita o valor. |
| **TEST-05** | Preservação de Datas Legadas | Datas antigas preenchidas no histórico de feedbacks são lidas e gravadas na planilha sem sofrer deleção. |
| **TEST-06** | Validação de Dropdowns de Status | Ao tentar digitar um status diferente de "Pendente", "Venda" ou "Não Venda", o Excel rejeita a entrada. |
| **TEST-07** | Teste de Bloqueio de Cópia (VBA) | Ao tentar pressionar `Ctrl+C` ou clicar com o botão direito nas células bloqueadas do `.xlsm` gerado, a ação é cancelada. |
| **TEST-08** | Teste de Concorrência do OneDrive | Simular que o arquivo OneDrive de destino está aberto para edição em outro processo e rodar o script; validar se ele gera o log de conflito amigável e encerra com sucesso preservando o arquivo local. |
| **TEST-09** | Fallback de COM | Desabilitar temporariamente a injeção VBA e forçar o salvamento local do `.xlsx` protegido; certificar que a proteção de células e validações de dados continuam ativas. |
