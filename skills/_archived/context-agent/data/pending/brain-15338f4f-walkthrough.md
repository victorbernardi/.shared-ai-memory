# Walkthrough: Visibilidade Omnipresente e Setup Final

Concluímos o ajuste final de infraestrutura. Todas as habilidades (Superpowers + Codex) estão agora unificadas no "DNA" global do seu motor.

## A Solução Definitiva para Visibilidade

Após diagnosticar que o motor priorizava configurações locais e ignorava plugins de markdown via JSON, mudamos para a estratégia de **Junctions de Agentes Globais**.

### 1. Unificação na Raiz do Agente
- **Diretório Global**: `C:\Users\victor.bernardi\.opencode\agent\`
- **Ação**: Linkamos individualmente cada skill do Codex e do Superpowers neste diretório.
- **Resultado**: Visibilidade garantida em **QUALQUER** pasta do seu computador (disco C:) onde você abrir o OpenCode.

### 2. Limpeza de Configurações
- Removemos as entradas redundantes de `plugin` dos arquivos `opencode.json` e `opencode.jsonc`. 
- Isso elimina mensagens de erro e garante que o motor utilize apenas as versões locais das skills que agora você pode editar e melhorar.

## O Que Você Tem Agora (Tab Menu)

Ao apertar Tab, você verá:
- **Skills Codex**: `Skill_Engenheiro_Master`, `Skill_Handover_Insight`, etc.
- **Skills Superpowers**: `brainstorming`, `systematic-debugging`, `writing-plans`, etc.
- **Inova Core**: Suas diretrizes globais de SQL e Wiki.

## Estrutura de Pastas Final

| Componente | Caminho Real (Editável) |
| :--- | :--- |
| **Skills Superpowers** | `C:\Projetos\Stout\superpowers\skills` |
| **Skills Codex** | `C:\Projetos\Codex_Second_Brain\Skills` |
| **Suíte de Skills (Linked)** | `C:\Users\victor.bernardi\.opencode\agent` |
| **Index da Wiki Inova** | `C:\Projetos\Stout\Inova\index.md` |

O setup está **100% calibrado** para máxima potência e produtividade. 🚀
