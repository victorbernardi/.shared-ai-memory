# Walkthrough: Otimização de Performance e Progressive Disclosure (Skill using-superantigravity)

**Data:** 2026-05-13  
**Contexto:** Sessão de infraestrutura Stout Edition.  
**Objetivo:** Resolver lentidão de carregamento e saturação de contexto.

---

## 1. O Problema: O Monólito de Instruções
Identificamos que a ativação da skill `using-superantigravity` injetava instantaneamente ~150 linhas de texto denso (diagramas, tabelas e filosofias) no contexto. Isso causava:
- Latência percebida de vários segundos.
- Consumo desnecessário da janela de contexto (Context Wall) com informações que o agente só precisaria em fases específicas.

## 2. A Solução: Arquitetura de 3 Níveis
Aplicamos a **Regra 1 do GEMINI.md** (Progressive Disclosure) para "refrigerar" o conhecimento:

### Nível 1: Launcher & Automação (SKILL.md)
O arquivo principal foi reduzido ao essencial:
- Metadados e gatilhos de ativação.
- Comando de background mandatório (`brain-watcher.py`).
- Instrução clara de como acessar os níveis superiores sob demanda.

### Nível 2: Processo (references/stout-lifecycle.md)
Arquivo isolado contendo as instruções das fases `Research`, `Strategy` e `Build`. O agente agora só carrega essas regras quando o usuário inicia uma dessas fases.

### Nível 3: Cold Storage (references/infrastructure.md & philosophy.md)
Documentação técnica profunda (Red Flags, Hierarquia de busca, Clonagem). Consulta apenas para alinhamento teórico.

## 3. Correções de Infraestrutura
Durante a validação, detectamos que o comando `start /B` falhava no ambiente PowerShell do Gemini CLI (Exit Code 1).
- **Ação:** Refatoramos o comando para a sintaxe nativa do PowerShell:
  `Start-Process python -ArgumentList "C:\Projetos\Stout\wiki-compiler\brain-watcher.py" -NoNewWindow`
- **Resultado:** O `brain-watcher` agora inicia corretamente em background sem travar o terminal.

## 4. Lições Aprendidas
- **Sintaxe de Shell:** Comandos de infraestrutura dentro de skills devem ser compatíveis com PowerShell para evitar falhas silenciosas no Windows.
- **Cache de Skill:** O CLI pode demorar a refletir mudanças físicas em skills na mesma sessão; a leitura direta via `read_file` é o teste de verdade.
- **Higiene de Contexto:** Menos instruções no prompt inicial resultam em raciocínios mais rápidos e focados.

---
*Walkthrough gerado automaticamente e promovido para a documentação do projeto.*
