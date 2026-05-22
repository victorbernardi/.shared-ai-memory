from pathlib import Path
from datetime import datetime
import json
import io
import sys

# Reconfigura o output para UTF-8 (Corta o mal pela raiz no Windows)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class GCCController:
    """
    Git-Context-Controller (GCC) para rastreabilidade de marcos lógicos.
    Implementa o padrão Context Graph (Situation, Rationale, Action, Outcome).
    """
    def __init__(self, base_dir: str = '.GCC'):
        self.base_dir = Path(base_dir)
        self.branches_dir = self.base_dir / 'branches'
        self._initialize_structure()

    def _initialize_structure(self):
        """Inicializa a estrutura de diretórios do GCC."""
        self.branches_dir.mkdir(parents=True, exist_ok=True)
        main_file = self.base_dir / 'main.md'
        if not main_file.exists():
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write("# 🌐 GCC: Global Context Control\n\n")
                f.write(f"Inicializado em: {datetime.now().isoformat()}\n")
                f.write("Status: Ativo\n")

    def commit_milestone(self, action: str, rationale: str, context: dict, outcome: str = 'SUCCESS'):
        """
        Registra um marco lógico (Checkpoint) no histórico analítico.
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"checkpoint_{timestamp}.md"
        file_path = self.branches_dir / filename

        markdown_content = f"""# 📍 Checkpoint: {action}

- **Data:** {datetime.now().isoformat()}
- **Status:** {outcome}

## 🔍 Context Graph (Quadrantes)

### 1. Situação (Situation)
Mapeamento do estado exato e panorama no momento da ocorrência.
```json
{json.dumps(context, indent=2, ensure_ascii=False)}
```

### 2. Lógica (Rationale)
Raciocínio metodológico que justificou a escolha.
> {rationale}

### 3. Ação (Action)
Etapa pragmática executada.
- `{action}`

### 4. Resultado (Outcome)
Produto empírico e consequências.
- {outcome}: Ação registrada e contexto persistido.

---
*Gerado automaticamente pelo GCC Controller.*
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(file_path)

# Instância única para uso no projeto
gcc = GCCController()
