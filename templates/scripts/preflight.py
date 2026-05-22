"""
preflight.py
============
Validação preventiva de catálogos antes do runtime.
Executa no startup e no hot-reload para garantir schemas válidos,
referências consistentes e regras sem conflitos fatais.
"""

import json
from pathlib import Path
from jsonschema import validate, ValidationError, Draft202012Validator
import yaml


class PreflightValidator:
    """
    Valida todos os artefatos declarativos antes de carregá-los.
    Falha rápido (fail-fast) com mensagens acionáveis.
    """

    def __init__(self, config_dir: Path):
        self.config_dir = Path(config_dir)
        self.errors: list[dict] = []
        self.warnings: list[dict] = []

    def run_all(self) -> dict:
        """Executa toda a bateria de validações."""
        self._check_audit_gate()
        self._validate_json_schemas()
        self._validate_rules_catalog()
        self._validate_no_duplicate_priorities()

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }

    def _check_audit_gate(self):
        """Check for the existence of .audit_gate in the project root."""
        gate_path = Path(".audit_gate")
        if gate_path.exists():
            try:
                # Tenta UTF-8 primeiro, depois Latin-1 como fallback
                try:
                    gate_content = gate_path.read_text(encoding="utf-8").strip()
                except UnicodeDecodeError:
                    gate_content = gate_path.read_text(encoding="latin-1").strip()
                
                self.errors.append({
                    "file": ".audit_gate",
                    "check": "error_immunity_protocol",
                    "message": f"SISTEMA TRAVADO: Falha pendente de auditoria. Detalhes: {gate_content}",
                })
            except Exception as e:
                self.errors.append({
                    "file": ".audit_gate",
                    "check": "error_immunity_protocol",
                    "message": f"SISTEMA TRAVADO: .audit_gate detectado, mas erro ao ler: {str(e)}",
                })

    def _validate_json_schemas(self):
        """1. Cada .schema.json deve ser um schema JSON válido."""
        for schema_file in self.config_dir.rglob("*.schema.json"):
            try:
                with open(schema_file, encoding="utf-8") as f:
                    schema = json.load(f)
                Draft202012Validator.check_schema(schema)
            except Exception as e:
                self.errors.append({
                    "file": str(schema_file),
                    "check": "schema_self_validation",
                    "message": f"Schema inválido: {e}",
                })

    def _validate_rules_catalog(self):
        """3. rules.yaml deve passar no business_rules schema."""
        if (self.config_dir / "data" / "config").exists():
            base_path = self.config_dir / "data" / "config"
        else:
            base_path = self.config_dir

        path = base_path / "rules.yaml"
        schema_path = base_path / "rules.schema.json"
        
        if not path.exists():
            self.errors.append({"file": str(path), "check": "exists", "message": "Arquivo de regras não encontrado"})
            return

        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            
            if schema_path.exists():
                with open(schema_path, encoding="utf-8") as f:
                    schema = json.load(f)
                validate(instance=data, schema=schema)
            
            if not isinstance(data, dict) or "rules" not in data:
                self.errors.append({"file": str(path), "check": "structure", "message": "Chave 'rules' ausente"})
            
            ids = [r.get("id") for r in data.get("rules", []) if r.get("id")]
            if len(ids) != len(set(ids)):
                self.errors.append({"file": str(path), "check": "unique_ids", "message": "IDs de regras duplicados"})
        except ValidationError as e:
            self.errors.append({"file": str(path), "check": "schema_validation", "message": e.message})
        except Exception as e:
            self.errors.append({"file": str(path), "check": "yaml_parse", "message": str(e)})

    def _validate_no_duplicate_priorities(self):
        """5. Alerta se múltiplas regras têm a mesma prioridade."""
        if (self.config_dir / "data" / "config").exists():
            rules_path = self.config_dir / "data" / "config" / "rules.yaml"
        else:
            rules_path = self.config_dir / "rules.yaml"

        if not rules_path.exists():
            return

        try:
            with open(rules_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception:
            return
            
        if not data:
            return

        priorities = {}
        for rule in data.get("rules", []):
            p = rule.get("priority", 0)
            priorities.setdefault(p, []).append(rule.get("id", "?"))

        for priority, ids in priorities.items():
            if len(ids) > 1:
                self.warnings.append({
                    "file": str(rules_path),
                    "check": "duplicate_priority",
                    "message": f"Prioridade {priority} compartilhada por: {', '.join(ids)}",
                })

# --- USO ---
if __name__ == "__main__":
    import sys
    config_path = Path("data/config") if Path("data/config").exists() else Path(".")
    validator = PreflightValidator(config_path)
    result = validator.run_all()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["valid"]:
        sys.exit(1)
