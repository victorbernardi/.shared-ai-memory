# Especificação Técnica: Adição da Coluna Mesorregião no Motor CEVAP

> **Status:** Aprovada pelo Usuário
> **Data:** 2026-06-01
> **Autor:** Gemini CLI Builder / Engenheiro de Software

---

## 1. Objetivo e Escopo

Integrar a coluna `Mesoregiao` na planilha final de ativação do Motor CEVAP (`PLANILHA_CEVAP_GOLD_V5_*.xlsx` e entrega no OneDrive). A fonte primária de dados para a correspondência é o arquivo JSON centralizado de mapeamento de cidades e mesorregiões localizado no projeto vizinho:
`C:\Projetos\Inova\projects\lead-csc-pops\data\config\cidade_mesoregiao.json`

## 2. Mapeamento e Normalização

O arquivo JSON `cidade_mesoregiao.json` mapeia chaves textuais (cidades ou combinações de cidade/UF) para mesorregiões.
Exemplos de chaves:
- `"ABADIA DOS DOURADOS / MG": "Triangulo Mineiro / Alto Paranaiba"`
- `"ABADIA DOS DOURADOS": "Triangulo Mineiro / Alto Paranaiba"`
- `"ABEL FIGUEIREDO / PA": "Sudeste Paraense"`

### Estratégia de Normalização
1. No script `polimento_final_v5.py`, a coluna `Cidade` é extraída em formato `"Cidade/UF"` (exemplo: `"Belo Horizonte/MG"`).
2. Para garantir o casamento de chaves (match rate), a string `"Cidade/UF"` será normalizada para maiúsculas e receberá espaços nas laterais da barra:
   - Entrada: `"Belo Horizonte/MG"`
   - Normalizado: `"BELO HORIZONTE / MG"`
3. **Algoritmo de Busca (Fallback):**
   - **Passo 1:** Buscar a chave exata normalizada (ex: `"BELO HORIZONTE / MG"`) no JSON.
   - **Passo 2 (Fallback):** Se não encontrar, buscar apenas o nome da cidade em maiúsculas (ex: `"BELO HORIZONTE"`).
   - **Passo 3 (Default):** Caso nenhuma chave corresponda, definir como `"Indisponível"`.

## 3. Impacto e Alterações Físicas

As seguintes alterações serão efetuadas:
1. **`scripts/polimento_final_v5.py`**:
   - Carregar o JSON usando `encoding='utf-8'` (Vacina de Encoding).
   - Mapear a mesorregião usando o algoritmo de fallback.
   - Adicionar a coluna `Mesoregiao` imediatamente após a coluna `Cidade` na lista `cols_finais` de saída.
2. **`tests/test_columns.py`**:
   - Adicionar `"Mesoregiao"` na lista `expected_cols` para manter a integridade dos testes de qualidade (QA).

## 4. Governança e Regras de Negócio

- ** Encoding:** UTF-8 obrigatório para leitura do JSON (`encoding='utf-8'`).
- ** Caminhos Relativos/Canônicos:** Usar caminhos robustos e tratar o JSON do projeto vizinho usando sua localização estática informada.
