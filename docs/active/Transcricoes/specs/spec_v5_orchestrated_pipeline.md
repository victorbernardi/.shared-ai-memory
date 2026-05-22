# Spec v5: Pipeline de Orquestração Única (UAP v3)

**Status:** Approved (Brainstorming Complete)
**Data:** 2026-05-05
**Autor:** Gemini CLI (Stout Engine)

## 1. Objetivo
Refatorar o sistema de transcrições para separar o processamento técnico local da inteligência agêntica. O agente assume a orquestração de background e a geração de Atas via skill especializada.

## 2. Requisitos Funcionais
- **RF1 (Python):** O script `transcribe.py` deve processar áudios em lote, gerar MD/PDF FULL e registrar sucesso no `transcription_log.json`.
- **RF2 (Python):** O script NÃO deve conter chamadas ao Gemini CLI ou subprocessos de IA.
- **RF3 (Agente):** O agente deve disparar o processamento em background.
- **RF4 (Agente):** O agente deve monitorar o log e, para cada novo FULL gerado, produzir a ATA via skill `meeting-assistant`.

## 3. Arquitetura Proposta
- **Camada Técnica:** Python 3 + Faster-Whisper + FFmpeg (Execução Local).
- **Camada de Governança:** JSON Log (Fonte da Verdade para o status).
- **Camada Inteligente:** Gemini CLI (Eu) + Skill `meeting-assistant` (Orquestração e Síntese).

## 4. Plano de Validação (TDD)
- **Teste 1:** Validar se o `transcribe.py` (refatorado) não possui referências ao Gemini CLI.
- **Teste 2:** Simular um registro de sucesso no log e verificar se o agente inicia a geração da ATA corretamente.
- **Teste 3:** Validar a persistência da ATA na pasta `/summaries/` seguindo a nomenclatura padrão.

---
*Documento gerado sob governança Stout.*
