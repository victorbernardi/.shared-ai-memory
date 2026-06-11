# 🚀 Plano de Implementação: Resolução de Colisões de CPFs nos Motores M0 & M2

> **ID do Plano:** `plan_v1_colisao_cpfs`
> **Fase:** `/plan` (Estratégia Técnica)
> **Data:** 2026-05-28
> **Autor:** Gemini Engenheiro de Software / Stout Lab
> **Status:** **STANDBY (Aguardando Aprovação Humana)**

---

## 1. Objetivo e Escopo

Eliminar de forma definitiva as colisões de CPFs nos motores analíticos de **Identidade (M0)** e **Faturamento (M2)** no pipeline do projeto `potencial-clientes`. A correção visa impedir que pessoas físicas distintas com CPFs nulos, vazios ou matematicamente inválidos sejam unificadas sob uma única raiz de grupo econômico, inflando artificialmente o faturamento consolidadado.

---

## 2. Proposta de Alterações Técnicas

### 🎯 Componente: Potencial Clientes - Faturamento

#### [MODIFY] [transform.py](file:///C:/Projetos/Inova/pipelines/potencial-clientes/02_Faturamento/transform.py)

Atualmente, o agrupamento de clientes e consolidação de notas fiscais é feito por `CNPJ_RAIZ` gerado a partir do CPF/CNPJ normalizado.
Propomos refatorar a normalização e a geração de raiz para isolar individualmente registros inválidos e nulos.

##### Estratégia de Código Proposta:

1. **Higienização Avançada de CPFs:**
   Implementar detecção ativa de documentos inválidos conhecidos (ex: sequências nulas `00000000000` a `99999999999`) e validação de dígitos verificadores básicos de CPFs/CNPJs.
2. **Geração de Chaves Raiz Únicas de Isolamento:**
   Se o CPF/CNPJ for nulo, vazio ou inválido, ao invés de retornar `""` (que causa colisão aglomerando todos na raiz comum vazia), geraremos uma chave raiz sintética e individualizada baseada no ID do cliente ou em uma chave primária do registro (ex: `f"TEMP_INVALID_{id_cliente}"` ou hash UUID individual do registro).
   * Isso garante que na agregação por `groupby("CNPJ_RAIZ")`, cada cliente inválido/nulo forme seu próprio grupo individual isolado (faturamento unitário), eliminando a colisão referencial de faturamento.

##### Código Refatorado Proposto:

```python
import re
import pandas as pd
import numpy as np

def validar_cpf(cpf: str) -> bool:
    """Valida matematicamente os digitos verificadores do CPF."""
    if not cpf or len(cpf) != 11 or cpf in [str(i)*11 for i in range(10)]:
        return False
    # Validação de primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    if resto != int(cpf[9]):
        return False
    # Validação de segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    if resto == 10:
        resto = 0
    return resto == int(cpf[10])

def normalizar_cnpj(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    # Supõe-se a existência de uma coluna identificadora única por cliente para isolamento (ex: 'ID_CLIENTE' ou 'COD_CLIENTE')
    # Usaremos 'ID_CLIENTE' se disponível; caso contrário, geraremos IDs sequenciais de linha para garantir isolamento temporário.
    client_id_col = "ID_CLIENTE" if "ID_CLIENTE" in df.columns else "COD_CLIENTE"
    
    def _norm(row):
        x = row["CPF_CNPJ_DO_CLIENTE"]
        if pd.isna(x) or str(x).strip() == "":
            return ""
        s = re.sub(r"\D", "", str(x))
        normalized = s.zfill(11) if len(s) <= 11 else s.zfill(14)
        return normalized

    # Aplicamos a normalização preservando dados da linha
    df["CPF_CNPJ_DO_CLIENTE_NORM"] = df.apply(_norm, axis=1)
    
    def _raiz(row):
        doc = row["CPF_CNPJ_DO_CLIENTE_NORM"]
        client_id = row[client_id_col] if client_id_col in row else str(np.random.randint(100000, 999999))
        
        if not doc:
            # Documento nulo/vazio: Raiz sintética única para isolar referencialmente
            return f"UNQ_NULL_PF_{client_id}"
            
        if len(doc) <= 11:
            # CPF: Valida legitimidade matemática
            if validar_cpf(doc):
                return doc  # CPF Legítimo: Raiz é o próprio CPF
            else:
                # CPF Inválido: Raiz sintética única para isolar referencialmente
                return f"UNQ_INVALID_PF_{client_id}"
        else:
            # CNPJ: Retorna os primeiros 8 dígitos legítimos
            return doc[:8]
            
    df["CNPJ_RAIZ"] = df.apply(_raiz, axis=1)
    # Sobrescreve coluna original limpa
    df["CPF_CNPJ_DO_CLIENTE"] = df["CPF_CNPJ_DO_CLIENTE_NORM"]
    df.drop(columns=["CPF_CNPJ_DO_CLIENTE_NORM"], inplace=True)
    return df
```

---

## 3. Plano de Verificação

### Testes Automatizados (TDD / Pandas)
*   Criaremos um caso de teste unitário offline em pandas que injetará um dataframe de teste contendo:
    *   3 clientes com CPFs válidos legítimos e notas fiscais separadas.
    *   4 clientes com CPFs nulos ou vazios e notas fiscais separadas.
    *   2 clientes com CPFs inválidos conhecidos (ex: `00000000000` ou digito incorreto).
*   **Critério de Sucesso do Teste:**
    *   O agrupamento referencial (`groupby("CNPJ_RAIZ").agg({"FATURAMENTO": "sum"})`) deve reportar exatamente **9 grupos separados** (sendo cada cliente nulo ou inválido seu próprio faturamento individual isolado) e **NUNCA agrupar notas fiscais de CPFs nulos/inválidos distintos no mesmo montante comum**.

---

## 4. Trava de Segurança & Próximos Passos

> [!IMPORTANT]
> **STANDBY MODE ATIVO:** Este plano estratégico foi formalizado com total rastreabilidade. Em conformidade absoluta com as regras locais e a governança universal do Stout Lab, nenhuma alteração de código foi realizada e nenhuma alteração será feita nos motores reais até que o usuário revise e aprove explicitamente esta estratégia técnica.

---
*Fim do plano de implementação.*
