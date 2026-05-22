# Spec: Conversão de Knowledge Work Plugins para Skills Antigravity

## Objetivo
Instalar e converter apenas as skills localizadas em `C:\Projetos\Stout\Plugins\knowledge-work-plugins\data` para o diretório de skills do Antigravity.

## Entendimento Atual
- O repositório está em `C:\Projetos\Stout\Plugins\knowledge-work-plugins`.
- O foco exclusivo é a subpasta `data`, que contém skills como `explore-data`, `write-sql`, etc.
- A instalação física no Antigravity envolve copiar essas pastas para `C:\Projetos\Stout\antigravity\skills\`.
- As skills originais já possuem arquivos `SKILL.md`, mas podem precisar de ajustes no frontmatter YAML para conformidade total com o Antigravity.

## Requisitos
1. **Instalação:** Copiar as subpastas de `C:\Projetos\Stout\Plugins\knowledge-work-plugins\data\skills\` para o diretório de destino.
2. **Nomenclatura:** Adicionar um prefixo `data-` nas pastas de destino para organização (ex: `data-explore-data`).
3. **Conversão:** Validar e ajustar o frontmatter YAML nos arquivos `SKILL.md`.

## Arquitetura Proposta
- **Processo Manual/Scriptado:** Identificar as pastas em `data/skills`, aplicar o prefixo e mover para a pasta de skills do projeto Stout.
- **Estrutura Final Exemplo:**
  - `C:\Projetos\Stout\antigravity\skills\data-explore-data\SKILL.md`
  - `C:\Projetos\Stout\antigravity\skills\data-write-sql\SKILL.md`

## Validação
- Verificar se o Antigravity reconhece as novas skills via `view_file`.
- Testar um gatilho de uma das novas skills (ex: "explore data").
