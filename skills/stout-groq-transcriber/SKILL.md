---
name: stout-groq-transcriber
version: 1.0.0
type: utility
category: transcrição
author: Claude Code (Stout)
created: 2026-07-01
description: Transcrição de áudio via Groq Whisper v3 + LLaMA, com limpeza automática e estruturação (summary + action items)
tags:
  - audio
  - transcription
  - groq
  - whisper
  - nlm
triggers:
  - transcribe audio
  - transcrever áudio
  - convert meeting to text
  - gerar transcrição
role: transcrição automática com estruturação
dependencies:
  - groq >= 1.5.0
  - python-dotenv >= 1.0.0
  - mutagen >= 1.48.0  # opcional, usado por format_report.py
status: active
---

# Stout Groq Transcriber

Skill para transcrição automática de áudio usando Groq Whisper v3 + modelo de limpeza configurável, com limpeza semântica automática e estruturação (Meeting Summary + Key Action Items). O pipeline segue ETL explícito: `run.py` orquestra `extract.py` → `transform.py` → `load.py`.

## Estrutura ETL

- `scripts/extract.py`: lê áudio, transcrição existente e metadados.
- `scripts/transform.py`: aplica correções, limpeza LLM, estruturação e renderização do relatório.
- `scripts/load.py`: grava os artefatos Markdown e cópias opcionais.
- `scripts/run.py`: coordena as etapas e expõe o entrypoint oficial; `transcribe.py` e `format_report.py` são wrappers compatíveis.

## O que faz

1. **Transcrição** via Groq Whisper Large v3 (rápido + preciso)
2. **Correção** via dicionário customizável (termos Inova, nomes próprios, etc)
3. **Limpeza** via modelo de chat Groq configurado por `GROQ_CLEANUP_MODEL` (padrão: `openai/gpt-oss-120b`)
4. **Estruturação** automática:
   - Meeting Summary (resumo interpretativo)
   - Transcrição completa formatada
   - Key Action Items (extraídos automaticamente)
5. **Relatório template (opcional)** via `run.py report` (ou o wrapper compatível `format_report.py`): reformata o output acima no template "Audio Transcription Report" (metadados + Meeting Minutes com Participants/Topics Discussed/Decisions Made/Action Items), sem re-transcrever o áudio — ver seção [Relatório no template audio-transcriber](#relatório-no-template-audio-transcriber)

## Qualidade

- **Precisão:** 98-99% (vs 70-80% Faster-Whisper)
- **Tempo:** ~2-3 minutos por 10min de áudio
- **Custo:** ~$0.02-0.03 por 10min (modelo v3)
- **Suporte:** Português (pt-BR), Inglês, outros idiomas via Groq

## Quando usar

✅ Transcrições de reuniões internas (CSC, alinhamentos, etc)  
✅ Documentação de processos (requer qualidade alta)  
✅ Análise de dados de áudio (requer precisão)  
✅ Captura de action items automática  

❌ Não usar para: áudio com muita distorção, ambiente muito barulhento, múltiplos falantes sem controle de qualidade

## Instalação

```bash
# Via stout-skill-manager (recomendado)
/stout-skill-manager create stout-groq-transcriber

# Direto
pip install groq python-dotenv
```

**Configuração de API Key:**

A skill busca a chave automaticamente em (nessa ordem):

1. Variável `Groq_API_Key` em `~/.shared-ai-memory/.env` ✅ (recomendado)
2. Variável `GROQ_API_KEY` em `~/.shared-ai-memory/.env`
3. `.env` local na pasta do script (para teste)
4. Variável de ambiente `GROQ_API_KEY`

Sua chave está configurada em: `~/.shared-ai-memory/.env`

## Uso

### Linha de comando

```bash
python scripts/run.py <audio> [--mode clean|debug|archive] [--out-dir DIR] [--session-name NAME] [--keep-source-copy]
```

**Modos:**

| Modo | Comportamento |
| --- | --- |
| `clean` (padrão) | Gera exatamente um `.md` em `research/<session>.md` ou `transcriptions/<session>.md` |
| `debug` | Isola todos os artefatos sob `transcriptions/<session>/debug/` |
| `archive` | Isola sob `transcriptions/<session>/archive/<timestamp>/` |

**Exemplos:**

```bash
# Clean — saída padrão (modo default)
python scripts/run.py meeting.mp3
# → research/meeting.md  (se research/ existe)  ou  transcriptions/meeting.md

# Debug
python scripts/run.py meeting.m4a --mode debug --keep-source-copy

# Archive
python scripts/run.py meeting.m4a --mode archive --keep-source-copy

# Saída em diretório customizado
python scripts/run.py meeting.m4a --out-dir ~/meus-relatorios

# Nome de sessão customizado
python scripts/run.py meeting.m4a --session-name reuniao-2026-07-09
```

### Via skill

```python
from stout_groq_transcriber import TranscriberPipeline

pipeline = TranscriberPipeline(
    api_key="gsk_...",
    corrections_dict={
        "Arca": "Arka",
        "CRC": "CRC",  # deixar como está
    }
)

result = pipeline.transcribe("audio.m4a")
print(result.summary)
print(result.action_items)
```

## Formatos suportados

Groq suporta nativamente:

- `.flac`, `.mp3`, `.mp4`, `.mpeg`, `.mpga`, `.m4a`, `.ogg`, `.opus`, `.wav`, `.webm`

Outros formatos são convertidos automaticamente via ffmpeg (se disponível).

## Dicionário de correções

Editar `config/corrections.json`:

```json
{
  "Arca": "Arka",
  "indopaycom": "Indopacom",
  "manutenção_preventiva": "manutenção preventiva",
  "MTBF": "MTBF"
}
```

Correções aplicadas **antes** da limpeza via LLM.

## Estrutura da saída

```
Meeting Summary: [resumo interpretativo em 2-3 linhas]

[Transcrição completa formatada em parágrafos]

Key Action Items
- [item 1]
- [item 2]
- [item 3]
```

## Relatório no template audio-transcriber

`run.py report` é um post-processor **opcional** e **separado** da transcrição: ele lê o `.txt`/`.md` já gerado (Meeting Summary + falas por Speaker + Key Action Items) e o reorganiza no template "Audio Transcription Report" da skill `audio-transcriber`, sem chamar o Whisper novamente. Precisa do arquivo de áudio original só para extrair metadados (tamanho e duração via `mutagen`) — não o retranscreve. `format_report.py` permanece como wrapper compatível.

```bash
python scripts/run.py report transcript.txt audio.m4a [output.md]
```

**Exemplo (fluxo completo):**

```bash
python scripts/run.py meeting.m4a --out-dir . --session-name meeting_transcript
python scripts/run.py report meeting_transcript.md meeting.m4a meeting_report.md
```

**Saída gerada:**

```markdown
# Audio Transcription Report

## 📊 Metadata
| Field | Value |
|-------|-------|
| **File Name** | ... |
| **File Size** | ... |
| **Duration** | ... |
| **Language** | Português (pt-BR) |
| **Processed Date** | ... |
| **Speakers Identified** | ... |
| **Transcription Engine** | Groq Whisper Large v3 + configured cleanup model |

## 📋 Meeting Minutes
### Participants
### Topics Discussed
### Decisions Made
### Action Items

## 📝 Transcrição Completa
[transcrição literal completa, preservada na íntegra]
```

**Dependência extra:** `mutagen` (extração de duração sem precisar de ffmpeg/ffprobe):

```bash
pip install mutagen
```

Se `mutagen` não estiver instalado, a Duration é reportada como "Desconhecida" e o restante do relatório é gerado normalmente.

## Configuração

**Via `.env`:**

```env
GROQ_API_KEY=gsk_...
GROQ_WHISPER_MODEL=whisper-large-v3
GROQ_CLEANUP_MODEL=openai/gpt-oss-120b
```

**Via `config/config.json`:**

```json
{
  "api_key": "${GROQ_API_KEY}",
  "whisper_model": "whisper-large-v3",
  "cleanup_model": "openai/gpt-oss-120b",
  "max_tokens": 4096,
  "temperature": 0.3
}
```

## Performance

| Arquivo | Duração | Tempo | Custo |
| --------- | --------- | ------- | ------- |
| Parte 1 (CSC) | ~3-4 min | ~2 min | ~$0.01 |
| Meeting típico | 30 min | ~10 min | ~$0.06 |
| Apresentação longa | 90 min | ~30 min | ~$0.18 |

## Troubleshooting

### Erro: "could not process file - is it a valid media file?"

- Arquivo corrompido ou HTML (não áudio)
- Solução: Re-fazer download da fonte

### Erro: GROQ_API_KEY não configurada

```bash
export GROQ_API_KEY="gsk_sua_chave_aqui"
# ou criar .env na pasta do script
```

### Transcrição incompleta

- Áudio muito longo (>20min contínuo pode ter limitação)
- Solução: Dividir em segmentos menores

## Roadmap

- [ ] v1.1: Suporte a diarização (múltiplos falantes automáticos)
- [ ] v1.2: API REST para integração
- [ ] v1.3: Batch processing para múltiplos arquivos
- [ ] v1.4: Dashboard de análise de transcrições
- [ ] v2.0: Armazenamento em banco com busca full-text

## Exemplos

Ver `docs/examples/` para amostras de uso.

## Referências

- [Groq Console](https://console.groq.com)
- [Groq API Docs](https://console.groq.com/docs)
- [Meeting Transcriber Repo](https://github.com/ben-arka/meeting-transcriber)

## Suporte

Dúvidas ou bugs? Abra uma issue no Stout ou contacte o time de Inteligência de Dados.

---

**Status:** ✅ Ativo | **Última atualização:** 2026-07-01
