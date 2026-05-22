# Spec: Reativação da Camada C2 via Soberania POPS (M0-v9)

## 1. Objetivo
Implementar uma nova versão do Motor de Identidade (v9) que reativa a unificação por vínculo de oficina/garantia (C2), utilizando o arquivo local `Product_details_full.xlsx` (POPS) como fonte primária de verdade sobre a posse dos chassis, prevenindo unificações indevidas causadas por locadoras e pela própria concessionária (Inova).

## 2. Requisitos Funcionais

### 2.1. Ingestão de Dados POPS
- **Fonte:** `C:\Projetos\Inova\Potencial Clientes\cache\Product_details_full.xlsx`.
- **Mapeamento:** Relação `CHASSI` -> `CNPJ_RAIZ_DONO` (ou campo equivalente que indique o proprietário).

### 2.2. Travas de Segurança (Anti-Bridge)
- **Filtro Volumétrico de Chassi:** Identificar chassis vinculados a mais de 2 raízes de CNPJ diferentes na `VO1010` no último ano. Estes chassis devem ser ignorados na unificação C2.
- **Filtro de Grandes Frotistas:** Identificar raízes de CNPJ que possuem volume anômalo de máquinas no POPS (ex: Locadoras).
- **BLOQUEIO DE DEALER (INOVA):**
    - O CNPJ e a Razão Social da **INOVA** têm **Soberania Zero**.
    - Chassis no POPS vinculados à Inova não podem ser usados como âncora de unificação.
    - A Inova nunca deve ser origem ou destino de solda na Camada C2.

### 2.3. Lógica de Unificação C2
- Se um `ID_CLIENTE` (Protheus) tem transações na `VO1010` para um `CHASSI_X`, e o POPS diz que o `CHASSI_X` pertence ao `CNPJ_GRUPO_Y` (e Y não é Inova/Locadora), unificar o cliente ao grupo Y.
- Precedência: C2 > C1.

## 3. Arquitetura (M0-v9)
- **Arquivo:** `02_Scripts/motor_identidade_m0_v9_pops.py`.
- **Performance:** Carregamento otimizado do Excel POPS e uso de `networkx` para resolução de conflitos de grupo.

## 4. Validação (DoD)
- Unificação bem-sucedida de filiais conforme posse no POPS.
- Zero absorção por grupos Inova ou Locadoras.

---
*Atualizado em: 2026-05-08*
*Assinado: Gemini CLI (Antigravity Engine)*
