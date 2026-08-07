# Mapa TOTVS → Inova (Protheus no Fabric)

Referência de adaptação entre as skills oficiais TOTVS (AdvPL/TLPP) e a
realidade Inova (Python + SQL lendo Protheus exposto no Microsoft Fabric).

Repositório oficial: https://github.com/totvs/engpro-advpl-tlpp-skills

## 1. Skills oficiais TOTVS e aplicabilidade (seis relevantes)

### sql-code-review (aplicável — adaptar)

Revisão universal de SQL é aproveitada: projeção explícita, filtros por chave,
joins com cardinalidade correta, sem `SELECT *`, atenção a funções em colunas
indexadas. Adaptar o destino: **Fabric/JDBC**, não DBAccess. Fornece checks de
SQL universal adaptáveis ao contexto Inova. Manter a exigência de evidência da
fonte.

### sql-optimization (aplicável — adaptar)

Princípios de otimização (evitar scans desnecessários, empurrar filtros,
reduzir linhas cedo) aplicam-se ao Fabric via **pushdown**. Medir custo de scan
no Fabric; plano nativo AdvPL não se aplica. Fornece checks de SQL universal
adaptáveis ao contexto Inova.

### query-builder (referência apenas)

Constrói SQL em AdvPL. **Não aplicável** a pipelines Python/Fabric: não
substitui `ConexaoFabric`/`load_query`/`query_loader`. Consultar apenas como
referência de intenção de query; nunca usar para gerar SQL de pipeline Inova.
Referência AdvPL/DBAccess apenas.

### data-dictionary-lookup (referência apenas)

Dicionário nativo TOTVS descreve campos AdvPL/DBAccess. Como referência de
significado de campos, se o destino for demonstravelmente AdvPL/DBAccess. Para
Python/Fabric, o contrato de campos vem das fontes observadas
(`references/inova-source-contract.md`), não do dicionário. Referência
AdvPL/DBAccess apenas.

### code-review (referência apenas)

Revisão de código AdvPL/TLPP. **Não aplicável** a Python/Fabric; referência
apenas quando a consulta revisada tocar código AdvPL/TLPP. Referência
AdvPL/TLPP apenas.

### refactor (referência apenas)

Refatoração de código AdvPL/TLPP. **Não aplicável** a Python/Fabric; referência
apenas quando a consulta revisada tocar código AdvPL/TLPP. Referência
AdvPL/TLPP apenas.

## 2. Conceitos AdvPL/DBAccess → status no Python/Fabric

Cada item abaixo é **não aplicável / requer evidência** quando o alvo é
Python/Fabric:

- **ChangeQuery** — intercepta SQL no runtime AdvPL; não existe no Fabric/JDBC.
- **RetSqlName** — resolve alias de tabela no DBAccess; não aplicável ao JDBC.
- **FWxFilial** — prefixo de filial no SQL nativo; sem equivalente direto no
  Fabric — a coluna de filial deve ser tratada como dado, com evidência.
- **FWExecStatement** — execução de SQL no runtime AdvPL; não substitui
  `ConexaoFabric`/`load_query`/`query_loader`.
- **Workarea** — conceito de área de trabalho AdvPL; não aplicável em Python.
- **NOLOCK** — hint de leitura no DBAccess/SQL Server nativo; **não aplicar**
  em consultas Fabric/JDBC sem evidência de suporte e sem justificativa de
  consistência.

Usar qualquer um desses sem evidência é achado **ALTA**.

## 3. O que a revisão Inova deve exigir

- **ConexaoFabric** — conexão explícita e documentada ao Fabric.
- **JDBC** — driver/jdbc string corretos; credenciais fora do código.
- **SQL files** — SQL de leitura em arquivos `.sql` ou literais revisados com
  o mesmo contrato; sem concatenação de inputs.
- **load_query/query_loader** — uso correto do loader da Inova
  (`from shared.query_loader import load_query` +
  `load_query(Path("queries/sa1010.sql"))`); revisar o que ele entrega (tipos,
  pushdown, cache).
- **Cache** — chave e proveniência do cache explicitadas; nunca assumir cache.
- **Pushdown** — filtros/projeções/joins empurrados ao Fabric; `SELECT *` é
  achado.
- **Duplicate scan** — múltiplas leituras da mesma fonte no pipeline devem ser
  justificadas; leitura repetida sem motivo é achado de custo.

## 4. Decisão final

Todo item adaptado de skill TOTVS só é válido com **evidência** no alvo
Fabric/JDBC. Sem evidência de aplicabilidade, o status é **REVIEW INCOMPLETE**
ou achado com severidade — nunca assumir equivalência AdvPL ↔ Fabric.
