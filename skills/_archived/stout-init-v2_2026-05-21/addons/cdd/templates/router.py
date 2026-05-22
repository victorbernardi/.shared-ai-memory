from typing import Any, List, Optional, Union
import yaml
import io
import sys
from pathlib import Path
import re
from datetime import datetime
from src.config import config
from src.gcc_controller import gcc

# Reconfigura o output para UTF-8 (Corta o mal pela raiz no Windows)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class SkillRouter:
    """
    Roteador que localiza e prepara instruções de Skills baseadas no Padrão de Pasta (Stout Standard).
    Implementa Progressive Disclosure (Nível 1, 2 e 3) com arquitetura Multi-Tier (Global + Local).
    """
    def __init__(self, skills_dirs: List[Union[str, Path]] = None):
        if skills_dirs is None:
            # Prioridade: Local primeiro, depois Global
            skills_dirs = [config.local_skills_path, config.global_skills_path]
        
        self.skills_dirs = [Path(d) for d in skills_dirs]
        self.skills_cache: List[dict] = []
        self._load_catalog()

    def _load_catalog(self):
        """
        Escaneia os diretórios de skills e carrega os metadados.
        """
        loaded_ids = set()
        self.skills_cache = []

        for d in self.skills_dirs:
            if not d.exists():
                continue

            for skill_folder in d.iterdir():
                if skill_folder.is_dir():
                    skill_file = skill_folder / 'SKILL.md'
                    if skill_file.exists():
                        metadata = self._extract_metadata(skill_file)
                        if metadata:
                            skill_id = metadata.get('id') or metadata.get('name') or skill_folder.name
                            if skill_id and skill_id not in loaded_ids:
                                metadata['id'] = skill_id
                                metadata['path'] = str(skill_file)
                                
                                # Validação opcional contra schema
                                if hasattr(config, 'skills_schema_path') and Path(config.skills_schema_path).exists():
                                    try:
                                        config.validate_config(metadata, config.skills_schema_path)
                                    except Exception as e:
                                        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
                                        print(f"[!] Aviso: Skill '{skill_id}' falhou na validacao: {error_msg[:100]}...")

                                self.skills_cache.append(metadata)
                                loaded_ids.add(skill_id)

    def _extract_metadata(self, file_path: Path) -> Optional[dict]:
        """Extrai apenas o frontmatter YAML de um arquivo SKILL.md."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
                if match:
                    return yaml.safe_load(match.group(1))
        except Exception:
            pass
        return None

    def get_skill_by_id(self, skill_id: str) -> Optional[dict]:
        """Busca os metadados de uma skill específica."""
        for skill in self.skills_cache:
            if skill.get("id") == skill_id:
                return skill
        return None

    def load_skill_level(self, skill_id: str, level: int, context: dict = None) -> dict:
        """
        Implementa Progressive Disclosure.
        """
        skill_meta = self.get_skill_by_id(skill_id)
        if not skill_meta:
            return {"error": f"Skill '{skill_id}' nao encontrada."}

        result = {
            "id": skill_meta["id"],
            "name": skill_meta["name"],
            "description": skill_meta.get("description", ""),
            "level_available": skill_meta.get("level", 1)
        }

        if level >= 2:
            result["instruction"] = self.build_instruction(skill_id, context or {})

        if level >= 3:
            result["resources"] = self.resolve_resources(skill_id)

        return result

    def build_instruction(self, skill_id: str, context: dict) -> str:
        """
        Gera a instrução final (Level 2 - Activation).
        """
        skill_meta = self.get_skill_by_id(skill_id)
        if not skill_meta:
            return f"[-] Skill '{skill_id}' nao encontrada."

        rationale = f"Ativando habilidade especializada '{skill_meta['name']}' (Level 2) via SkillRouter."
        gcc.commit_milestone(
            action=f"activate_skill:{skill_id}:level2",
            rationale=rationale,
            context=context
        )

        try:
            with open(skill_meta['path'], 'r', encoding='utf-8') as f:
                content = f.read()
                body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL).strip()
                final_instruction = body
                for key, value in context.items():
                    placeholder = f"{{{{{key}}}}}"
                    final_instruction = final_instruction.replace(placeholder, str(value))
                return final_instruction
        except Exception as e:
            return f"[-] Erro ao ler corpo da skill {skill_id}: {e}"

    def resolve_resources(self, skill_id: str) -> List[str]:
        """
        Resolve caminhos de recursos técnicos (Level 3 - Execution).
        """
        skill_meta = self.get_skill_by_id(skill_id)
        if not skill_meta:
            return []

        gcc.commit_milestone(
            action=f"activate_skill:{skill_id}:level3",
            rationale=f"Carregando recursos tecnicos (Level 3) para a skill '{skill_meta['name']}'.",
            context={"skill_id": skill_id}
        )

        resources = skill_meta.get('resources', [])
        resolved = []
        skill_folder = Path(skill_meta['path']).parent

        for res in resources:
            if res.startswith('./'):
                abs_path = (skill_folder / res[2:]).resolve()
                resolved.append(str(abs_path))
            else:
                resolved.append(res)
        
        return resolved

# Instância única para uso no projeto
router = SkillRouter()
