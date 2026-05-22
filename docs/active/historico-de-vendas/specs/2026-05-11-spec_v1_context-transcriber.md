# Spec: Context Transcriber (v1)

- **ID:** 2026-05-11-context-transcriber
- **Versão:** 1.0.0
- **Status:** Aprovado
- **Autor:** Gemini CLI (Arquiteto de Integração)

## 1. Objetivo
Migrar e evoluir a infraestrutura de transcrição centralizada para uma skill agêntica e contextual (`context-transcriber`). A skill deve automatizar a transcrição de áudios diretamente dentro dos diretórios de projeto, utilizando o contexto local (arquivos e termos do projeto) para aumentar a fidelidade terminológica da rede neural Whisper.

## 2. Requisitos

### 2.1. Requisitos Funcionais (RF)
- **RF01 (Discovery):** Listar arquivos na raiz do projeto para extrair vocabulário técnico.
- **RF02 (Injection):** Alimentar o parâmetro `initial_prompt` do Faster-Whisper com o vocabulário extraído.
- **RF03 (Transcription):** Transcrever áudios locais em formatos comuns (m4a, mp3, wav).
- **RF04 (Refinement):** Realizar pós-processamento via LLM para correção de erros gramaticais e de contexto.
- **RF05 (Governance):** Criar e salvar outputs em `docs/transcricao/`.
- **RF06 (Naming):** Seguir o padrão `YYYY-MM-DD_[Projeto-Assunto]_FULL.md`.

### 2.2. Requisitos Não-Funcionais (RNF)
- **RNF01 (Performance):** Utilizar `faster-whisper` com quantização `int8` para balancear velocidade e precisão em CPU.
- **RNF02 (Portabilidade):** A skill deve ser auto-contida em `~/.gemini/skills/context-transcriber`.
- **RNF03 (Segurança):** Não enviar arquivos de áudio para nuvens públicas; processamento de áudio é 100% local.

## 3. Arquitetura
A skill operará como um wrapper em torno de scripts Python:
1. **Core:** `transcribe_with_context.py` (Cópia adaptada do script legado).
2. **Context Provider:** Módulo interno que lê o diretório atual via comandos de shell.
3. **Skill UI:** `SKILL.md` definindo triggers e interface de interação com o usuário.

## 4. Validação (Plano de Testes)
- **Teste 1:** Executar a skill no projeto `Historico-de-Vendas`.
- **Resultado Esperado:** Transcrição do áudio "Análise histórico de vendas - estoque.m4a" gerada em `docs/transcricao/` contendo termos técnicos como "Excel", "Estoque", "Histórico de Vendas" escritos corretamente.
- **Teste 2:** Verificar se a pasta `docs/transcricao` foi criada automaticamente caso estivesse ausente.

---
*Assinado: Gemini CLI | Framework Stout*
