---
name: canary-deployment
description: "Protocolo de segurança para proteção de arquivos críticos. Ativa automaticamente antes de salvar modificações em motores Inova/Stout ou configurações globais."
risk: safe
source: custom
date_added: "2026-04-28"
---

# Canary Deployment — Proteção de Sistema (Fast Edition)

Este protocolo substitui a criação manual de arquivos `.stable.*` por uma abordagem de **Checkpoints de Integridade** para manter a fluidez do agente.

## Quando Usar
Ativar obrigatoriamente antes de modificar arquivos nos domínios:
- `C:\Motores-LLM\antigravity\skills\**`
- `C:\Projetos\Stout\**` (Motores e Lógica)
- `C:\Projetos\Inova\**` (Engines de Cálculo)
- Qualquer arquivo de configuração `.json`, `.toml` ou `.yaml` de sistema.

---

## O Protocolo "Fast Canary"

### Passo 1 — Checkpoint Preventivo
Antes de aplicar qualquer `replace` ou `write`, o agente deve garantir que o estado atual está seguro.
- **Se em repo Git:** Verifique se há alterações pendentes. Se houver, avise o usuário.
- **Se fora de Git:** Utilize a memória da sessão para registrar o estado original ("Snapshot") caso precise reverter.

### Passo 2 — Apresentação da Mudança (Visual Diff)
O agente **DEVE** apresentar a mudança proposta de forma clara antes de executá-la, usando o formato:

```
═══════════════════════════════════════════════════
CANARY ATIVO: <caminho do arquivo>
═══════════════════════════════════════════════════
```
Apresente o bloco de código ANTES e DEPOIS no prompt.

### Passo 3 — Aprovação Humana
Aguarde o "S" (Sim) ou "N" (Não) do Victor antes de realizar a escrita física no disco.

### Passo 4 — Registro de Auditoria
Após a promoção bem-sucedida, registre a ação em `C:\Users\victor.bernardi\.gemini\antigravity\diary\canary-log.md`:
`YYYY-MM-DD | <arquivo> | AÇÃO: promovido | <breve descrição>`

---

## Regras de Ouro
1. **Pequenos Passos:** Nunca tente fazer um canary de 500 linhas de uma vez. Quebre em edições atômicas.
2. **Reversão Imediata:** Se o Victor disser "N", descarte a proposta e retorne ao estado de plano.
3. **Log é Sagrado:** O `canary-log.md` deve ser mantido atualizado para rastreabilidade de falhas.
