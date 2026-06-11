# 📑 Especificação Técnica: Resolução de Colisões de CPFs nos Motores M0 & M2

> **ID da Especificação:** `spec_v1_colisao_cpfs_motores`
> **Fase:** `/brainstorm` (Pesquisa e Diagnóstico)
> **Data:** 2026-05-28
> **Autor:** Gemini Engenheiro de Software / Stout Lab
> **Status:** Concluído (Pronto para Planejamento)

---

## 1. Contexto de Negócio & Impacto

O ecossistema Stout Lab possui um pipeline analítico de **Potencial de Clientes** que consome dados transacionais e de cadastro para gerar modelagens estatísticas e dashboards de Key Performance Indicators (KPIs). 

Dentro desse pipeline, dois motores desempenham papéis críticos:
1. **Motor M0 (Identidade):** Higieniza, valida e normaliza documentos de identificação (CPF/CNPJ).
2. **Motor M2 (Faturamento):** Consolida notas fiscais e transações financeiras, agrupando clientes por **Grupo Econômico** (Raiz do documento) para calcular faturamentos reais consolidados.

### O Bug de Colisão de CPFs
Historicamente, foi detectado no banco de dados SQLite de cognição (`session_learning.db`) o seguinte incidente reincidente:
> *Colisões de CPFs nos motores M0 e M2 agrupam incorretamente pessoas físicas distintas na mesma raiz de grupo econômico, inflando faturamentos de forma artificial e poluindo a modelagem estatística.*

*   **Risco Técnico:** Alto. Corrupção da integridade referencial e agregação estatística incorreta.
*   **Impacto de Negócios:** Gravíssimo. Inflar faturamentos artificiais induz a decisões errôneas de crédito, limite e classificação de clientes, além de violar regras de governança e LGPD ao misturar CPFs distintos.

---

## 2. Localização Física no Ecossistema

Graças a uma varredura com scripts analíticos de alto desempenho em Python, localizamos o projeto e os códigos-fonte afetados no ambiente do host:

*   **Repositório do Projeto:** `C:\Projetos\Inova\pipelines\potencial-clientes\`
*   **Motor M0 (Identidade):** `C:\Projetos\Inova\pipelines\potencial-clientes\00_Motor_Identidade\`
*   **Motor M2 (Faturamento):** `C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\`
*   **Arquivo Crítico Afetado:** `C:\Projetos\Inova\pipelines\potencial-clientes\02_Faturamento\transform.py` (e scripts acoplados em `00_Motor_Identidade\src\`)

---

## 3. Diagnóstico e Causa Raiz

A análise técnica do histórico de commits e do código do arquivo `transform.py` revelou a seguinte lógica de normalização de documentos:

```python
def normalizar_cnpj(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    def _norm(x):
        if pd.isna(x) or str(x).strip() == "":
            return ""
        s = re.sub(r"\D", "", str(x))
        return s.zfill(11) if len(s) <= 11 else s.zfill(14)
        
    df["CPF_CNPJ_DO_CLIENTE"] = df["CPF_CNPJ_DO_CLIENTE"].apply(_norm)
    
    def _raiz(doc):
        if not doc:
            return ""
        # CPF mantém 11 dígitos, CNPJ extrai os primeiros 8 dígitos
        return doc if len(doc) <= 11 else doc[:8]
        
    df["CNPJ_RAIZ"] = df["CPF_CNPJ_DO_CLIENTE"].apply(_raiz)
    return df
```

### Análise de Causa Raiz das Colisões
1. **Junção por Raiz Vazia (`""`):** Se o CPF ou CNPJ de um cliente não for informado (nulo ou vazio), a função `_norm` retorna `""`, e `_raiz` também retorna `""`. Na fase de agrupamento em grupo econômico por `CNPJ_RAIZ`, **todos os milhares de clientes sem documento preenchido são agrupados sob a mesma raiz `""`**. Isso consolida faturamentos de milhares de pessoas físicas independentes sob uma única entidade fictícia vazia, inflando artificialmente o faturamento deste "grupo".
2. **CPFs Inválidos/Fictícios Comuns:** Cadastros com CPFs de teste ou falsificados (ex: `00000000000`, `11111111111`, `99999999999`) passam pela normalização e geram a mesma raiz correspondente, aglutinando pessoas físicas distintas na mesma raiz.
3. **CPFs Incompletos:** CPFs preenchidos com menos de 11 dígitos (ex: `123456`) que não possuem preenchimento de zeros à esquerda original ou que são normalizados incorretamente colidem com outros registros legítimos após a aplicação do `zfill(11)`.

---

## 4. Requisitos da Proposta de Solução

Para sanar a colisão mantendo a aderência ao CDD e às Karpathy Laws, o novo algoritmo de processamento de CPFs no motor M0 e M2 deve cumprir os seguintes requisitos:

1. **Isolamento de Documentos Nulos/Vazios:** Se o CPF/CNPJ for nulo ou vazio, a chave `CNPJ_RAIZ` gerada deve ser **única e individualizada** por cliente (ex: baseada no `ID_CLIENTE` interno ou gerando um identificador hash único como `TEMP_PF_IDCLIENTE`), garantindo que clientes sem CPF nunca pertençam ao mesmo grupo econômico raiz.
2. **Validador de CPFs Legítimos (Higienização Ativa):** Implementar um filtro no `_norm` que detecte CPFs repetidos conhecidos (`00000000000` etc.) e CPFs matematicamente inválidos (cálculo dos dígitos verificadores). Se o documento for inválido, ele deve ser reclassificado como "Documento Inválido" e receber uma chave raiz isolada e não-aglutinável.
3. **Garantia de Não-Regressão:** A modelagem de faturamento de grupos econômicos de CNPJs válidos (primeiros 8 dígitos) deve permanecer completamente inalterada.

---

## 5. Próximos Passos (Transição de Fase)

Conforme as diretrizes de governança locais:
1. Concluímos a fase `/brainstorm` com esta especificação formalizada.
2. O próximo passo é acionar a fase `/plan` (`process-writing-plans`) para desenhar o plano estratégico detalhado das alterações em `transform.py` e nos testes unitários e de integração de `02_Faturamento` e `00_Motor_Identidade`.
3. O plano será gerado na pasta `docs/plans/` sob o nome `plan_v1_colisao_cpfs.md` e colocado em STANDBY aguardando a aprovação humana.

---
*Fim da especificação técnica.*
