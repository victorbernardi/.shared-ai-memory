# Spec: Blindagem via Junctions e Ponto Único de Verdade (v7)

## 1. Objetivo
Implementar uma infraestrutura de arquivos que garanta a centralização absoluta da documentação (`docs/`) através de Junctions, eliminando a fragmentação física e garantindo que qualquer agente ou ferramenta, independente do contexto, escreva no repositório central em `.shared-ai-memory`.

## 2. Diagnóstico de Melhoria
A sugestão do usuário de usar **Junctions** resolve a causa raiz da dispersão:
- **Eficiência:** Elimina a necessidade de scripts de "saneamento" ou regras complexas de caminhos absolutos.
- **Transparência:** Ferramentas que buscam caminhos legados (ex: `.antigravity/docs`) encontrarão os arquivos atualizados sem saber que estão em outro diretório.
- **Consistência:** Resolve o "Problema de Três Corpos" documental de forma nativa no sistema de arquivos (NTFS).

## 3. Arquitetura de Junctions
- **Fonte (Master):** `C:\Users\victor.bernardi\.shared-ai-memory\docs\`
- **Alvos (Junctions):**
  - `C:\Users\victor.bernardi\.antigravity\docs` -> Aponta para o Master.
  - `C:\Motores-LLM\antigravity\docs` -> Aponta para o Master.

## 4. Riscos e Mitigações
- **Risco de Exclusão:** Excluir a pasta alvo (`.antigravity/docs`) antes de criar o junction. 
  - *Mitigação:* O backup já foi realizado na v6.
- **Risco de Promoção (Golden Copy):** Tradicionalmente, `C:\Motores-LLM` é promovido via Canary. Para documentação, a "promoção" será instantânea.
  - *Mitigação:* Aceitável para documentos, pois evita a "Assimetria de Contexto" (o agente "no escuro" sobre o que foi decidido no Stout).

## 5. Plano de Validação
- **Teste de Transparência:** Criar um arquivo em `.antigravity/docs/test.md` e verificar se ele aparece instantaneamente em `.shared-ai-memory/docs/test.md`.

---
*Status: Spec v7 Refinada (Junction Architecture) | Pronto para Estratégia*
