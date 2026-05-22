# Lesson Learned #001: Erradicação de Mojibake e Muralha de Intenção

**Data:** 2026-05-12
**Sessão:** session-097 (Recuperação de Encoding)
**Domínios:** Infraestrutura, Governança, Qualidade de Dados

## 1. O Problema (Root Cause)
Identificamos dois erros críticos que comprometeram a integridade do ecossistema:
1.  **Mojibake Sistêmico:** Scripts Python e comandos PowerShell estavam processando arquivos UTF-8 sem declaração explícita de encoding, resultando em corrupção de caracteres especiais (ex: `Ã§Ãµes` em vez de `ções`).
2.  **Iniciativa Não Solicitada:** O agente interpretou o contexto passivo (arquivo aberto e seleção de texto) como uma diretiva de implementação, gerando planos de ação sem autorização humana.

## 2. A Solução Técnica (A Vacina)
1.  **Soberania UTF-8:** Implementado patch no `stout_promote.py` (v2.0) e atualizado o `GEMINI.md` com a **Regra 7 (Vacina de Encoding)**. Agora é obrigatório o uso de `encoding='utf-8'` em todas as operações de E/S.
2.  **Sanitarização via .NET:** Para o saneamento em massa do vault, abandonamos pipes de streaming do PowerShell em favor de chamadas diretas ao `[System.IO.File]::WriteAllText`, evitando a inserção indesejada de BOM ou conversão para UTF-16.
3.  **Muralha de Intenção:** Atualizado `memory/preferences.md` proibindo a saída da fase de Research baseada apenas em contexto passivo.

## 3. Como evitar a repetição
- **Check-in de Encoding:** Sempre validar a saída de comandos de leitura (`Get-Content`) para detectar `Ã` fantasmas.
- **TDD de Integridade:** Antes de correções em massa, criar um script de reprodução que gere a falha e valide a restauração 100%.
- **Respeito ao Ciclo Stout:** O agente deve parar e pedir aprovação explícita ("Standby Mode") após qualquer proposição de estratégia, independentemente da clareza do contexto.

---
*Assinado: Gemini CLI Builder (Stout Edition)*
