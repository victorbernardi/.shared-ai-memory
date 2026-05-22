# Spec: OpenCode Global Tool Routing

**Data:** 2026-04-23
**Autor:** Victor Bernardi
**Status:** Aprovado

---

## Propósito

Definir uma política global do OpenCode no Stout para roteamento de ferramentas, sem afetar o Antigravity. A regra desejada é: pesquisas web devem usar o MCP Tavily, consultas de documentação técnica devem usar o MCP Context7 e persistência de memória deve usar o `context-agent`.

---

## Escopo

- Vale para o OpenCode em `C:/Projetos/Stout/.opencode/`
- Não modifica `antigravity/`
- Não altera plugins externos nem o repositório `Plugins/everything-claude-code/`
- Não redefine o comportamento interno do Antigravity, que já está configurado separadamente

---

## Decisão Arquitetural

A política será centralizada em um arquivo de instrução global próprio do OpenCode, referenciado por `C:/Projetos/Stout/.opencode/opencode.json`. A configuração técnica do MCP Tavily também será adicionada no mesmo `opencode.json`, enquanto o `context7` permanece como está.

Essa separação evita misturar contexto geral do projeto com regras operacionais específicas. O `GEMINI.md` continua como contexto do ecossistema, enquanto a nova instrução passa a ser a fonte explícita das regras de roteamento de ferramentas do OpenCode.

---

## Estrutura

### 1. Configuração MCP

Adicionar `tavily-search` em `C:/Projetos/Stout/.opencode/opencode.json` usando variável de ambiente, sem copiar credenciais do Antigravity para dentro do Stout.

### 2. Política Global de Ferramentas

Criar um arquivo dedicado com as regras:

- web search -> `tavily-search`
- documentação técnica externa -> `context7`
- memória persistente de sessão/projeto -> `context-agent`
- fallbacks só quando a ferramenta primária não estiver disponível ou não cobrir o caso

### 3. Inclusão Global

Incluir esse arquivo na lista `instructions` do OpenCode para que a regra valha em toda sessão do motor, não apenas em agentes específicos.

---

## Regras Operacionais

### Pesquisa Web

Quando a intenção for busca geral na web, pesquisa exploratória, levantamento de fontes externas ou validação de fatos recentes, a ferramenta prioritária deve ser o MCP `tavily-search`.

Ferramentas genéricas de fetch não devem ser a primeira escolha para busca aberta.

### Documentação Técnica

Quando a intenção for consultar documentação oficial, APIs, SDKs, referências de framework ou material técnico estruturado, a ferramenta prioritária deve ser o MCP `context7`.

Busca web comum só entra como fallback quando a documentação não estiver disponível via Context7.

### Memória

Quando a intenção for salvar contexto, decisões, pendências ou estado de projeto para continuidade entre sessões, a política deve apontar para o `context-agent`, e não para mecanismos genéricos de memória.

---

## Segurança

- Nenhuma credencial será hardcoded em arquivos novos do OpenCode
- O Tavily deve usar variável de ambiente (`TAVILY_API_KEY`)
- A mudança não deve introduzir dependência do layout do Antigravity

---

## Validação

Após a implementação, validar:

1. `C:/Projetos/Stout/.opencode/opencode.json` continua sendo JSON válido
2. O bloco `mcp` passa a conter `tavily-search`
3. A lista `instructions` inclui o novo arquivo de política global
4. O arquivo de política deixa explícito que a regra vale só para o OpenCode/Stout
5. Nenhum arquivo sob `antigravity/` é modificado

---

## Fora de Escopo

- Portar ou reconfigurar o Antigravity
- Alterar skills do plugin ECC
- Implementar novas ferramentas de memória além do `context-agent`
- Criar lógica automática de fallback mais complexa que uma instrução global clara
