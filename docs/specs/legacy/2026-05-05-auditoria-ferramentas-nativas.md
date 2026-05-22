# Especificação: Auditoria de Integridade de Ferramentas Nativas (v1.0)

## 1. Objetivo
Validar a precisão do mapeamento de ferramentas documentado em `gemini-tools.md` contra a API real disponível no Gemini CLI. O objetivo final é garantir que o agente utilize comandos funcionais e que a documentação reflita a realidade técnica do ambiente Stout.

## 2. Requisitos

### Funcionais
- Testar a existência e funcionalidade de ferramentas de leitura (`view_file`).
- Testar a existência e funcionalidade de ferramentas de escrita (`write_to_file`).
- Testar a existência e funcionalidade de ferramentas de edição (`replace_file_content`, `multi_replace_file_content`).
- Testar ferramentas de navegação e busca (`list_dir`, `grep_search`).
- Testar execução de comandos (`run_command`).
- Validar se nomes alternativos sugeridos (aliases) como `read_file` ou `write_file` são reconhecidos pelo sistema.

### Não-Funcionais
- **Segurança:** Realizar testes de escrita apenas em arquivos temporários na pasta `./scratch/` ou arquivos de teste dedicados.
- **Transparência:** Registrar o resultado (sucesso/falha/erro de sintaxe) para cada tentativa.
- **Disciplina Stout:** O teste deve ser conduzido via plano de estratégia aprovado.

## 3. Arquitetura de Teste
O teste será dividido em três baterias:
1.  **Bateria A (Documentada):** Execução dos comandos exatamente como constam no `gemini-tools.md`.
2.  **Bateria B (Aliasing):** Tentativa de execução de comandos com nomes simplificados/alternativos.
3.  **Bateria C (Metadata):** Verificação de flags obrigatórias e comportamento de retorno.

## 4. Validação (Plano de Testes)
O objetivo será considerado atingido quando:
- For gerada uma tabela comparativa com Status (Funcional / Erro / Alias).
- As discrepâncias forem identificadas com mensagens de erro reais do CLI.
- (Opcional) A documentação `gemini-tools.md` for corrigida para refletir os achados.

---
*Data: 2026-05-05*
*Status: Aprovado via Brainstorming*
