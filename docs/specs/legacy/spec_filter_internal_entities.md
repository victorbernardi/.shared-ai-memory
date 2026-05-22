# Especificação Técnica: Filtragem de Entidades Internas (John Deere & Inova)

## 1. Objetivo
Remover o faturamento e o potencial de mercado das empresas **JOHN DEERE BRASIL LTDA** e **INOVA (Concessionária)** dos motores de inteligência. Isso evita a inflação artificial dos números de mercado, uma vez que estas entidades representam a fábrica e o canal de distribuição, não o cliente final de aftermarket.

## 2. CNPJs Identificados (Raízes - 8 dígitos)
Após varredura nos códigos (especificamente no `motor_identidade_m0.py` e bases transacionais), foram identificadas as seguintes raízes:

### 🏢 INOVA (Grupo/Dealer)
- `08673321` (INOVA EQUIPAMENTOS LTDA)
- `06286309` (INOVA EQUIPAMENTOS LTDA)
- `05804104` (INOVA MAQUINAS LTDA)
- `11099079` (INOVA INFRAESTRUTURA)
- `00679427` (INOVA - Raiz Adicional)

### 🚜 JOHN DEERE (Fábrica)
- `89674782` (JOHN DEERE BRASIL LTDA)

---

## 3. Análise de Impacto (Base 2025/2026)
Executada simulação interna nos datasets ouro atuais:

| Motor | Métrica | Valor Atual (Bruto) | Valor Após Filtro | Impacto (Redução) |
| :--- | :--- | :--- | :--- | :--- |
| **M2 (Faturamento)** | CAL2025_PECAS | R$ 187.363.274,82 | R$ 179.450.169,44 | **- R$ 7.913.105,38 (4,22%)** |
| **M3 (Potencial)** | Potencial Total | R$ 527.549.201,18 | R$ 526.593.916,70 | **- R$ 955.284,48 (0,18%)** |

**Observação:** O maior impacto está no faturamento da John Deere Brasil, que consome peças internamente (garantia/venda direta), mas não possui frota de construção mapeada para potencial no território.

---

## 4. Requisitos Técnicos
1. **M2 (Faturamento):** Inserir trava no Bloco [2.0] de `motor_de_faturamento_v1.py` logo após a higienização do CNPJ.
3. **Filtro de Território (AOR):** No Motor M3, filtrar para manter apenas máquinas com `AOR Indicator` igual a "Inside dealer AOR" ou "Benchmark Injection". Máquinas "Outside dealer AOR" devem ser removidas para focar no potencial de responsabilidade da Inova.
4. **Auditabilidade:** Gerar log indicando o volume de faturamento/potencial descartado pela regra de "Filtro de Entidades Internas" e "Filtro de Território".

## 5. Análise de Impacto Adicional (AOR)
A aplicação do filtro de AOR removerá **631 máquinas**, com um impacto estimado de:
- **Potencial Removido (Outside AOR):** ~ R$ 82.267.185,26.
- **M2:** Verificar se o `Total_Liquido_Pecas` bate com o valor simulado de R$ 179,4M.
- **M3:** Verificar se o `Potencial Total Anual` bate com R$ 526,6M.
- **Cross-check:** Garantir que o CNPJ `89674782` não apareça mais no `dataset_ouro_pecas_grupo_v1.xlsx`.

---
*Assinado: Antigravity (Discovery Phase)*
