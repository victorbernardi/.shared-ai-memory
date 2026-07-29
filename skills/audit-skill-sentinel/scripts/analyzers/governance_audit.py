"""
Analyzer de governanca.

Avalia maturidade de governanca: logging, rate limits, confirmacoes,
audit trail, alertas. Baseado no padrao de referencia do instagram/scripts/governance.py.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from config import GOVERNANCE_LEVELS


_EXTERNAL_INTEGRATION_PATTERN = re.compile(
    r"(?:\brequests\b|\bhttpx\b|\baiohttp\b|\bboto3\b|\bopenai\b|"
    r"\bplaywright\b|\bselenium\b|\burllib\.request\b|\bgoogle\.generativeai\b)",
    re.I,
)
_EXTERNAL_DESTRUCTIVE_PATTERN = re.compile(
    r"(?:\b(?:requests|httpx)\.(?:post|put|delete|patch)\s*\(|"
    r"\bgit\s+(?:push|merge|reset|clean)\b|"
    r"\b(?:publish|send_email|send_message)\s*\()",
    re.I,
)


def _read_sources(skill_data: Dict[str, Any]) -> List[str]:
    sources: List[str] = []
    skill_path = Path(skill_data["path"])
    for rel_path in skill_data.get("python_files", []):
        filepath = skill_path / rel_path
        if not filepath.exists():
            continue
        try:
            sources.append(filepath.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    return sources


def _has_external_integrations(sources: Iterable[str]) -> bool:
    return any(_EXTERNAL_INTEGRATION_PATTERN.search(source) for source in sources)


def _has_external_destructive_action(sources: Iterable[str]) -> bool:
    return any(_EXTERNAL_DESTRUCTIVE_PATTERN.search(source) for source in sources)


def _is_valid_safe_local_profile(sources: Iterable[str]) -> bool:
    """Aceita perfil seguro somente sem integrações ou mutações externas."""

    source_list = list(sources)
    return not _has_external_integrations(source_list) and not _has_external_destructive_action(source_list)


def _detect_governance_level(skill_data: Dict[str, Any], skill_path: Path) -> int:
    """Detecta nivel de maturidade de governanca."""
    has_action_log = False
    has_rate_limit = False
    has_confirmation = False
    has_warnings = False

    for rel_path in skill_data.get("python_files", []):
        filepath = skill_path / rel_path
        if not filepath.exists():
            continue
        try:
            source = filepath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if re.search(r'(?:action_log|log_action|audit_log)', source, re.I):
            has_action_log = True
        if re.search(r'(?:rate_limit|check_rate|RateLimitExceeded)', source, re.I):
            has_rate_limit = True
        if re.search(r'(?:requires_confirmation|confirmation_request|--confirm)', source, re.I):
            has_confirmation = True
        if re.search(r'(?:warning_threshold|RATE_LIMIT_WARNING|warnings?\s*\.append)', source, re.I):
            has_warnings = True

    if has_action_log and has_rate_limit and has_confirmation and has_warnings:
        return 4
    elif has_action_log and has_rate_limit and has_confirmation:
        return 3
    elif has_action_log and has_rate_limit:
        return 2
    elif has_action_log:
        return 1
    return 0


def analyze(skill_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
    """Analisa governanca de uma skill. Retorna (score, findings)."""
    findings: List[Dict[str, Any]] = []
    skill_name = skill_data["name"]
    skill_path = Path(skill_data["path"])
    sources = _read_sources(skill_data)

    if skill_data.get("sentinel_profile") == "safe-local" and _is_valid_safe_local_profile(sources):
        return 100.0, [{
            "skill_name": skill_name,
            "dimension": "governance",
            "severity": "info",
            "category": "safe_local_profile",
            "title": "Perfil safe-local validado",
            "description": "A skill não executa mutações externas nem integrações de API; controles de rate limit e confirmação não são aplicáveis.",
        }]

    level = _detect_governance_level(skill_data, skill_path)
    score = level * 25.0  # 0=0, 1=25, 2=50, 3=75, 4=100
    has_external_integrations = _has_external_integrations(sources)

    # Findings baseados no nivel
    if level == 0:
        findings.append({
            "skill_name": skill_name,
            "dimension": "governance",
            "severity": "high",
            "category": "no_governance",
            "title": "Sem modulo de governanca",
            "description": "A skill nao tem nenhum mecanismo de governanca. "
                           "Isso significa que acoes nao sao rastreadas e nao ha controle de taxa.",
            "recommendation": "Criar governance.py com GovernanceManager (action log + rate limiting). "
                              "Referenciar instagram/scripts/governance.py como modelo.",
            "effort": "medium",
            "impact": "high",
        })

    if level < 2 and has_external_integrations:
        findings.append({
            "skill_name": skill_name,
            "dimension": "governance",
            "severity": "medium",
            "category": "no_rate_limiting",
            "title": "Sem rate limiting",
            "description": "Chamadas API nao tem controle de taxa, risco de bloqueio por excesso de uso.",
            "recommendation": "Implementar check_rate_limit() antes de chamadas a APIs externas",
            "effort": "medium",
            "impact": "high",
        })

    if level < 3:
        has_destructive = _has_external_destructive_action(sources)

        if has_destructive:
            findings.append({
                "skill_name": skill_name,
                "dimension": "governance",
                "severity": "medium",
                "category": "no_confirmation",
                "title": "Acoes destrutivas sem confirmacao",
                "description": "Skill tem acoes que modificam dados externos mas sem 2-step confirmation",
                "recommendation": "Implementar padrao de confirmacao: requires_confirmation() + create_confirmation_request()",
                "effort": "medium",
                "impact": "high",
            })

    if level >= 3:
        # Bonus: verificar se o audit log tem consulta
        has_cli = False
        for rel_path in skill_data.get("python_files", []):
            filepath = skill_path / rel_path
            if not filepath.exists():
                continue
            try:
                source = filepath.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if "get_recent_actions" in source or "__main__" in source:
                has_cli = True

        if not has_cli:
            findings.append({
                "skill_name": skill_name,
                "dimension": "governance",
                "severity": "info",
                "category": "no_audit_cli",
                "title": "Audit log sem CLI de consulta",
                "recommendation": "Adicionar modo CLI para consultar acoes recentes: python governance.py",
                "effort": "low",
                "impact": "low",
            })

    # Registrar nivel como info
    findings.append({
        "skill_name": skill_name,
        "dimension": "governance",
        "severity": "info",
        "category": "governance_level",
        "title": f"Nivel de governanca: {level} - {GOVERNANCE_LEVELS.get(level, '?')}",
        "description": f"Maturidade de governanca detectada: nivel {level}/4",
    })

    return max(0.0, min(100.0, score)), findings
