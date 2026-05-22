# 🔬 LABORATÓRIO DE PESQUISA — Motor CEVAP

> **Objetivo:** Auditoria de Causa Raiz e Testes de Hipóteses
> **Status:** Ativo (05/05/2026)

---

## 1. INVESTIGAÇÃO: SKAVA E PONTUAL (Grandes Clientes)

### Hipótese: Erro de Join ou Inatividade Real?
- **SKAVA (03353341):** Localizada na base M5. Última venda registrada no M3 em **02/10/2025**. Inatividade calculada: **215 dias**.
- **PONTUAL (12292478):** Localizada na base M5. Última venda registrada no M3 em **09/08/2025**. Inatividade calculada: **269 dias**.

### Conclusão Empírica
Os clientes estão na lista **corretamente** conforme a regra de negócio (Inatividade > 90 dias). Não houve erro de processamento; o dado reflete uma inatividade real no sistema de faturamento M3 para esses CNPJs Raiz.

---

## 2. AUDITORIA DE COLUNAS (FIDELIDADE DE DADOS)

### Colunas Preservadas do M5:
- `CNPJ_GRUPO_ID` (agora como `CNPJ_GRUPO`)
- `Grupo_Economico`
- `Status_Fidelidade`
- `Potencial Total`
- `SOW_Total_Auditado`
- `Fat_Contido_Total`
- `GAP_Total`
- `Qtd_Maquinas`
- `Horimetro_Medio`
- *(E todas as demais 18 colunas originais do dataset estrategico v1)*

---

## 3. PONTOS DE FALHA IDENTIFICADOS (SANEAMENTO)

| Ponto de Falha | Impacto | Ação de Bloqueio |
| :--- | :--- | :--- |
| **Arquivo Aberto** | Falha na geração do Excel. | Implementado versionamento por **Timestamp** (`YYYYMMDD_HHMM`). |
| **Divergência de Tipos** | Match Rate 0% em joins. | Forçada conversão para `str` e `strip()` em todas as chaves de join. |
| **Data/Hora no Excel** | Dificuldade de leitura. | Aplicado `.dt.date` para remover frações de tempo da `Ultima_Compra`. |

## 4. DESIGN DE ARQUITETURA V4 (MODELO HÍBRIDO)

### Decisão Estratégica: Grupo vs Filial
- **Problema:** Como equilibrar o potencial do grupo com a precisão operacional da filial?
- **Solução:** Gatilho de inatividade por **Grupo**, mas linha de ativação por **Filial (Maior Faturamento)**.
- **Vantagem:** Evita abordar filiais "fantasmas" ou irrelevantes do grupo, focando o esforço comercial onde o dinheiro circulava.

### Mapeamento de Grão (v4)
| Entidade | Grão | Justificativa |
| :--- | :--- | :--- |
| **Inatividade** | Grupo (8) | Evitar falsos-positivos se a matriz estiver ativa. |
| **CNPJ Ativação** | Filial (14) | Maior faturamento histórico (Opção A do Brainstorm). |
| **Seedz / InovaPay** | Grupo (8) | Centralização de recursos financeiros do grupo. |
| **Equipamentos** | Filial -> Grupo | Hierarquia de fallback para garantir cobertura. |
| **Orçamentos** | Filial (14) | Medir intenção de compra da unidade específica. |

---
*Este laboratório isola as investigações antes da promoção para o script de produção.*
