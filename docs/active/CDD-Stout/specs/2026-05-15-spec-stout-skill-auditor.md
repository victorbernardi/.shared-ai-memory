# 📑 Especificação Técnica: stout-skill-auditor (Tier 3 Porteiro)

> **Status:** Aprovado (Brainstorming Concluído)
> **Data:** 2026-05-15
> **Versão:** 1.0.0

---

## 1. Objetivo

O `stout-skill-auditor` atua como o "Porteiro" do Ecossistema Stout. Inspirado na profundidade da `skill-sentinel` mas focado estritamente na fase de *concepção* (pré-código), seu objetivo é evitar a proliferação de skills ambíguas, duplicadas ou com sobreposição de escopo. Ele decide, com base em metadados semânticos e consultas ao `stout-skill-registry`, se uma nova intenção de skill deve resultar em uma **criação do zero**, na **melhoria de uma skill existente** ou se deve ser **rejeitada**.

## 2. Requisitos

### 2.1 Funcionais (RF)

- **RF01 (Coleta de Intenção):** O auditor deve receber o nome proposto, o papel (role), os gatilhos (triggers) e uma descrição do comportamento esperado.
- **RF02 (Integração com Registry):** Deve consultar obrigatoriamente o `registry.json` (através dos scripts do `stout-skill-registry`) para listar todas as skills ativas e seus metadados.
- **RF03 (Cálculo de Sobreposição Semântica):** Deve analisar a intenção proposta contra as skills existentes.
  - Se a similaridade for alta (ex: > 80%), rejeitar a criação e recomendar melhoria.
  - Se a similaridade for moderada (ex: 40-80%), pausar para avaliação humana (questionamento de fronteiras).
  - Se a similaridade for baixa (ex: < 40%), emitir aprovação para criação.
- **RF04 (Emissão de Veredito):** O resultado da auditoria deve ser consolidado em um artefato `audit_result.json` com os campos: veredito (APPROVED, QUESTIONED, REJECTED), metadados propostos e justificativas.
- **RF05 (Prevenção de Execução Direta):** A `stout-create-skill` deve ser bloqueada se não houver um `audit_result.json` válido com o status "APPROVED".

### 2.2 Não-Funcionais (RNF)

- **RNF01 (Velocidade):** A análise deve ser rápida, pois é um bloqueio (gate) no processo de ideação.
- **RNF02 (Rastreabilidade):** As justificativas para rejeições devem ser claras, preferencialmente apontando qual skill existente já resolve o problema, permitindo um roteamento rápido para a `stout-improve-skill`.
- **RNF03 (Isolamento):** O auditor não cria pastas ou arquivos da nova skill, apenas emite um laudo.

## 3. Arquitetura do Auditor

### 3.1 Estrutura da Skill

```text
skills/stout-skill-auditor/
├── SKILL.md                  # Regras de auditoria e fluxos de decisão
├── config/
│   ├── similarity_threshold.yaml # Definições dos thresholds de pontuação
│   └── role_definitions.yaml     # Papéis primários definidos no ecossistema
├── scripts/
│   ├── semantic_overlap.py       # Script principal de análise comparativa
│   └── role_conflict_checker.py  # Verifica se o 'role' proposto conflita diretamente
└── references/
    ├── decision_criteria.md      # Como decidir: criar vs melhorar vs rejeitar
    └── overlap_examples.md       # Casos reais de sobreposição para treinar o agente
```text

## 4. Integração do Ecossistema

1.  **Usuário/Ideia:** Apresenta a intenção de criar uma skill.
2.  **stout-skill-auditor:** Processa a ideia contra o `stout-skill-registry`.
3.  **Saída 1 (APPROVED):** A ideia avança para a `stout-create-skill`.
4.  **Saída 2 (REJECTED/QUESTIONED):** A ideia é desviada para a `stout-improve-skill` para refatorar a skill que já detém aquele contexto.

## 5. Padrões Inspirados na `skill-sentinel`

Enquanto o `skill-sentinel` analisa o código-fonte existente (pós-facto) com uma arquitetura de múltiplos analisadores (segurança, performance, qualidade), o `stout-skill-auditor` atua *antes do código* (pré-facto) com foco na arquitetura semântica e governança de metadados CDD. Em um roadmap futuro (Tier 5), a validação de código profunda do Sentinel poderá ser acoplada à homologação final.

---
*Assinado: Arquiteto Stout Inova*