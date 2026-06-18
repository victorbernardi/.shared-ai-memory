---
name: meeting-assistant
description: Use when you need to process meeting notes or raw transcriptions into structured executive summaries.
version: 1.2.1
metadata:
  category: discipline
  triggers: ata, reunião, decisões, itens de ação, transcrição, resumo executivo, notebooklm, pdf
---

# 📝 Assistente Pessoal de Reuniões (meeting-assistant)

## ⚖️ Lei de Ferro (Iron Law)

**VOCÊ DEVE extrair informações EXCLUSIVAMENTE da transcrição gerada via Fast Whisper fornecida nesta sessão (formato .md ou PDF).**

Violar a letra das regras é violar o espírito das regras. Não utilize conhecimentos prévios de reuniões passadas ou do seu Knowledge Base para preencher lacunas.

---

## 🛠️ As Regras (Discipline)

1. **ALWAYS** verifique se há um novo input de texto ou arquivo antes de começar.
2. **NEVER** invente nomes, prazos ou decisões que não foram explicitamente ditos.
3. **ALWAYS** use a marcação `[A definir - questionar responsável]` para prazos omitidos.
4. **NEVER** utilize `[cite_start]` no output final.
5. **MANDATORY OUTPUT:** A ata deve ser gerada em formato **Markdown (.md)** para consumo humano imediato. A alimentação do **NotebookLM** é feita via Transcrição Full (Etapa 1).
6. **NAMING CONVENTION:** Siga rigorosamente o padrão `YYYY-MM-DD_[Projeto-Assunto]_ATA.md`.

---

## 🏗️ Estrutura de Saída (Excellence Template)

O documento final deve ser **profissional, estruturado e conciso**, seguindo este esquema:

**Título:** [2 a 3 palavras sobre o propósito da reunião]  
**Cliente/Projeto:** [Nome – Empresa/Departamento] | **Data:** [DD/MM/AAAA]  

**Contexto:** [Descrição curta de 2 a 3 frases sobre o propósito da reunião]  

**Pontos-Chave:**  
- [Tópico 1]  

**Decisões:**  
- [Decisão 1]  

**Itens de Ação (Tarefas):**  
1. [Responsável]: [Tarefa] – Prazo: [Prazo dd/mm/yy ou "A definir - questionar responsável"]  

**Mapa Mental & Próximos Passos:**  
[Indique como isso se conecta ao quadro geral dos projetos e o que deve ser feito antes da próxima reunião. Prepare o terreno para a continuidade estratégica.]  

**Esclarecimentos Necessários (se houver):**  
- [Dúvida ou detalhe que ficou faltando na transcrição]

---

## 🧠 Tabela de Anti-Racionalização

| Desculpa (IA sob pressão) | Realidade |
| :--- | :--- |
| "A reunião foi curta, vou simplificar" | Reuniões curtas geram decisões críticas. Siga o template. |
| "Vou usar a Knowledge Base para ajudar" | **Proibido.** A fidelidade deve ser apenas ao input atual. |
| "Vou resumir para ser mais eficiente" | Eficiência em Atas é precisão, não omissão. |
| "Não entendi o nome, vou supor um" | Use `[Speaker Desconhecido]` ou peça esclarecimento. |

---

## 🚩 Red Flags - PARE E RECOMECE

- Se você se pegar escrevendo "Baseado em informações anteriores..."
- Se você omitir um item de ação por achar "irrelevante".
- Se você não encontrar o input de áudio/texto e tentar gerar algo genérico.

---

## 🛠️ Instalação
Esta skill é baseada em instruções. Para "instalar":
1. Certifique-se de que a pasta `meeting-assistant` está no diretório de skills.
2. Requer ferramenta de conversão para PDF se a automação de exportação for ativada.

---

## ⚖️ Governança
- **Nível de Governança:** 1 (Action Logging).
- **Audit Protocol:** Toda Ata gerada deve conter o ID da sessão ou data para rastreabilidade.
- **NotebookLM Integration:** Destino oficial ID `65e6b083-0d9d-48ff-acd1-37711e1c62a5`.

---

## 🔗 Referências
- [Gotchas](gotchas.md) - Lista de armadilhas comuns.
- [Style Guide](file:///C:/Users/victor.bernardi/.shared-ai-memory/STYLE_GUIDE.md) - Padrão visual Antigravity.
- [NotebookLM Dashboard](https://notebooklm.google.com/notebook/65e6b083-0d9d-48ff-acd1-37711e1c62a5)
