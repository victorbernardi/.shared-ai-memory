# Plano de Execução — Correção do Maestro M0 (Unificação de Grupos e Eleição de Representante)

> **Documento:** Plano de Execução Técnica (v11.8)  
> **Status:** STANDBY MODE (Aguardando Aprovação Humana)  
> **Referência:** Inova Pós-Venda / Motor de Identidade M0  
> **Data:** 2026-05-21  

---

## 1. RESUMO DOS PROBLEMAS & SOLUÇÃO TÉCNICA

Este plano detalha a implementação das correções de infraestrutura cognitiva do Maestro M0 para sanar as falhas de unificação e representação de grupos (incluindo VIX, PH Comercio e Ferro+).

### Proposta de Alterações:
1. **welders.py (Camada C3):** Adicionar no método `build_graph` o loop de agrupamento nominal exato (`NOME_DNA` + `PERFIL`) para reintroduzir arestas C3 com score 95 no grafo transitivo `NetworkX`.
2. **seo_ge_batch_v11_7.py (Eleição Robustecida):**
   * Agregar dados de SA1010, VO1010 e VV1010 para computar o `score_frequencia` por CNPJ completo (`CNPJ_L` de 14 dígitos).
   * Substituir a escolha de líder cega por uma classificação baseada nesse score de ecossistema.
   * Garantir que nós isolados pós-filtro de mega-grupos retenham sua linhagem raiz de 8 dígitos de forma robusta e livre de NaNs.

---

## 2. PROPOSTA DE MODIFICAÇÕES

---

### Componente: WeldEngine

#### [MODIFY] [welders.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/scripts/engine/welders.py)

**O que muda:**
* Inserção do mapeamento da Camada C3 dentro de `build_graph()`.
* Iteração sob o DataFrame agrupado por `NOME_DNA` e `PERFIL` para estabelecer elos lineares de transição entre nós correspondentes.

**Diferencial Técnico (Draft do Patch):**
```python
        # Camada C3: Solda de Nome 100% (Unificacao Automatica)
        print("WELDING: Aplicando unificacao automatica C3 (100% Match)...")
        df_c3 = df_sa1[df_sa1['NOME_DNA'].str.strip().fillna('') != ''].copy()
        for (nome_dna, perfil), group in df_c3.groupby(['NOME_DNA', 'PERFIL']):
            ids = group['ID_CLIENTE'].tolist()
            cgcs = group['A1_CGC'].tolist()
            for i in range(len(ids)-1):
                self.add_connection(ids[i], ids[i+1], 'C3:SOLDA_NOME_EXATO', cgc_a=cgcs[i], cgc_b=cgcs[i+1])
```

---

### Componente: Batch Engine

#### [MODIFY] [seo_ge_batch_v11_7.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/scripts/seo_ge_batch_v11_7.py)

**O que muda:**
* Computação das tabelas de frequência estatística para SA1010, VO1010 e VV1010, somando-as em um dicionário rápido indexado por `CNPJ_L` (14 dígitos).
* Classificação dos nós no componente conexo baseando-se em `(score_frequencia, CNPJ_L)` para eleger de forma determinística o líder real.
* Derivação do nome e da raiz do grupo a partir do representante robusto.

**Diferencial Técnico (Draft do Patch):**
```python
    # 1. Computar votos no ecossistema
    print("RANKING: Computando score de frequencia no ecossistema...")
    f_sa1 = df_sa1['CNPJ_L'].value_counts().reset_index()
    f_sa1.columns = ['CNPJ_L', 'n_sa1']
    
    df_veic = df_vv1.copy()
    df_veic['CNPJ_DONO'] = df_veic['VV1_DOCIND'].apply(limpar_cnpj)
    f_vv1 = df_veic['CNPJ_DONO'].value_counts().reset_index()
    f_vv1.columns = ['CNPJ_L', 'n_vv1']
    
    df_vo1['CNPJ_OF'] = df_vo1['VO1_PROVEI'].str.strip().map(mapa_cod_cnpj)
    f_vo1 = df_vo1['CNPJ_OF'].value_counts().reset_index()
    f_vo1.columns = ['CNPJ_L', 'n_vo1']
    
    votos = pd.merge(f_sa1, f_vv1, on='CNPJ_L', how='outer')
    votos = pd.merge(votos, f_vo1, on='CNPJ_L', how='outer').fillna(0)
    votos['score_frequencia'] = votos['n_sa1'] + votos['n_vv1'] + votos['n_vo1']
    dict_scores = dict(zip(votos['CNPJ_L'], votos['score_frequencia']))
    
    master['score_frequencia'] = master['CNPJ_L'].map(dict_scores).fillna(0)
```

E no loop de consolidação:
```python
    for comp in components:
        l_ids = list(comp)
        sub_df = master[master['ID_CLIENTE'].isin(l_ids)]
        if sub_df.empty: continue
        
        # Eleger o CNPJ_L (14 dígitos) mais frequente/ativo
        representante = sub_df.sort_values(by=['score_frequencia', 'CNPJ_L'], ascending=[False, True]).iloc[0]
        lider_raiz = representante['CNPJ_DNA']
        lider_nome = representante['A1_NOME'].strip()
        
        for cid in l_ids:
            id_to_group[cid] = lider_raiz
            id_to_group_name[cid] = f"GRUPO {lider_nome}"
```

---

## 3. PLANO DE VERIFICAÇÃO (TESTES)

### Testes Automatizados (TDD Preflight)
* Criar um script de teste unitário em `tests/test_maestro_correcoes.py` mockando os dados do SA1010 para validar:
  1. Que a Camada C3 adiciona as conexões esperadas no grafo.
  2. Que o cálculo do `score_frequencia` unifica e ordena corretamente o representante do grupo.
  3. Que o nome do grupo e o CNPJ do líder correspondem ao representante mais ativo.

### Verificação Manual (Pós-Batch)
* Executar o lote com cache estrito (`seo_ge_batch_v11_7.py`).
* Verificar o log de saída para atestar que `arestas_c3` é maior que 0.
* Validar no arquivo gerado `03_Resultados/dataset_ouro_v11_7.xlsx` se a raiz `00000152` (VIX LOGISTICA) está corretamente mapeada no grupo correto, com nome adequado e sem valores nulos/NaNs.

---

## 4. TRAVA DE SEGURANÇA & PRÓXIMOS PASSOS

> [!IMPORTANT]
> **STANDBY MODE ATIVO:**
> Em total conformidade com a **Fase de Estratégia (/plan)** do ecossistema Stout, este agente pausou a execução técnica. Nenhuma alteração em código de produção foi efetuada.
> **Aguardamos sua aprovação formal deste plano para iniciarmos a Fase de Execução (/build).**
