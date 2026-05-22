# Plano de Evolução: Config-First Architecture (Soberania de Regras)

## Problema
A dispersão de constantes de negócio (como listas de TES ou thresholds de tempo) em vários scripts cria "verdades locais" que divergem entre si. Isso causa paridade de dados falha entre o relatório PDF e o Scanner, por exemplo.

## Proposta
Tornar o `src/config.py` uma peça obrigatória gerada pelo `stout-init`.

## Estrutura do Config-Standard
1. **DNA (Regras de Negócio):** Listas de códigos, categorias e filtros mestres.
2. **Parameters (Thresholds):** Definição de limites (ex: `MONTHS_FOR_INACTIVITY = 24`).
3. **Registry (Paths):** Mapeamento centralizado de arquivos de entrada e saída.
4. **SQL Templates:** Filtros comuns para injeção em queries.

## Por que seguir?
- **SSOT (Single Source of Truth):** Um único lugar para mudar uma regra de negócio.
- **Onboarding Rápido:** Um novo agente entende o projeto lendo apenas o `config.py`.
- **Desacoplamento:** Scripts de execução dependem de abstrações, não de valores fixos.
