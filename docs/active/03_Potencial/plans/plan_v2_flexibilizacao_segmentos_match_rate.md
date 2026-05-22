# Plano de Ação: Flexibilização de Segmentos no Potencial (M3) e Aumento de Match Rate (M4)

> **Versão:** v2.0  
> **Data:** 2026-05-22  
> **Status:** STANDBY - Aguardando Aprovação do Usuário  
> **Escopo:** Motor M3 (Potencial), Motor M4 (Estratégia), Cruzamento Faturamento-Potencial  
> **Identidade Local:** pipelines/potencial-clientes/03_Potencial/docs/plans/plan_v2_flexibilizacao_segmentos_match_rate.md

---

## 📖 1. Contexto e Diagnóstico de Causa Raiz

Durante as análises de cruzamento estratégico entre **Faturamento (Motor M2)** e **Potencial de Peças (Motor M3)** conduzidas no **Motor M4 (Estratégia)**, identificamos um match rate excessivamente baixo entre as bases. Muitos clientes gigantes com faturamento expressivo de peças apareciam com Potencial = 0 no consolidado.

A causa raiz técnica foi isolada no transformador do Motor M3 (`03_Potencial/transform.py`), na linha 455:
```python
df_frota = df_frota[df_frota["Segmento de Atuacao"].str.contains("Constru", case=False, na=False)].copy()
```

### O Descompasso Lógico:
1. **Faturamento (M2):** É agnóstico de segmento. Ele extrai todo o faturamento de peças John Deere (Proteus/ERP) de clientes da Inova, incluindo peças para máquinas agrícolas, de pavimentação e de construção.
2. **Potencial (M3):** A função `_inferir_segmento` classifica as frotas e, em seguida, a linha 455 descarta sumariamente qualquer chassis cujo segmento não seja estritamente `"Construcao"` (filtrado por `"Constru"`).
3. **Impacto no Cruzamento (M4):** Clientes com frotas de **Pavimentação** (ex: marcas Hamm, Wirtgen, Vögele) ou **Agro** (máquinas agrícolas) têm seu potencial completamente zerado em M3. Quando o M4 cruza o faturamento deles com o potencial, não há match de potencial, gerando distorções graves em métricas de SOW (Share of Wallet) e GAP.

---

## 🎯 2. Opções de Negócio Propostas para Decisão

Abaixo estão descritas as três alternativas para flexibilização e correção dessa regra de negócio no M3:

### Opção A (Recomendada: Construção + Pavimentação)
Flexibilizar o filtro do segmento em M3 para reter frotas de **Construção** e **Pavimentação** (as principais linhas de atuação de infraestrutura da concessionária Inova).
*   **Código Proposto:**
    ```python
    df_frota = df_frota[df_frota["Segmento de Atuacao"].str.contains("Constru|Paviment", case=False, na=False)].copy()
    ```
*   **Vantagens:** Mantém o foco estratégico de infraestrutura e reabilita o cálculo de potencial de peças para frotas de pavimentação (Hamm, Wirtgen, etc.), que geram faturamento constante.
*   **Desvantagens:** Continua descartando frotas puramente Agro e Tecnologia.

### Opção B (Máxima Cobertura: Sem Filtro de Segmento)
Remover completamente o filtro de segmento na linha 455 de `transform.py`. Qualquer chassis mapeado na base DNA (independente de ser Construção, Pavimentação, Agro ou Tecnologia) terá seu potencial de peças calculado em M3.
*   **Código Proposto:** Remover a linha 455 de `03_Potencial/transform.py`.
*   **Vantagens:** Match rate máximo e perfeito com o faturamento do ERP. Se o cliente comprou peças agrícolas e está na base DNA, seu potencial estará disponível para o cálculo de SOW em M4.
*   **Desvantagens:** Pode inflar o potencial de peças do concessionário se o foco estrito for apenas Linha Amarela (Construção/Pavimentação).

### Opção C (Filtro por Demanda M2 - Complexo)
Permitir a entrada de chassis de Pavimentação ou Agro apenas se houver faturamento histórico para aquele CNPJ/Grupo em M2.
*   **Vantagens:** Extremamente cirúrgico.
*   **Desvantagens:** Cria acoplamento circular complexo entre os motores M2 e M3, violando o princípio de independência dos motores. **Desaconselhado.**

---

## 🛠️ 3. Proposta de Alterações Técnicas (Sob Opção A ou B)

### 3.1. [MODIFY] [03_Potencial/transform.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/03_Potencial/transform.py)
*   Ajustar a linha 455 para implementar a flexibilização do filtro de acordo com a opção aprovada (A ou B).

### 3.2. [NEW] [03_Potencial/tests/test_segment_filter.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/03_Potencial/tests/test_segment_filter.py)
*   Implementar teste de unidade seguindo o ecossistema TDD.
*   O teste fornecerá dados estruturados simulados (`pops`, `dna`, `m0`, etc.) com chassis de Construção, Pavimentação e Agro.
*   Na etapa **RED**, validamos que a regra atual falha (ou descarta os chassis).
*   Na etapa **GREEN**, após aplicar a correção, validamos que os chassis das frotas aprovadas passam pelo filtro e têm seu potencial calculado.

---

## 🚦 4. Plano de Verificação e Homologação

1.  **Testes de Unidade (Pytest):** Executar o novo teste `pytest pipelines/potencial-clientes/03_Potencial/tests/test_segment_filter.py`.
2.  **Execução Local do Motor M3:** Rodar `python run.py` dentro de `03_Potencial` e certificar que a volumetria de chassis com potencial gerada no Parquet ouro aumentou de forma consistente e com qualidade de dados (sem nulos).
3.  **Execução de Ponta a Ponta:** Executar `python ligar_motores.py` na raiz para reprocessar toda a esteira do M0 ao M5.
4.  **Análise de Impacto de Match Rate:** Medir a nova taxa de match rate no Motor M4 e validar o incremento real nas volumetrias de clientes ativos mapeados com potencial de peças.
