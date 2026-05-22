# 🗺️ Esboço de Projeto: Migração Estrutural e Organização de Código (M3 Src)

> **Projeto:** Motor M3 — Potencial Clientes (Inova)
> **Status:** Proposto / Próxima Sessão
> **Documento de Planejamento:** `docs/plans/plan_v1_migracao_arquitetura_src_m3.md`

Este documento atua como o esboço do projeto e plano de ação estruturado para reorganizar a árvore de diretórios do motor M3. O objetivo é mover os códigos funcionais de extração, transformação e carga para o diretório `src/etl/`, eliminando a poluição visual na raiz e preservando a execução do runner.

---

## 📂 1. Estrutura Física: Antes vs. Depois

### Estrutura Atual (Poluição na Raiz):
```
03_Potencial/
├── extract.py         <-- Solto na raiz
├── transform.py       <-- Solto na raiz
├── load.py            <-- Solto na raiz
├── run.py             <-- Runner
├── Potencial Oficial FY26.xlsx
├── ESTUDO - ...xlsx
├── data/
└── src/
    └── tools/
        └── stout_promote.py
```

### Estrutura Alvo (Organização de Elite):
```
03_Potencial/
├── run.py             <-- ÚNICO script de execução na raiz (Ponto de Entrada)
├── Potencial Oficial FY26.xlsx
├── ESTUDO - ...xlsx
├── data/              <-- Caches e outputs (ignorados pelo Git)
├── docs/              <-- Documentações locais
└── src/
    ├── __init__.py    <-- Declaração de pacote Python
    ├── etl/
    │   ├── __init__.py
    │   ├── extract.py  <-- Movido e encapsulado
    │   ├── transform.py <-- Movido e encapsulado
    │   └── load.py     <-- Movido e encapsulado
    └── tools/
        └── stout_promote.py
```

---

## 🛠️ 2. Mapeamento das Alterações Técnicas

### A. Criação de Pacotes Python
* Criar os arquivos de inicialização vazios `src/__init__.py` e `src/etl/__init__.py` para permitir que o interpretador Python reconheça a pasta como módulos importáveis de forma limpa.

### B. Movimentação Física e Ajuste de Caminhos
* Mover fisicamente `extract.py`, `transform.py` e `load.py` para `src/etl/`.
* **Ajuste Crítico de Resolução do Shared (`sys.path`):** 
  Como os scripts estarão um nível mais profundo na árvore de diretórios, a linha que calcula o diretório compartilhado `/shared` no topo de cada script precisa ser ajustada:
  ```python
  # De: Path(__file__).parents[3] / "shared"
  # Para:
  _shared_dir = Path(__file__).parents[4] / "shared"
  ```

### C. Refatoração do Runner (`run.py`) na Raiz
O script principal que é chamado pelo Task Scheduler do Windows permanece no topo da raiz, mas agora atua apenas como o orquestrador que importa as funções de dentro de `src/`:
```python
# Alteração dos Imports no run.py:
from src.etl.extract import extract
from src.etl.transform import run_transform
from src.etl.load import save
```

---

## 🧪 3. Plano de Validação e Integridade

Para garantir que a reorganização do repositório ocorra sem efeitos colaterais na esteira de dados de produção:

- [ ] **Validação de Imports Locais:** Rodar uma compilação de sintaxe rápida no `run.py` para garantir que o interpretador local resolva todos os caminhos do `src/` e do `/shared`.
- [ ] **Teste de Execução Local:** Executar o pipeline `python run.py` de ponta a ponta, atestando que os pre-flights do sensor de recência e os post-flights de escrita física gravam os parquets locais e no `/shared` normalmente.
- [ ] **Verificação de Regressão Numérica:** Rodar o script `validate_pipeline.py` para atestar que os desvios de registros e somatórios matemáticos do potencial e chassi se mantêm em **0%** de variação após a migração.
