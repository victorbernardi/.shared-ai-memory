# Plano de Atualização da Governança e Ecossistema Stout-Init

## Objetivo
Implementar a nova arquitetura de governança em camadas (Global vs. Local), redefinir o fluxo de orquestração de skills via `using-superantigravity` e otimizar o ciclo de vida de inicialização de projetos com o `stout-init`.

## Escopo & Impacto
Esta atualização afeta o comportamento global do agente, definindo regras rígidas de separação de responsabilidades (Engenheiro vs. Cientista) e garantindo a imutabilidade dos projetos locais (cada projeto carrega seu próprio snapshot de skills).

## Passos da Implementação

### Fase 1: Atualização da Orquestração (`using-superantigravity`)
Modificaremos a skill `using-superantigravity` para incorporar a lógica de orquestração e o comando de clonagem:
1. **Lógica de Busca em Cascata:**
   - Instruir a busca primária na Golden Copy: `C:\Motores-LLM\gemini-cli\antigravity\skills`.
   - Busca secundária lendo o arquivo `C:\Projetos\Stout\Plugins\CATALOGO.md` para encontrar skills originais.
   - Fallback: acionar a skill `skill-manager`.
2. **Clonagem e Isolamento:**
   - Ao selecionar uma skill global ou plugin, instruir o agente a **cloná-la** para o diretório local do projeto (ex: `./skills/[nome-da-skill]`).
   - Proibição explícita do uso de *junctions* para a pasta de skills local. As skills locais devem permanecer imutáveis a menos que atualizadas manualmente.
3. **Comando `promote-to-global`:**
   - Definir o fluxo onde o "Engenheiro" (Gemini CLI) pode ser instruído a promover uma skill local bem-sucedida de volta para `C:\Projetos\Stout\Plugins`.

### Fase 2: O Novo Ciclo de Vida (`stout-init` + `brainstorming`)
Atualizaremos os templates e possivelmente a lógica da skill `stout-init` (localizada na Golden Copy e/ou drafts) para:
1. **Prioridade do Código:**
   - O scaffolding inicial deve criar a estrutura física (pastas `src`, `docs`, etc.) antes de qualquer reflexão, garantindo um ambiente estável.
2. **Integração com Brainstorming:**
   - Após criar os arquivos (incluindo versões base do `GEMINI.md` e `ANTIGRAVITY.md` locais), acionar automaticamente a skill `brainstorming`.
   - O objetivo do brainstorming será preencher e refinar esses arquivos locais com o contexto específico do projeto, alinhado à identidade global (`plano_executivo_kpis_ia_pos_venda_v2_consolidado.md`).

### Fase 3: Estruturação dos Templates (Global vs Local)
1. **GEMINI.md (Global / Engenheiro):**
   - Refinaremos o template global para focar nas regras padronizadas (workflow, deploy, criação de novas skills).
2. **ANTIGRAVITY.md (Global / Cientista):**
   - Refinaremos o template focado em análise de dados, validações e uso dos MCPs.
3. **CATALOGO.md:**
   - Criação de um esqueleto base em `C:\Projetos\Stout\Plugins\CATALOGO.md` (caso não exista) para indexar as skills originais.

## Validação
- Executar um teste simulado do comando "iniciar novo projeto".
- Verificar se a tentativa de usar uma skill dispara a busca no diretório correto e resulta na clonagem local.

## Alternativas Consideradas
- **Usar Junctions para as Skills:** Descartado pois violaria o princípio de isolamento e imutabilidade dos projetos antigos em caso de atualização de uma skill global.
