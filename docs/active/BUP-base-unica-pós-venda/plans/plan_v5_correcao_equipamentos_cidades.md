# Plano de Execução v5: Correção de Equipamentos e Cidades na BUP

> **Identidade:** Antigravity CLI Builder / Engenheiro de Software  
> **Status:** AGUARDANDO APROVAÇÃO (Standby Mode)  
> **Referência:** [Especificação Técnica v4](file:///C:/Projetos/Inova/projects/BUP-base-unica-p%C3%B3s-venda/docs/specs/spec_v4_correcao_equipamentos_cidades.md)

---

## 1. Escopo das Modificações
Ajustar o pipeline de consolidação do pós-venda para resolver duas lacunas identificadas na última entrega:
1. **Coluna Equipamentos:** Retornar o portfólio correto de máquinas associando a base real de dados `dataset_ouro_dna_maquinas_v1.parquet`.
2. **Coluna Cidade:** Tratar strings de município e estado em branco no cadastro do Protheus que geravam barras soltas (`" / "`), padronizando o fallback para `"Indisponível"`.

---

## 2. Abordagem de Implementação Detalhada

### 2.1 Passo 1: Ajuste da Fonte de Máquinas (Equipamentos)
Modificar a linha 41 do arquivo `scripts/consolidate_bup.py` para redirecionar o `PATH_MAQUINAS` para a base correta de dados no diretório do shared.

- **Arquivo:** [consolidate_bup.py](file:///C:/Projetos/Inova/projects/BUP-base-unica-pós-venda/scripts/consolidate_bup.py)
- **Mudança:**
  ```diff
  -PATH_MAQUINAS  = SHARED_DATA / "dataset_ouro_maquinas_v1.parquet"
  +PATH_MAQUINAS  = SHARED_DATA / "dataset_ouro_dna_maquinas_v1.parquet"
  ```

### 2.2 Passo 2: Higienização de Cidades
Modificar o bloco de merge e formatação da localização a partir da linha 460 de `scripts/consolidate_bup.py`. Substituir a concatenação simples que falhava em campos com espaços em branco pela nova função `formatar_cidade_completa(mun, est)`.

- **Arquivo:** [consolidate_bup.py](file:///C:/Projetos/Inova/projects/BUP-base-unica-pós-venda/scripts/consolidate_bup.py)
- **Mudança:**
  ```python
  # Merge de Localização (Cidade apenas)
  if df_protheus_cad is not None:
      df_protheus_cad['A1_CGC'] = df_protheus_cad['A1_CGC'].astype(str).str.strip().str.replace(r'\D', '', regex=True).str.zfill(14)
      
      def formatar_cidade_completa(mun, est):
          mun_clean = str(mun).strip() if pd.notnull(mun) else ""
          est_clean = str(est).strip() if pd.notnull(est) else ""
          
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

## 3. Protocolo de Validação e Testes
Após as alterações, realizaremos as seguintes validações empíricas:
1. **Execução Local:** Rodar o consolidador localmente via Python Anaconda e confirmar se não ocorrem exceções ou KeyError.
2. **QA Invariants (TDD):** Executar a suite de testes unitários para certificar que as regras de governança e integridade não foram quebradas.
   - Comando: `& "C:\Users\victor.bernardi\AppData\Local\anaconda3\python.exe" -m pytest tests/ -v`
3. **Validação do Output:**
   - Abrir o arquivo gerado `BUP_POS_VENDA.xlsx` em `data/`.
   - Filtrar a coluna `Equipamentos` e verificar se não está mais em branco para clientes que possuem frota.
   - Filtrar a coluna `Cidade` e verificar que não há valores contendo apenas `/` ou espaços nulos. Todos devem ser nomes válidos ou `"Indisponível"`.
