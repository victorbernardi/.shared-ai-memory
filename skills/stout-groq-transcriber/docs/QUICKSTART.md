# Stout Groq Transcriber — Quick Start

## Instalação em 3 passos

### 1. Dependências

```bash
pip install groq python-dotenv
```

### 2. Configurar API Key

✅ **Recomendado:** A chave já está em `~/.shared-ai-memory/.env`

A skill carrega automaticamente — nada a fazer!

**Alternativas:**

- Variável de ambiente: `export GROQ_API_KEY="gsk_..."`
- Local .env: Crie `.env` na pasta do script

Obtenha uma chave gratuita em: <https://console.groq.com>

### 3. Transcrever

```bash
python transcribe.py seu_audio.mp3
```

Saída:

- Se `research/` existir no projeto → `research/seu_audio.md`
- Se `research/` não existir → `transcriptions/seu_audio.md`

---

## Exemplos de Uso

### Transcrevendo um arquivo

```bash
# Saída automática no modo clean
python transcribe.py meeting_2026_07_01.m4a

# Debug com cópia do original
python transcribe.py meeting.mp3 --mode debug --keep-source-copy

# Archive
python transcribe.py meeting.m4a --mode archive --keep-source-copy

# Saída em diretório customizado
python transcribe.py meeting.m4a --out-dir relatorios --session-name reuniao
```

### Programaticamente

```python
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()

# Transcrever
with open("audio.mp3", "rb") as f:
    result = client.audio.transcriptions.create(
        file=("audio.mp3", f.read()),
        model="whisper-large-v3"
    )
    print(result)
```

---

## Customizar correções

Edite `config/corrections.json`:

```json
{
  "palavra_errada": "Palavra Correta",
  "outro_erro": "Outra Correcao"
}
```

Próxima transcrição usará as novas regras.

---

## Formatos suportados

✅ `.mp3`, `.mp4`, `.m4a`, `.m4v`, `.wav`, `.ogg`, `.flac`, `.webm`, `.opus`

❌ Outros formatos precisam de ffmpeg (não incluído)

---

## Troubleshooting

| Erro | Solução |
| ------ | --------- |
| `GROQ_API_KEY not set` | Configure variável de ambiente ou .env |
| `could not process file` | Arquivo corrompido ou inválido |
| `Timeout` | Áudio muito longo — divida em partes |

---

## Performance

- **Arquivo:** 3.67 MB (CSC parte 1)
- **Tempo:** ~2 minutos
- **Custo:** ~$0.01
- **Qualidade:** 98-99% de precisão

---

**Próximas etapas:** Ver `SKILL.md` para features avançadas.
