# Especificação: Evolução da Skill Context-Agent (Argumentos Manuais)

## 1. Problema
Atualmente, o comando `save` da skill `context-agent` extrai metadados (tópicos, decisões, tarefas) de forma puramente automatizada a partir dos logs da sessão. Isso resulta em:
- Tópicos imprecisos para sessões técnicas complexas.
- Perda de decisões importantes que não utilizam os marcadores padrão.
- Dificuldade em guiar a "memória" do sistema de forma deliberada.

## 2. Objetivos
Permitir que o usuário ou o agente forneça informações explícitas durante o salvamento da sessão, garantindo que a memória de longo prazo reflita fielmente os pontos cruciais discutidos.

## 3. Requisitos Funcionais

### 3.1. Novos Argumentos no CLI
O comando `save` deve aceitar os seguintes parâmetros opcionais:
- `--topic`: String única para definir o título principal da sessão.
- `--summary`: Texto curto (resumo executivo) que descreve o que foi feito.
- `--decisions`: Lista ou string de decisões tomadas.
- `--tasks`: Lista ou string de tarefas pendentes ou concluídas.

### 3.2. Lógica de Precedência
Os dados fornecidos via argumentos CLI devem ter **prioridade absoluta** sobre os dados extraídos automaticamente pelo parser.
- Se `--topic` for fornecido, ele substitui a extração automática de tópicos.
- Se `--summary` for fornecido, ele deve ser injetado no topo do arquivo de resumo gerado.

### 3.3. Retrocompatibilidade
O comando `save` sem argumentos deve continuar funcionando exatamente como hoje (modo 100% automático).

## 4. Requisitos Não-Funcionais
- **Robustez:** O sistema não deve falhar se os argumentos manuais contiverem caracteres especiais ou forem muito longos.
- **Transparência:** O log de salvamento deve indicar quais campos foram preenchidos manualmente.

## 5. Critérios de Aceite
1. Executar `python context_manager.py save --topic "Teste Manual"` gera um arquivo markdown onde o primeiro tópico é "Teste Manual".
2. O parser automático não sobrescreve os valores manuais.
3. A funcionalidade de sincronização com `MEMORY.md` reflete os dados manuais.
