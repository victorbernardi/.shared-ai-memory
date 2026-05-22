# 📐 Spec: Pipeline de Transcrição Industrial (v3.1)

**Status:** Em Auditoria | **Links:** [SOW v3](file:///C:/Projetos/Transcricoes/docs/specs/sow_v3_transcricao_industrial.md)

---

## 1. Requisitos Funcionais (Functional Requirements)

| ID | Descrição | Implements |
|:---|:---|:---:|
| **FR-001** | Implementar gerador de hash MD5 por arquivo. | AC-1 |
| **FR-002** | Criar engine de log JSON persistente em `/logs/`. | AC-3 |
| **FR-003** | Integrar normalização FFmpeg (16kHz, Mono). | AC-4 |
| **FR-004** | Implementar rotina de compressão FLAC e deleção. | AC-2 |
| **FR-005** | Desenvolver validação de paridade (Duração vs Segmentos). | AC-5 |

---

## 2. Cenários de Teste (Test Scenarios)

| ID | Cenário | FR Relacionado |
|:---|:---|:---:|
| **T-001** | Iniciar áudio novo e verificar criação de hash no JSON. | FR-001, FR-002 |
| **T-002** | Re-executar o mesmo áudio e confirmar que o sistema o ignora. | FR-001 |
| **T-003** | Verificar se o arquivo original foi removido após o FLAC. | FR-004 |
| **T-004** | Simular áudio truncado e verificar falha na validação tripla. | FR-005 |

---

## 3. Matriz de Rastreabilidade

| AC | FR | Teste | Status |
|:---|:---|:---|:---:|
| AC-1 | FR-001 | T-001, T-002 | ⏳ Pendente |
| AC-2 | FR-004 | T-003 | ⏳ Pendente |
| AC-3 | FR-002 | T-001 | ⏳ Pendente |
| AC-4 | FR-003 | Manual | ⏳ Pendente |
| AC-5 | FR-005 | T-004 | ⏳ Pendente |

---
*Status: Aguardando Validação Final*
