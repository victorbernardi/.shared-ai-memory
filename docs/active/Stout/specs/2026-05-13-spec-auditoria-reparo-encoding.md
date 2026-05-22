# Spec: Auditoria e Reparo de Encoding (Stout Shield)

**Status:** Draft  
**Data:** 2026-05-13  
**Autor:** Gemini CLI (Arquiteto de Design Agêntico)

---

## 1. Objetivo
Sanitizar o ecossistema Stout contra corrupção de caracteres, garantindo que todos os arquivos `.md` sigam o padrão **UTF-8 (sem BOM)** e reparando diagramas de árvore e acentuações quebradas por interpretações errôneas de ANSI/Windows-1252.

## 2. Requisitos Funcionais

### 2.1 Detecção (Auditoria)
- Varredura recursiva de arquivos `.md` (ignora `.git`, `venv`, `node_modules`).
- Identificação de arquivos codificados em ANSI/ISO-8859-1.
- Identificação de padrões de "Double UTF-8" (ex: `á` em vez de `á`, `├` em vez de `├`).

### 2.2 Reparo (Remediação)
- Conversão automática de ANSI para UTF-8.
- Reversão de padrões de corrupção conhecidos:
    - Acentuação (PT-BR e outros idiomas).
    - Diagramas de Árvore (Box Drawing characters).
- Preservação de quebras de linha e estrutura original.

### 2.3 Prevenção (Stout Shield)
- Sugerir integração no `markdown-auto-fixer` para impedir novas corrupções.
- Configuração de `.editorconfig` recomendada.

## 3. Arquitetura Proposta

### Componente: `encoding_fixer.py`
Um script utilitário que realiza o reparo em duas passagens:
1. **Passagem de Normalização:** Converte bytes ANSI para strings UTF-8.
2. **Passagem de Sanitização:** Aplica regex/mapeamento para corrigir sequências de bytes UTF-8 que foram salvas como se fossem caracteres ANSI.

## 4. Plano de Validação (DoD)
- [ ] O script `audit_encoding.py` deve retornar "Nenhum problema detectado" após a execução do reparo.
- [ ] O arquivo `2026-05-06-api-scraper-spec.md` (ANSI) deve ser legível como UTF-8 puro.
- [ ] O arquivo `SECURITY_GUARDRAILS.vi.md` (Corrompido) deve recuperar a legibilidade dos caracteres vietnamitas e emojis.
- [ ] Diagramas de árvore em arquivos de walkthrough devem exibir `├`, `─`, `└` corretamente.

## 5. Riscos e Mitigações
- **Falsos Positivos:** Caracteres que parecem corrupção mas são legítimos em outros idiomas.
    - *Mitigação:* Focar em sequências específicas de 2-3 bytes típicas de corrupção UTF-8/ANSI.
- **Perda de Dados:** Erro na conversão de bytes.
    - *Mitigação:* Criar backup `.bak` automático antes de sobrescrever qualquer arquivo.
