# Plan v3: Correção e Estabilização do Pipeline de Atas (ATA)

**Goal:** Corrigir a falha na geração de Atas Executivas (ATA) no script `transcribe.py` e validar a integração com o Gemini CLI no Windows.

---

## 📋 Lista de Tarefas (Bite-Sized)

### 1. Preparação & TDD (Fase de Falha)
- [ ] Criar `tests/test_gemini_integration.py` para reproduzir o erro.
- [ ] Executar o teste e confirmar a falha (esperado: `None` ou erro de execução).

### 2. Implementação da Correção
- [ ] Modificar `transcribe.py`: adicionar `shell=True` na chamada `subprocess.run` do Gemini CLI.
- [ ] Melhorar o tratamento de erros na função `generate_ata_gemini` para imprimir `stderr` em caso de falha.
- [ ] Ajustar o regex de limpeza do JSON para maior resiliência.

### 3. Validação & Verificação
- [ ] Executar `tests/test_gemini_integration.py` e confirmar sucesso.
- [ ] Executar `tests/test_hash.py` para garantir que não houve regressão no core.

### 4. Reprocessamento (Recovery)
- [ ] Forçar o reprocessamento manual dos arquivos de 2026-05-05 no log ou deletar as entradas de sucesso temporariamente para que o script gere as ATAs faltantes.
- [ ] Verificar a existência das ATAs em `transcriptions/summaries/`.

---

## ⚠️ Travas de Segurança
- **Backup:** O script já utiliza hashing, então o reprocessamento não afetará os arquivos MD/PDF já gerados se não forem deletados, mas a lógica de skip baseada no hash deve ser considerada.
- **Ambiente:** Manter caminhos absolutos conforme padrão do projeto.

---
*Status: Aguardando /build*
