# Plano de Implementação: Correção de Colisão de CPFs no Agrupamento (M2 e M0)

Este plano descreve a abordagem técnica para sanar o bug de colisões de CPFs no motor **M2 (Faturamento)** e no motor **M0 (Identidade)**. O bug agrupa incorretamente pessoas físicas distintas na mesma raiz de grupo econômico, inflando faturamentos de forma artificial e poluindo a modelagem estatística.

---

## User Review Required

> [!IMPORTANT]
> **Definição da Regra de Separação de Documentos:**
> O laboratório demonstrou que na base real de clientes, 99,8% dos CPFs legítimos estão gravados com comprimento físico **11** e 99,7% dos CNPJs com comprimento **14**.
> Propomos adotar o comprimento físico numérico limpo para classificar:
> *   **Comprimento <= 11:** Tratado como **CPF**. A chave do grupo é o CPF completo (11 dígitos), evitando colisões.
> *   **Comprimento > 11:** Tratado como **CNPJ**. A chave do grupo é a raiz de 8 dígitos, mantendo a consolidação de filiais de empresas.
>
> Há 28 registros de CNPJs de empresas ou entes cadastrados com documentos sintéticos ou com muitos zeros à esquerda (ex: `00060769000103`) que possuem parte significativa de 11 dígitos. A limpeza de zeros à esquerda para fins de classificação foi descartada, pois transformaria CNPJs reais em CPFs (quebrando seu agrupamento). A classificação será baseada no **comprimento numérico total limpo**, preservando 100% dos CNPJs legítimos e os CPFs tradicionais.

---

## Proposed Changes

### 1. Preparação da Infraestrutura de Código (Git Branch)
*   Criação de branch exclusiva: `fix/m2-m0-cpf-zfill-collision` a partir da branch principal.

---

### 2. Motor M2: Faturamento de Peças Construction
#### [MODIFY] [queries/vendas_pecas_construcao.sql](file:///C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/queries/vendas_pecas_construcao.sql)
*   Hoje a query extrai a raiz do CNPJ fazendo `LEFT(CPF_CNPJ_DO_CLIENTE, 8) AS CNPJ_RAIZ` no próprio SQL do Fabric, aplicando a mesma lógica para CPFs e CNPJs e gerando colisões de CPF direto na fonte.
*   **Alteração:** Modificar a query para extrair o documento original `CPF_CNPJ_DO_CLIENTE` limpo e delegar a extração da raiz de forma condicional para o transformador Python, ou extrair de forma inteligente via `CASE WHEN` no SQL. Adotaremos a extração condicional no transformador Python por maior controle e retrocompatibilidade de testes.

#### [MODIFY] [transform.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/transform.py)
*   **Ajustar `normalizar_cnpj`:** Não aplicar `zfill(14)` geral. Identificar comprimento.
    ```python
    def normalizar_cnpj(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        def _norm(x):
            if pd.isna(x) or str(x).strip() == "":
                return ""
            # Remove não numéricos
            s = re.sub(r"\D", "", str(x))
            # Se for CPF (tamanho <= 11), preenche até 11. Se for CNPJ, preenche até 14.
            return s.zfill(11) if len(s) <= 11 else s.zfill(14)
        df["CPF_CNPJ_DO_CLIENTE"] = df["CPF_CNPJ_DO_CLIENTE"].apply(_norm)
        return df
    ```
*   **Refatorar `extrair_cnpj_raiz` (ou a geração da chave):**
    ```python
    def extrair_cnpj_raiz(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        def _raiz(doc):
            if not doc:
                return ""
            # Se for CPF (tamanho 11), a raiz é o próprio CPF completo (sem colisão)
            if len(doc) <= 11:
                return doc
            # Se for CNPJ (tamanho 14), a raiz são os 8 primeiros dígitos
            return doc[:8]
        df["CNPJ_RAIZ"] = df["CPF_CNPJ_DO_CLIENTE"].apply(_raiz)
        return df
    ```

---

### 3. Motor M0: Identidade Global de Clientes
#### [MODIFY] [scripts/motor_identidade_m0.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/00_Motor_Identidade/scripts/motor_identidade_m0.py)
*   Refatorar a função `limpar_cnpj` para não aplicar `zfill(14)` generalizado sobre CPFs.
*   Ajustar a criação de `CNPJ_DNA` (linha 263) para preservar os 11 dígitos de CPFs (tamanho <= 11) em vez de truncar as 8 primeiras posições da string de 14 dígitos (que gerava a colisão `'000XXXXX'`).
    ```python
    # Proposta de Ajuste no M0:
    df_sa1['CNPJ_L'] = df_sa1['CNPJ_ORIGINAL'].apply(limpar_cnpj_condicional)
    df_sa1['CNPJ_DNA'] = df_sa1.apply(
        lambda r: r['CNPJ_L'] if len(r['CNPJ_L']) <= 11 else r['CNPJ_L'][:8], 
        axis=1
    )
    ```

---

## Verification Plan

### Automated Tests
*   **Motor M2:** Executar os testes unitários do M2 garantindo que o faturamento de CPFs não seja somado de forma colidida e que CNPJs continuem agrupando filiais sob a mesma raiz de 8 dígitos.
*   **Execução Local M2:** Rodar `python run.py` dentro de `02_Faturamento` e analisar a redução na quantidade de grupos econômicos e o faturamento total por grupo para homologar a consistência.
*   **Execução Local M0:** Rodar `python motor_identidade_m0.py` em `00_Motor_Identidade/scripts` e auditar a nova base de identidade gerada em `dataset_ouro_identidade.parquet` garantindo o fim das colisões de CPF.

### Manual Verification
*   Confirmar que os CPFs de teste `123.456.789-01` e `123.450.000-00` geram raízes/chaves distintas (`12345678901` e `12345000000`) e que os CNPJs `01.234.567/0001-89` e `01.234.567/0002-90` geram a mesma raiz (`01234567`).
