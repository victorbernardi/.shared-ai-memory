# Plano de Implementação: Reset de Cache ChromeDriver

Este plano descreve a limpeza do binário incompatível para forçar o alinhamento de versões.

## 1. Alterações Propostas

### [DELETE] [undetected_chromedriver.exe](file:///C:/Users/victor.bernardi/AppData/Roaming/undetected_chromedriver/undetected_chromedriver.exe)
Remoção do binário da versão 148.

## 2. Execução

1.  **Kill Processes:** Encerrar qualquer instância de `chromedriver.exe` ou `chrome.exe` que possa estar travando o arquivo.
2.  **Purge:** Deletar o executável no caminho identificado.
3.  **Bootstrap:** Executar o `notebooklm_proxy.cmd` para disparar o novo download.

## 3. Verificação
Acompanhar o log do terminal para garantir que o download da versão 147 seja concluído com sucesso.

---
**Aprovas o reset do driver? (S/N)**
