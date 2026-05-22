# Especificação Técnica v4: Correção das Colunas Equipamentos e Cidade no BUP

**Data:** 2026-05-22  
**Autor:** Antigravity / AI Coding Assistant  
**Status:** PROPOSTA / PESQUISA CONCLUÍDA  

## 1. Objetivo de Negócio e Impacto
O relatório consolidado da BUP (Base Única de Pós-Venda) atende à coordenação de pós-venda John Deere para apoiar a atuação consultiva dos consultores de Peças de Construção. A integridade e confiabilidade dos dados do relatório são críticas para direcionar a equipe de vendas de forma eficiente. 
A correção atual visa:
1. **Coluna Equipamentos:** Garantir que o portfólio de máquinas/equipamentos de cada grupo econômico ou filial seja corretamente exibido no relatório, o que atualmente não está ocorrendo devido a um apontamento incorreto de arquivo de origem.
2. **Coluna Cidade:** Purificar a exibição das localizações no relatório, eliminando a exibição de barras isoladas (`" / "`) para clientes sem endereço completo no Protheus, e padronizando-os como `"Indisponível"`.

---

## 2. Diagnóstico Técnico Detalhado

### 2.1 Coluna Equipamentos
- **Problema:** A coluna `Equipamentos` é exportada vazia no relatório final da BUP.
- **Causa Raiz:** No script principal `scripts/consolidate_bup.py` (linha 41), a constante `PATH_MAQUINAS` está mapeada para:
  `PATH_MAQUINAS  = SHARED_DATA / "dataset_ouro_maquinas_v1.parquet"`
  No entanto, o arquivo real presente no diretório compartilhado (`C:\Projetos\Inova\shared\data`) chama-se **`dataset_ouro_dna_maquinas_v1.parquet`**. Como o arquivo `dataset_ouro_maquinas_v1.parquet` não existe, o script ignora silenciosamente a carga de máquinas e deixa a coluna em branco.
- **Evidência do Diagnóstico (Offline):**
  - Existência de `dataset_ouro_maquinas_v1.parquet`: **False**
  - Existência de `dataset_ouro_dna_maquinas_v1.parquet`: **True** (com 22.057 linhas e as colunas esperadas `CNPJ Dono Oficial`, `CNPJ Raiz Dono` e `Modelo_Codigo`).
- **Solução:** Sincronizar o caminho de `PATH_MAQUINAS` no código para apontar para `dataset_ouro_dna_maquinas_v1.parquet`.

### 2.2 Coluna Cidade
- **Problema:** Clientes aparecem no relatório com a cidade preenchida como `"Indisponível"` e outros como `" / "`.
- **Causa Raiz:**
  - A cidade é formatada via: `df_protheus_cad['Cidade_Format'] = df_protheus_cad['A1_MUN'].str.strip() + " / " + df_protheus_cad['A1_EST'].str.strip()`
  - Se o cliente **não tem registro no cadastro local (SA1010)**, ou se os campos de localização são estritamente nulos (`NaN`), a concatenação retorna `NaN` e o `.fillna("Indisponível")` substitui pelo valor de fallback. (Representa **76 clientes / 0.28%** da base).
  - Se o cliente **tem registro no cadastro local**, mas os campos de município (`A1_MUN`) e estado (`A1_EST`) estão salvos no Protheus como **strings vazias ou apenas espaços** (ex: `""` ou `"   "`), a concatenação resulta na string literal `" / "`. Como não é um valor nulo (`NaN`), o `.fillna("Indisponível")` não é acionado, fazendo com que a barra apareça limpa no relatório. (Representa **135 clientes / 0.50%** da base).
- **Solução:** Implementar uma função de formatação robusta que trata strings vazias, valores nulos (`NaN`, `None`), espaços em branco e garante a remoção de `" / "` vazias, centralizando o fallback correto de `"Indisponível"`.

---

## 3. Especificação das Mudanças Propostas

### 3.1 Correção do Caminho de Máquinas
No arquivo [consolidate_bup.py](file:///C:/Projetos/Inova/projects/BUP-base-unica-pós-venda/scripts/consolidate_bup.py#L41), alterar a definição de `PATH_MAQUINAS` de:
```python
PATH_MAQUINAS  = SHARED_DATA / "dataset_ouro_maquinas_v1.parquet"
```
para:
```python
PATH_MAQUINAS  = SHARED_DATA / "dataset_ouro_dna_maquinas_v1.parquet"
```

### 3.2 Refatoração da Formatação de Cidade
No arquivo [consolidate_bup.py](file:///C:/Projetos/Inova/projects/BUP-base-unica-pós-venda/scripts/consolidate_bup.py#L460-L466), substituir o bloco de merge e formatação por:
```python
    # Merge de Localização (Cidade apenas)
    if df_protheus_cad is not None:
        df_protheus_cad['A1_CGC'] = df_protheus_cad['A1_CGC'].astype(str).str.strip().str.replace(r'\D', '', regex=True).str.zfill(14)
        
        # Função auxiliar de formatação robusta de cidade/estado
        def formatar_cidade_completa(mun, est):
            mun_clean = str(mun).strip() if pd.notnull(mun) else ""
            est_clean = str(est).strip() if pd.notnull(est) else ""
            
            # Higienização de strings de nulo ou vazias
            if mun_clean.upper() in ["NAN", "NONE", "NULL"] or not mun_clean:
                mun_clean = ""
            if est_clean.upper() in ["NAN", "NONE", "NULL"] or not est_clean:
                est_clean = ""
                
            if not mun_clean and not est_clean:
                return "Indisponível"
            elif mun_clean and est_clean:
                return f"{mun_clean} / {est_clean}"
            elif mun_clean:
                return mun_clean
            else:
                return est_clean

        df_protheus_cad['Cidade_Format'] = df_protheus_cad.apply(lambda r: formatar_cidade_completa(r['A1_MUN'], r['A1_EST']), axis=1)
        df_cevap = pd.merge(df_cevap, df_protheus_cad[['A1_CGC', 'Cidade_Format']], left_on="CNPJ_Cliente", right_on="A1_CGC", how="left")
        df_cevap['Cidade'] = df_cevap['Cidade_Format'].fillna("Indisponível")
        df_cevap.drop(columns=['A1_CGC_y', 'Cidade_Format'], inplace=True, errors='ignore')
```

---

## 4. Plano de Testes e Validação
1. **Verificação dos Equipamentos:**
   - Confirmar se a contagem de clientes com máquinas no log do consolidador passa de `0` para uma quantidade consistente (espera-se milhares de registros combinados).
   - Validar no Excel final se a coluna `Equipamentos` está preenchida com os modelos correspondentes aos CNPJs.
2. **Verificação das Cidades:**
   - Confirmar se a coluna `Cidade` no Excel final não apresenta nenhuma barra solta `" / "`.
   - Garantir que todos os registros sem localização adequada sejam consolidados sob `"Indisponível"`.
