# SOW: Upgrade de Pipeline Industrial

**ID** | **Critério de Aceitação (AC)** | **Sinal Observável (Sucesso)**
:---|:---|:---
AC-1 | O sistema deve evitar reprocessar áudios já transcritos. | O sistema pula o arquivo e loga "Skipped".
AC-2 | O sistema deve reduzir o espaço em disco ocupado pelos áudios. | Arquivo original deletado e substituído por .flac.
AC-3 | Todo processamento deve deixar um rastro auditável. | Arquivo JSON atualizado com hash MD5 e data.
AC-4 | A transcrição deve ser otimizada para acurácia máxima. | Áudio normalizado para 16kHz mono antes do Whisper.
AC-5 | O sistema deve garantir que o arquivo final não está corrompido. | Validação tripla (Técnica/Conteúdo/Status) aprovada.

---
*Referência: SOW-TR-V3-2026*
