# 🧠 Lições Aprendidas e Evolução do Sistema

Este documento registra o aprendizado contínuo do projeto, capturando erros, correções e preferências do usuário para guiar sessões futuras.

---

## 1. PREFERÊNCIAS DO USUÁRIO (O QUE FUNCIONA)
- **Infraestrutura Existente Primeiro:** Sempre priorizar MCPs locais já configurados (`notebooklm-mcp.exe`) em vez de reconstruir integrações manuais via API/Tokens.
- **Transparência e Organização:** Arquivos devem ter pastas claras (`src`, `data`, `scripts`, `docs`) e ativos processados devem ser arquivados em `data/archived`.
- **Manifestos Padronizados:** Uso de arquivos JSON como única fonte da verdade para entradas em lote.

---

## 2. FALHAS E CORREÇÕES (LOG DE APRENDIZADO)

### Falha A: Negligência na Validação (TDD)
- **Erro:** Considerar o deploy como "concluído" após a execução do script sem realizar uma auditoria rigorosa no destino final (NotebookLM).
- **Causa:** Otimismo excessivo e quebra do protocolo Antigravity.
- **Correção:** Implementação de script de auditoria via MCP para contar fontes no Notebook e geração de `error_report.json`.
- **Aprendizado:** **Deploy sem validação é apenas uma tentativa.** A confirmação deve ser técnica e baseada em dados.

### Falha B: Substituição de MCP por Script Customizado
- **Erro:** Ignorar o MCP configurado no `settings.json` e tentar criar um wrapper REST do zero.
- **Causa:** Falha na leitura inicial do contexto do projeto e falta de teste de ferramentas existentes.
- **Correção:** Pivotagem estratégica para usar o executável local do MCP como backend do script Python.
- **Aprendizado:** Verifique as ferramentas do MCP antes de escrever código. Se o MCP existe, ele é a via preferencial.

---

## 3. MELHORIAS PARA A SKILL `STOUT-INIT`
- **Scaffolding de Automação:** Incluir automaticamente um `template_sources.json` e um `README_STOUT.md` em novos projetos.
- **Pre-flight Checks:** Adicionar um passo de validação de rede para detectar bloqueios (403/404) antes de iniciar execuções em massa.
- **Modularidade de Ingestão:** Criar uma classe base de `Uploader` que suporte `url`, `youtube` e `file` nativamente.

---

## 4. MELHORIAS PARA O `GEMINI.MD`
- Adicionar sempre uma seção de **"Observabilidade"** listando onde ficam os arquivos de erro e log persistentes.
- Vincular o sucesso de cada **Próxima Ação** a uma evidência de validação específica.

---

## 5. CONCLUSÃO PARA PRÓXIMAS SESSÕES
O agente deve agir como um **Operador de Sistemas**, priorizando a estabilidade e a prova de sucesso sobre a velocidade de implementação. **Confie nos MCPs, valide cada upload.**
