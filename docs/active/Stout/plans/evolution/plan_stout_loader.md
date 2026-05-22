# Plano de Evolução: Stout-Standard Loader (Resiliência de Dados)

## Problema
Em sessões recentes, observamos falhas recorrentes de `KeyError` e `UnicodeEncodeError` devido a:
- Parquets gerados de Excels com nomes de colunas inconsistentes (espaços, minúsculas).
- Encodings variados (cp1252 vs utf-8) em ambientes Windows brasileiros.
- Perda de rastro sobre a "idade" do dado no cache.

## Proposta
Criar um método `load_stout_data(path, ...)` na biblioteca core do ecossistema.

## Especificação Técnica
1. **Normalização Total:** O loader deve aplicar `.str.upper().str.strip().replace(' ', '_')` em todas as colunas no momento da carga.
2. **Fallback de Encoding:** Tentar carregar em ordem: `utf-8-sig`, `cp1252`, `latin1`.
3. **Metadados de Frescor:** Adicionar uma coluna oculta `_STOUT_LOAD_DATE` e emitir um log se a fonte original for mais antiga que o limite definido em config.
4. **Resiliência Numérica:** Limpeza automática de strings que representam números (remoção de R$, separadores de milhar).

## Impacto
Elimina 90% dos erros de "fiação" de dados iniciais, permitindo que o agente foque na lógica e não no saneamento básico.
