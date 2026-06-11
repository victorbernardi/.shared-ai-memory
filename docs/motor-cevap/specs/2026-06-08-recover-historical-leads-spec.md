# Especificação Técnica: Recuperação Histórica de Leads (Motor CEVAP)

> **Status:** Aprovado para Planejamento  
> **Data:** 08/06/2026  
> **Versão:** v1.0  
> **Autor:** Gemini CLI Builder / Arquiteto de Dados  

---

## 1. Objetivo

Implementar um script pontual de diagnóstico e recuperação (`recover_historical_leads.py`) para resgatar os preenchimentos de controle comercial (`Data_Tentativa_1`, `Status_Contato_1`, `Data_Tentativa_2`, `Status_Contato_2`, `Observacao`) realizados por consultores em planilhas históricas desatualizadas (devido ao uso de links antigos), e aplicar esses dados especificamente nos clientes que hoje constam como **Pendentes** na planilha ativa atual do OneDrive.

---

## 2. Requisitos

### 2.1 Requisitos Funcionais

1.  **Varredura Cronológica Reversa:** 
    *   Listar todos os arquivos da pasta [data/](file:///C:/Projetos/Inova/projects/motor-cevap/data) correspondentes ao padrão `CEVAP_ATIVACAO_*.xlsx`.
    *   Extrair o timestamp (`YYYYMMDD_HHMM`) de cada nome de arquivo.
    *   Ordenar os arquivos do mais recente para o mais antigo.
2.  **Identificação de Alvos na Planilha Atual:**
    *   Ler a planilha de produção ativa no OneDrive (`CEVAP_ATIVACAO.xlsx`).
    *   Mapear quais CNPJs estão com status em aberto, isto é, possuem `Status_Contato_1 == "Pendente"` ou `Status_Contato_2 == "Pendente"` (ou vazios).
    *   **Regra de Ciclo Fechado:** Clientes que já estejam marcados como `"Venda"` ou `"Nao Venda"` na planilha ativa não devem ter seus dados modificados, pois o ciclo do lead já foi encerrado.
3.  **Resgate de Preenchimento Histórico:**
    *   Para os CNPJs elegíveis (atualmente `"Pendente"`), buscar retrospectivamente nas planilhas históricas.
    *   O script deve capturar a primeira ocorrência cronológica mais recente que contenha preenchimento válido (não-nulo, não-vazio e diferente de `"Pendente"`).
    *   Os campos a serem restaurados são: `Data_Tentativa_1`, `Status_Contato_1`, `Data_Tentativa_2`, `Status_Contato_2` e `Observacao`.
4.  **Normalização de Dados:**
    *   Saneamento total de CNPJs (limpeza de caracteres não numéricos e `zfill(14)`).
    *   Limpeza de espaços em branco nos textos de Observação.
    *   Conversão automática de variações textuais de status inválidas para o padrão da validação: `"Venda"`, `"Nao Venda"`, `"Sem Contato"`.
5.  **Relatório de Auditoria:**
    *   Escrever um relatório Markdown detalhado em [docs/specs/](file:///C:/Projetos/Inova/projects/motor-cevap/docs/specs) contendo:
        *   Lista de CNPJs e Clientes que foram atualizados.
        *   Os valores anteriores (Pendente) vs. os novos valores recuperados.
        *   A planilha histórica de onde o dado foi resgatado.

### 2.2 Requisitos Não-Funcionais

1.  **Isolamento Operacional:** O script deve rodar sob demanda (`python scripts/recover_historical_leads.py`) e não será executado automaticamente no pipeline diário.
2.  **Imunidade a Falhas de Leitura:** Arquivos de dados corrompidos ou com schema inválido devem ser ignorados individualmente com mensagens claras no terminal (sem interromper a execução).
3.  **Encoding:** Respeitar a **Regra 7** (uso estrito de `encoding='utf-8'` em operações de E/S de texto).

---

## 3. Arquitetura e Mudanças Propostas

Como este é um processo pontual, **nenhum arquivo do pipeline principal será modificado**.
As alterações se limitam a:
1.  Criação do script de recuperação: [scripts/recover_historical_leads.py](file:///C:/Projetos/Inova/projects/motor-cevap/scripts/recover_historical_leads.py)
2.  Criação do script de teste unitário: [tests/test_recovery.py](file:///C:/Projetos/Inova/projects/motor-cevap/tests/test_recovery.py)
3.  Geração do relatório de auditoria Markdown em [docs/specs/](file:///C:/Projetos/Inova/projects/motor-cevap/docs/specs) após a execução em Dry-Run.

---

## 4. Plano de Validação e Testes (DoD)

1.  **Teste Unitário (`pytest`):** Criar um mock em `test_recovery.py` com cenários de:
    *   Clientes inalterados (já com status "Venda" or "Nao Venda").
    *   Clientes atualizados com preenchimentos válidos de planilhas desatualizadas.
    *   Desempate cronológico (garantir que a planilha mais recente sobrescreva as mais antigas).
2.  **Dry-Run Real:** Executar o script no modo simulação, analisar o relatório Markdown gerado e, somente após aprovação humana, aplicar as alterações físicas na planilha do OneDrive.
