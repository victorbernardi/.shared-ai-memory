# Antigravity Infrastructure & Skill Management

## How to Access Skills

**In Gemini / Antigravity:** O orquestrador deve seguir a seguinte hierarquia de busca ao receber um comando:
1. **Nível 1 (Golden Copy):** Buscar em `C:\Motores-LLM\gemini-cli\antigravity\skills`.
2. **Nível 2 (Plugins):** Buscar em `C:\Projetos\Stout\Plugins`. O orquestrador **DEVE** ler obrigatoriamente o arquivo `C:\Projetos\Stout\Plugins\CATALOGO.md` para tomar a decisão baseada nas skills originais disponíveis.
3. **Nível 3 (Fallback):** Acionar a skill `skill-manager` para buscar ou instalar novas capacidades.

**Clonagem e Isolamento:**
Uma vez selecionada a skill ideal, ela deve ser **clonada** integralmente para a pasta `skills/` do projeto local (ex: `./skills/[nome-da-skill]`). 
- **PROIBIÇÃO:** Nunca utilize *junctions* ou links simbólicos para a pasta de skills local. Cada projeto deve ser auto-contido e imutável.

**Comando `promote-to-global`:**
O Engenheiro (Gemini CLI) pode ser instruído a promover uma skill local para o nível global. O fluxo consiste em validar a qualidade da skill local e movê-la/copiá-la para `C:\Projetos\Stout\Plugins`, atualizando o `CATALOGO.md`.
