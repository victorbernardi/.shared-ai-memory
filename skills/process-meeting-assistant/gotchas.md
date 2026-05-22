# ⚠️ Gotchas: meeting-assistant

Este documento lista as armadilhas comuns e comportamentos de falha que agentes de IA costumam apresentar ao processar reuniões.

## 1. O Gotcha da "Preguiça de Contexto"
**Sintoma:** A IA começa a resumir excessivamente a partir do meio da transcrição.
**Causa:** Limite de tokens ou pressão por velocidade.
**Como Evitar:** A IA deve processar a transcrição em blocos mentais e garantir que a seção de "Decisões" contenha TODOS os acordos feitos, não apenas os últimos.

## 2. O Gotcha do "Ajudante Inventivo"
**Sintoma:** A IA sugere "Próximos Passos" que não foram discutidos.
**Causa:** Treinamento base da IA tentando ser prestativa (helpful).
**Como Evitar:** Toda sugestão que não estava no áudio deve estar CLARAMENTE marcada na seção "Mapa Mental" como *[Sugestão da IA - Não discutido]*.

## 3. O Gotcha do "Speaker Mapping"
**Sintoma:** A IA confunde quem disse o quê em reuniões com muitas pessoas.
**Causa:** Falta de diarização clara no áudio bruto.
**Como Evitar:** Se houver dúvida sobre o orador, use a lógica de eliminação ou marque como `[Responsável a confirmar]`. Nunca atribua uma tarefa a alguém se houver 1% de dúvida.

## 4. O Gotcha da "Alucinação Silenciosa"
**Sintoma:** A IA remove termos técnicos complexos ou siglas que não conhece.
**Causa:** Filtro de clareza do modelo de linguagem.
**Como Evitar:** Termos técnicos e siglas DEVEM ser mantidos exatamente como no original. Se a IA não souber o significado, deve listar na seção "Esclarecimentos Necessários".

---
*Mantenha este documento atualizado a cada falha detectada.*
