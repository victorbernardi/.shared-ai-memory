import os
import sys
import yaml
import json
import io
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from jsonschema import validate, ValidationError

# Reconfigura o output para UTF-8 (Corta o mal pela raiz no Windows)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Shared Core Path (Default Stout Standard)
shared_core_path = r'C:\Projetos\Stout\scripts\core'
if shared_core_path not in sys.path:
    sys.path.append(shared_core_path)

try:
    import engine
except ImportError:
    engine = None

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    
    rules_path: str = './_config/config/rules.yaml'
    rules_schema_path: str = './_config/config/rules.schema.json'
    skills_schema_path: str = './_config/config/skills.schema.json'
    
    local_skills_path: str = './skills'
    global_skills_path: str = os.path.expanduser('~/.shared-ai-memory/.gemini/skills')

    def validate_config(self, data: dict, schema_path: str):
        """Valida um dicionário contra um arquivo de schema JSON."""
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        try:
            validate(instance=data, schema=schema)
            return True
        except ValidationError as e:
            print(f"[ERROR] Validacao falhou [{schema_path}]: {e.message}")
            raise e

    def load_rules(self):
        if not Path(self.rules_path).exists():
            return []
        with open(self.rules_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if data:
            self.validate_config(data, self.rules_schema_path)
            return data.get('rules', [])
        return []

    def get_engine(self, rules):
        if engine:
            return engine.BusinessRuleEngine(rules)
        return None

config = Config()
