# 🚶 WALKTHROUGH: Campanha Lubrificantes Uberlândia 2026

Este documento descreve como operar o motor de metas estratégico para a filial de Uberlândia (V2.3), garantindo a integridade dos dados e a correta distribuição de metas.

---

## 🚀 1. Execução Rápida

Para gerar a matriz estratégica atualizada, execute o comando abaixo no terminal (estando na raiz do projeto):

```powershell
# Configurar ambiente e rodar motor
$env:PYTHONPATH = "C:\Projetos\Inova\shared;" + $env:PYTHONPATH
python src/main_campanha_uberlandia.py
```

O arquivo final será gerado na pasta `outputs/` com o padrão:
`MATRIZ_ESTRATEGICA_UBERLANDIA_YYYYMMDD_HHMM.xlsx`.

---

## 🏗️ 2. Arquitetura do Motor

O motor principal (`src/main_campanha_uberlandia.py`) segue um pipeline de 4 estágios:

### A. Ingestão e Taxonomia (Filtro Blindado)

O sistema utiliza o arquivo `data/config/taxonomy_lubrificantes.json` para filtrar o faturamento.

* **Positivos:** `LUB`, `LUBRIFICANTE`, `OLEO`, `HY-GARD`, `PLUS-50`, `BREAK IN`.
* **Negativos:** Barragem automática de 28 termos (ex: `BOMBA`, `FILTRO`, `BICO`, `CONEXAO`) para evitar que peças de reposição inflem a meta de lubrificantes.

### B. Atribuição Dinâmica

* **Dono da Conta:** Identificado pela *última venda de qualquer produto* realizada em 2026. Isso garante que o consultor que está operando na conta hoje seja o responsável pela meta.
* **Audit:** A lógica foi validada no laboratório contra orçamentos abertos para garantir zero conflito de atendimento.

### C. Inteligência Híbrida de Potencial (M3 + Histórico)

O teto estratégico de cada cliente é calculado como:
`MAX( Potencial_LUB_M3 * 0.50 , Fat_LUB_2025 * 1.20 )`

* Garante que clientes sem máquinas mapeadas tenham meta (+20% sobre 2025).
* Garante que frotas gigantes mapeadas no M3 gerem oportunidade real.

### D. Balança de Metas (SOW Amortecido)

Para evitar metas impossíveis para clientes que não compram (Churn ou Novos), aplicamos deságios no GAP:

* **Penetração < 5%:** Meta reduzida em 90%.
* **Penetração 5-20%:** Meta reduzida em 70%.
* **Penetração > 20%:** Meta integral de aceleração.

---

## 📊 3. Estrutura de Outputs

O Excel gerado contém duas visões:

1. **METAS_POR_CLIENTE:** Lista de ataque para o consultor, com mix de produtos sugerido (Top 3 histórico ou Kit de Revisão).
2. **PERF_POR_CONSULTOR:** Visão gerencial com índice de Agressividade (% sobre a média mensal) e Folga de Teto (O quanto da carteira ainda é "mato alto").

---

## 🛠️ 4. Manutenção e Ajustes

* **Alterar Meta Global:** Edite a constante `META_GLOBAL = 400000.0` no script principal.
* **Atualizar Produtos:** Edite `data/config/taxonomy_lubrificantes.json` para adicionar novos óleos ou palavras de bloqueio.
* **Novas Bases:** Substitua os arquivos na pasta `data/` mantendo os nomes originais (`Detalhamento de Vendas_uberlandia.xlsx`).

---
**Governança:** Este projeto segue os padrões Stout/CDD. Qualquer alteração lógica deve ser documentada no `DICIONARIO_OUTPUT.md`.
