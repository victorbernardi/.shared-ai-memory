# Walkthrough: Transição de Identidade BUP

Nesta tarefa, realizamos a transição completa da identidade do projeto de `lista-clientes` para `BUP-base-unica-pós-venda`.

## Mudanças Realizadas

### 1. Memória Global (.shared-ai-memory)
- Renomeamos as pastas de histórico e temporárias:
    - `.gemini\history\lista-clientes` -> `BUP-base-unica-pós-venda`
    - `.gemini\tmp\lista-clientes` -> `BUP-base-unica-pós-venda`
- Criamos o novo diretório de documentação ativa:
    - `docs\active\BUP-base-unica-pós-venda`

### 2. Reconstrução de Junctions
- A pasta `docs/` local agora é uma **Junction** apontando para o diretório centralizado na memória global:
    - `docs/` -> `C:\Users\victor.bernardi\.shared-ai-memory\docs\active\BUP-base-unica-pós-venda`
- Isso garante que a documentação técnica e os planos sejam persistidos globalmente.

### 3. Governança e Documentação
- **ANTIGRAVITY.md**: Atualizado com o novo nome do projeto e os caminhos corretos da hierarquia de memória.
- **GEMINI.md**: Atualizado para referenciar o script principal `consolidate_bup.py` e marcar o progresso da estratégia.

### 4. Saneamento de Scripts
- **qa_latest_output.py**: Agora busca dinamicamente o arquivo `BUP_POS_VENDA_*.xlsx` mais recente na pasta `data/`.
- **resgate_dados_v4.py** & **polimento_final_v5.py**: Removidas referências hardcoded ao antigo `Motor CEVAP`. Os scripts agora operam de forma dinâmica dentro da pasta do projeto atual.

## Verificação
- [x] Junction `docs/` validada (os arquivos Spec e Plan foram movidos com sucesso para a memória global).
- [x] Scripts auxiliares saneados e prontos para uso.
- [x] Estrutura de memória global sincronizada com o novo nome.

---
*Assinado: Antigravity (IA)*
