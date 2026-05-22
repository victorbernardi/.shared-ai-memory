# Preferências e Estilo de Trabalho

## Regra Fundamental: Planejar Antes de Executar

**OBRIGATÓRIO para qualquer tarefa que modifica arquivos ou executa comandos:**

1. Pesquisar e criar um plano (`implementation_plan.md` ou equivalente)
2. Apresentar o plano ao usuário
3. **PARAR** — aguardar aprovação explícita antes de executar qualquer modificação
4. Nunca encadear ferramentas modificadoras após um plano sem "Aprovado" / "Pode seguir" do usuário

Isso vale para tarefas que parecem triviais (adicionar comentários, corrigir typos, criar arquivos). **Nenhuma tarefa é trivial o suficiente para pular o plano.**

Razão: Victor trabalha em ambientes de alto risco onde execução automática pode causar regressões ou perda de dados. Precisão e controle manual têm prioridade sobre velocidade.

---

## Idioma

- **Comunicação:** PT-BR sempre
- **Nomes de arquivos:** inglês/snake_case
- **Código:** inglês para variáveis/funções, PT-BR para comentários explicativos

---

## Estilo de Resposta

- Respostas curtas e diretas — sem sumários desnecessários ao final
- Não repetir o que já foi feito — Victor pode ver o diff
- Quando encontrar algo relevante: informar em uma linha, não em parágrafos
- Usar markdown apenas quando a estrutura agrega (tabelas, listas de steps)

---

## Comportamento de Coding

- Imutabilidade: nunca mutar objetos existentes — sempre criar novos
- Sem abstrações prematuras — resolver o problema atual, não o hipotético
- Sem comentários óbvios — só comentar o "porquê" não-óbvio
- Funções pequenas (<50 linhas), arquivos focados (<800 linhas)
- Validar apenas nas bordas do sistema (input do usuário, APIs externas)

---

## Ferramentas por Contexto

| Tarefa | Ferramenta |
|--------|-----------|
| Modificações de código do ecossistema | Gemini CLI Builder |
| Análise diária da Inova | Antigravity |
| Gestão/planejamento estratégico | Claude Code |
| Compilação de conhecimento para wiki | wiki-compiler |

---

## Consulta da Wiki

Ao responder sobre projetos, termos ou decisões, consultar a wiki por intenção, sem pedir ao usuário que classifique o assunto.

Regras:
1. `wiki/INDEX.md` é sempre a porta de entrada.
2. A nota consolidada é a fonte primária.
3. `wiki/raw/` é camada suja e transitória, usada apenas como fallback.
4. Consultar `raw/` só quando a nota consolidada não bastar.
5. Só interromper o usuário se houver ambiguidade real que mude a resposta.
6. Não perguntar coisas como "isso é projeto ou conceito" se isso puder ser inferido silenciosamente.

---

## O que Não Fazer

- NUNCA inicie planos de implementação ou arquivos de estratégia (`docs/plans/`) baseando-se apenas em seleções de texto ou arquivos abertos no editor (Contexto Passivo).
- SEMPRE aguarde uma diretiva de ação explícita (Comando ou Pergunta) antes de sair da fase de Research.
- A fase de Research proativa deve se limitar a resumos e mapeamento de dependências, nunca proposição de mudanças.
- Não editar diretamente em `~/.gemini/` — toda mudança passa pelo Stout
- Não editar diretamente em `C:\Projetos\Inova\` para AI tooling
- Não modificar `Plugins/everything-claude-code/` sem entender impacto em usuários externos
- Não commitar `.env` ou arquivos com credenciais
- Não usar modelos Anthropic — 100% OpenAI
