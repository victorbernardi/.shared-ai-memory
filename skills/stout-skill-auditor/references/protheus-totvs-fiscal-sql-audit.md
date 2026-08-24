# Referência — auditoria fiscal SQL em Protheus/TOTVS

Esta referência apoia a auditoria de sobreposição da `stout-skill-auditor`.
Ela não cria uma responsabilidade nova: quando a intenção envolver Protheus,
TOTVS, SF2/SF3/SFT, NF, filial, série, cancelamento ou SQL fiscal, use estas
verificações para avaliar se uma skill existente já cobre o trabalho e para
registrar uma intenção de forma precisa.

## Gatilhos

`Protheus`, `TOTVS`, `SF2010`, `SF3010`, `SFT010`, `SF2`, `SF3`, `SFT`,
`nota fiscal`, `NF`, `cancelamento`, `filial`, `série`, `F2_FIMP`, `F2_STATUS`,
`F3_DTCANC`, `FT_DTCANC`, `Fabric`, `SQL AdvPL` e `TLPP`.

## Procedimento reutilizável

1. Descrever a intenção com nome, papel, gatilhos, fonte, grão, chave e
   estado esperado. Não propor uma skill nova só porque falta uma consulta.
2. Consultar o Ledger e executar `scripts/semantic_overlap.py` antes de criar
   ou separar qualquer skill. Uma referência de domínio deve permanecer dentro
   de uma skill de auditoria somente quando for material de apoio, não uma
   nova capacidade executável.
3. Confirmar a existência das tabelas e colunas por consulta somente leitura,
   preferencialmente via `INFORMATION_SCHEMA` ou catálogo equivalente do
   Fabric. Não pedir um dicionário externo quando a estrutura disponível e o
   formato nativo permitem identificar o campo; preservar o valor original e
   marcar a interpretação como premissa quando a legenda não for oficial.
4. Usar `shared.query_loader` para carregar SQL versionado e
   `shared.fabric_db`/`ConexaoFabric` para consulta. Não escrever SQL inline no
   pipeline e não registrar segredos, tokens ou credenciais.
5. Selecionar colunas explicitamente, usar joins ANSI explícitos e filtrar
   registros ativos com `D_E_L_E_T_ = ''` conforme a convenção observada na
   réplica. Primeiro auditar os valores distintos de `D_E_L_E_T_`; não usar
   `<> '*'` como substituto permissivo em uma consulta autoritativa. Filtrar a
   filial quando o objetivo for uma empresa; em consulta cross-branch,
   declarar que a filial faz parte da chave.
6. Normalizar somente a chave de comparação, sem destruir o valor nativo:
   filial numérica para quatro posições, série numérica pelo valor (`1` e
   `001`) e série textual literalmente (`DI`, `RPS`, `LOC`), NF numérica sem
   zeros artificiais (`217400.0`, `000217400`). O formato identifica número e
   série; quantidade de dígitos isolada não define uma data.
7. Usar `filial + série + NF` para relacionar a oficina com o fiscal. Se a
   combinação ainda não for única, investigar cliente/loja; nunca ligar uma
   NF apenas pelo número. Para `SF3010` e `SFT010`, agregar no grão da NF antes
   de juntar ao cabeçalho `SF2010`, evitando multiplicação por itens.
8. Separar os significados nativos:

   | Campo/evidência | Interpretação | Uso seguro |
   | --- | --- | --- |
   | `F2_FILIAL` | Filial do cabeçalho SF2010 | Parte da chave fiscal; não comparar NF sem filial |
   | `F2_FIMP = S` | NF autorizada | Pode ser evidência fiscal indireta, se a regra de negócio aprovar |
   | `F2_FIMP = T` | NF transmitida | Não equivale a autorizada |
   | `F2_FIMP = N` | NF não autorizada | Não confirmar execução |
   | `F2_FIMP = D` | NF denegada | Não confirmar execução |
   | `F2_STATUS = 026` | Cancelamento não autorizado | Não é cancelamento confirmado |
   | `F3_DTCANC`/`FT_DTCANC` preenchido | Marcador de cancelamento | Excluir da evidência de NF ativa |
   | `F3_OBSERV`/`FT_OBSERV = NF CANCELADA` | Marcador textual de cancelamento | Excluir da evidência de NF ativa |

   Uma NF autorizada não é pagamento, faturamento financeiro liquidado,
   margem ou prova isolada de execução. Não sobrescrever conflito operacional
   com evidência fiscal.
9. Manter datas como `date`/`datetime` no DataFrame. Na saída de negócio, as
   colunas de data devem ser exibidas como `dd/mm/aaaa`; ISO fica restrito a
   manifesto ou interface técnica.
10. Registrar resultado, cobertura, duplicidade, estado fiscal, regra,
    limitação e impacto comercial. Se a premissa mudar a contagem, criar nova
    versão da decisão e executar novo replay no mesmo período e denominador.

## Consulta e qualidade SQL

Para código AdvPL/TLPP, preferir `FWExecStatement` com parâmetros e aplicar
`ChangeQuery` quando a consulta for executada pelo framework. Evitar
concatenação de valores, `SELECT *`, joins implícitos, listas `VALUES` geradas
em produção, Cartesian joins e agregação depois de um join que multiplica
itens. Usar `TRY_CONVERT` para campos numéricos ou datas sujos e falhar fechado
quando a chave necessária estiver ausente.

Checklist mínimo antes de reutilizar uma consulta:

- tabelas e campos confirmados na réplica atual;
- filtros ativos e filial explicitados;
- chave completa e normalização testada com exemplos nativos;
- SF3/SFT agregadas antes do join;
- estados `F2_FIMP` e `F2_STATUS` preservados separadamente;
- cancelamento validado por data/observação nativa;
- datas convertidas por formato válido e exportadas como `dd/mm/aaaa`;
- schema, nulos, cardinalidade, duplicidades e tempo registrados;
- diff e hash dos artefatos versionados verificados antes da instalação.

## Ferramentas e fontes oficiais

- Código local: `C:\Projetos\Inova\.venv\Scripts\python.exe`, PowerShell 7,
  UTF-8, `rg`, `Get-FileHash` e `git diff --check`.
- Fabric: `shared.query_loader` e `shared.fabric_db` em consultas somente
  leitura.
- Parquet: `pandas`/`pyarrow` para schema, campos de status, nulos e
  cardinalidade; arquivos de vendas/devoluções sem status não devem ser
  promovidos a fonte fiscal.
- [TOTVS — F2_FIMP](https://tdn.totvs.com/plugins/viewsource/viewpagesrc.action?pageId=866530133)
- [TOTVS — F2_STATUS](https://centraldeatendimento.totvs.com/hc/pt-br/articles/22567084496919-Cross-Segmentos-Backoffice-Protheus-SIGAFAT-Preenchimento-do-campo-Status-Canc-NFe-F2-STATUS)
- [TOTVS — notas canceladas](https://centraldeatendimento.totvs.com/hc/pt-br/articles/360044027134-Cross-Segmento-TOTVS-Backoffice-Linha-Protheus-SIGAFAT-Qual-relat%C3%B3rio-posso-utilizar-para-visualizar-as-notas-canceladas)
- [TOTVS — chave de relacionamento fiscal](https://tdn.totvs.com/plugins/viewsource/viewpagesrc.action?pageId=864345302)
- [Revisão SQL AdvPL/TLPP da TOTVS](https://raw.githubusercontent.com/totvs/engpro-advpl-tlpp-skills/main/skills/advpl-tlpp/sql-code-review/SKILL.md)

## Falhas e limites conhecidos

O caminho documentado `stout-skill-registry/scripts/query_registry.py` pode não
existir em todas as instalações. Nesse caso, consultar `registry.json` e usar
as ferramentas existentes do Ledger; não fabricar um resultado de overlap.
Campos nativos sem legenda devem ser preservados e ficar `A VALIDAR`.
