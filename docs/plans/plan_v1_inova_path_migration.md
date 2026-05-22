# Plano de Estratégia: Atualização de Paths Hardcoded (Inova)

Este plano define a abordagem para remover referências ao diretório antigo `C:\Projetos\Inova\Potencial Clientes` e adotar o padrão `shared/config.py`.

## 1. Objetivos
- Eliminar referências absolutas obsoletas em 52 scripts.
- Implementar descoberta dinâmica do diretório `shared`.
- Garantir que o pipeline possa ser movido sem quebrar os caminhos.

## 2. Abordagem Técnica

### 2.1 Snippet Padrão de Injeção
Para scripts que não estão na raiz do projeto, utilizaremos o seguinte padrão no topo do arquivo:

```python
import sys
from pathlib import Path as _Path

# Localiza a raiz do projeto (C:\Projetos\Inova) subindo N níveis
# Exemplo para um script em pipelines/potencial-clientes/00_Motor_Identidade/scripts/
_project_root = _Path(__file__).parents[3] 
_shared_dir = _project_root / "shared"

if str(_shared_dir) not in sys.path:
    sys.path.insert(0, str(_shared_dir))

from config import POTENCIAL_CLIENTES, SHARED_DATA
```

### 2.2 Mapeamento de Substituição
| Origem (Antigo) | Destino (Novo/Config) |
|---|---|
| `C:\Projetos\Inova\Potencial Clientes` | `POTENCIAL_CLIENTES` |
| `...\Potencial Clientes\05_Motor_Identidade` | `POTENCIAL_CLIENTES / "00_Motor_Identidade"` |
| `...\Potencial Clientes\01_DNA` | `POTENCIAL_CLIENTES / "01_DNA"` |
| `...\Potencial Clientes\02_Faturamento` | `POTENCIAL_CLIENTES / "02_Faturamento"` |
| `...\Potencial Clientes\03_Potencial` | `POTENCIAL_CLIENTES / "03_Potencial"` |
| `...\Potencial Clientes\04_Estrategia` | `POTENCIAL_CLIENTES / "04_Estrategia"` |
| `...\Potencial Clientes\06_Segmentacao` | `POTENCIAL_CLIENTES / "05_Segmentacao"` |

## 3. Ordem de Execução
1.  **Scripts de Raiz e Orquestradores:** `ligar_motores.py`.
2.  **Scripts de Produção (00-05):** Arquivos em `pipelines/`.
3.  **Scripts de Suporte e Documentação:** Arquivos em `99_Documentacao/`.
4.  **Rascunhos e Diagnósticos:** Pasta `rascunhos/`.

## 4. Validação
- Executar `ligar_motores.py` (dry-run ou verificação de paths).
- Rodar `grep` (Select-String) final para confirmar erro zero de referências antigas.

---
**Status:** Aguardando Aprovação (Standby Mode)
**Autor:** Gemini CLI Builder
