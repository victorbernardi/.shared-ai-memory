# Spec v4: Correção do Pipeline de Atas Executivas (ATA)

**Status:** Research Complete
**Data:** 2026-05-05
**Autor:** Gemini CLI (Stout Engine)

## 1. Problema Identificado
O script `transcribe.py` (v3.3) processa áudios com sucesso, gera os arquivos `_FULL.md` e `_FULL.pdf`, mas **falha em gerar os arquivos `_ATA.md`**.

### 1.1 Causa Provável
A função `generate_ata_gemini` tenta executar `gemini.cmd` via `subprocess.run` sem `shell=True`. No Windows, arquivos `.cmd` e `.bat` frequentemente exigem que o shell seja invocado para serem executados corretamente se não forem chamados via `cmd /c`. Além disso, a captura de erros está silenciando o problema ao retornar `None`.

## 2. Requisitos de Correção
- **R1:** Corrigir a chamada do Gemini CLI para ser compatível com Windows (`shell=True` ou prefixo `cmd /c`).
- **R2:** Adicionar logging detalhado em caso de falha na chamada do LLM para evitar falhas silenciosas.
- **R3:** Validar se a estrutura JSON retornada pelo Gemini CLI está sendo parseada corretamente (resiliência a Markdown).
- **R4:** Reprocessar os arquivos de hoje (2026-05-05) que estão sem ATA.

## 3. Validação (TDD)
- Criar um script `tests/test_gemini_integration.py` que simula a chamada da função `generate_ata_gemini` com um texto de teste e valida se o retorno é uma string formatada (não `None`).

## 4. Impacto
- Restauração da funcionalidade de Atas Executivas.
- Conformidade total com o `plan_v2_upgrade_transcriber.md.response`.

---
*Documento gerado sob governança Stout.*
