# Especificação Técnica — Correção do Maestro M0 (Unificação de Grupos e Eleição de Representante)

> **Documento:** Especificação Técnica de Requisitos (v11.8)  
> **Status:** EM REVISÃO (Modo Read-Only)  
> **Referência:** Inova Pós-Venda / Motor de Identidade M0  
> **Data:** 2026-05-21  

---

## 1. OBJETIVO DO NEGÓCIO & CONTEXTO

O Motor de Identidade (M0) é a fundação analítica do pipeline `potencial-clientes` da Inova. Ele consolida clientes dispersos do ERP Protheus em grupos econômicos sob um único `ID_GRUPO_MAESTRO`. A integridade deste motor impacta diretamente o faturamento mapeado downstream nos motores M1-M5 (CEVAP, DNA, Potencial).

Recentemente, a transição para a v11.7 introduziu instabilidades críticas:
1. **Omissão da Camada C3 (Nome Exato):** A solda linguística exata foi omitida no grafo transitivo. Isso desmembrou grupos coesos como **PH COMERCIO** e **FERRO+** (perda de R$20M+ de potencial mapeado).
2. **Eleição Frágil de Representantes:** A escolha do líder do grupo baseou-se apenas na contagem bruta de cadastros (`value_counts()`) e na extração cega da primeira linha (`.iloc[0]`). Isso fez com que filiais insignificantes (ou registros incompletos) dessem nome aos mega-grupos corporativos.
3. **Isolamento de Mega-Grupos (Grupo Fantasma `00000152`):** A **VIX LOGISTICA S.A.** (raiz `00000152`, faturamento de R$20M+ disperso) foi ejetada do Grupo Águia Branca no filtro de mega-grupos e ficou sem arestas no grafo, gerando um registro fragmentado de apenas R$1.36M com `Grupo_Economico` vazio.

Esta especificação define as correções estruturais para sanar estas três causas raiz no `WeldEngine` e no script de lote `seo_ge_batch_v11_7.py`.

---

## 2. REGRAS DE NEGÓCIO AFETADAS

### R2.1 — A Camada C3 (SOLDA_NOME_EXATO)
* **Definição:** Clientes com o mesmo `NOME_DNA` e `PERFIL` (diferentes de vazio/nulo) pertencem ao mesmo grupo econômico.
* **Score:** 95.
* **Comportamento Esperado:** Deve injetar arestas bidirecionais no grafo transitivo para consolidar elos nominais fortes antes da fase de dissolução de mega-grupos.

### R2.2 — Eleição de Representante Multi-Fonte (Ecosystem Score)
* **Definição:** O representante de um grupo (líder de 14 dígitos) não pode ser selecionado às cegas (`.iloc[0]`). Ele deve ser o CNPJ completo com a maior atividade real no ecossistema de dados.
* **Fórmula do Score de Frequência:**
  $$\text{Score\_Frequencia} = N_{\text{SA1010}} + N_{\text{VO1010}} + N_{\text{VV1010}}$$
  Onde:
  * $N_{\text{SA1010}}$: Frequência de ocorrência do CNPJ no cadastro.
  * $N_{\text{VO1010}}$: Frequência de ocorrência do CNPJ em ordens de serviço (oficina/VO1).
  * $N_{\text{VV1010}}$: Frequência de ocorrência do CNPJ na frota (veículos/VV1).
* **Nome do Grupo:** O nome do grupo maestro deve ser a Razão Social original (`A1_NOME`) do representante eleito, sanitizada e sem sufixos de filiais secundárias, caso aplicável.

### R2.3 — Mapeamento Resiliente de Nós Isolados
* **Definição:** Nós que ficam órfãos ou sem arestas ativas após a dissolução de mega-grupos não podem resultar em `NaN` na atribuição do `CNPJ_GRUPO`.
* **Comportamento Esperado:** O batch deve mapear o `CNPJ_GRUPO` de nós sem componentes conexos ativas de volta ao seu `CNPJ_DNA` original de 8 dígitos de forma elegante, garantindo integridade cadastral de 100%.

---

## 3. CRITÉRIOS DE ACEITAÇÃO (AC)

* **AC-1 [GRAFO - CAMADA C3]:** O método `build_graph` em `welders.py` deve agrupar o cadastro por `NOME_DNA` e `PERFIL` e conectar nós idênticos com a estratégia `'C3:SOLDA_NOME_EXATO'`, gerando arestas ativas no log.
* **AC-2 [RANKING - VOTOS MULTI-FONTE]:** O script de lote deve agregar os caches locais de oficina (`PATH_VO1`), veículos (`PATH_VV1`) e cadastro (`PATH_SA1`), calculando o `score_frequencia` para cada CNPJ completo (`CNPJ_L` de 14 dígitos).
* **AC-3 [ELEIÇÃO - LÍDER REAL]:** No agrupamento de componentes do grafo, o líder de 14 dígitos eleito para o grupo econômico deve ser aquele com maior `score_frequencia`. A razão social desse líder dará nome ao grupo.
* **AC-4 [PRESERVAÇÃO - VIX LOGISTICA]:** A raiz `00000152` (VIX LOGISTICA) deve ser processada, mantendo sua correta representatividade no grupo mestre, e seu potencial consolidado não pode ser fragmentado.
* **AC-5 [VALIDAÇÃO - INTEGRIDADE]:** Nenhum ID de cliente no master final (`dataset_ouro_identidade`) pode conter `CNPJ_GRUPO` nulo ou vazio. A integridade cadastral de saída deve ser de 100%.

---

## 4. METRICAS & KPIs DE SUCESSO

| Métrica | Situação Atual (v11.7) | Alvo Esperado (v11.8) |
|---------|------------------------|-----------------------|
| `arestas_c3` | `0` | `> 0` (Restabelecida) |
| Representação VIX | Fragmentada / Vazia | Integrada / **VIX LOGISTICA S.A.** |
| Nomes de Grupos | Filiais incoerentes / Truncadas | Razão Social do Líder do Ecossistema |
| Registros com NaN | Presentes em falhas de mega-grupos | **0%** (Higiene Absoluta) |

---

## 5. HISTÓRICO DE ESPECIFICAÇÕES (NÃO SOBRESCREVER)
* `2026-05-08-ecossistema-maestro-v10.md` (v10 original)
* `2026-05-11-spec-shared-sync-v11-7.md` (v11.7 de transição)
* `2026-05-12-delta-qsa-scanner.md` (Crawler QSA automático)
