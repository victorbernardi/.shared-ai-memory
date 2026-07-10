#!/usr/bin/env python3
"""
Busca semântica de skills no stout-skill-registry.
Retorna lista ranqueada de skills ativas relevantes para uma query.
"""
import sys
import json
import argparse
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = Path(__file__).parent
REGISTRY_PATH = SCRIPT_DIR.parent.parent / "stout-skill-registry" / "registry.json"
DEFAULT_THRESHOLD = 60


def load_registry() -> list[dict]:
    if not REGISTRY_PATH.exists():
        print(f"[ERRO] registry.json não encontrado em {REGISTRY_PATH}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return [s for s in data.get("skills", []) if s.get("status") == "active"]


def tokenize(text: str) -> set[str]:
    stopwords = {"de", "do", "da", "e", "para", "com", "em", "o", "a", "os", "as", "um", "uma"}
    return {w.lower() for w in text.replace("-", " ").split() if w.lower() not in stopwords}


def score_skill(skill: dict, query_tokens: set[str]) -> int:
    score = 0
    role_tokens = tokenize(skill.get("role", ""))
    trigger_tokens: set[str] = set()
    for t in skill.get("triggers", []):
        trigger_tokens |= tokenize(t)

    # Role match: até 60 pontos
    if role_tokens:
        overlap = query_tokens & role_tokens
        score += int((len(overlap) / max(len(query_tokens), 1)) * 60)

    # Trigger match: até 40 pontos
    if trigger_tokens:
        overlap = query_tokens & trigger_tokens
        score += int((len(overlap) / max(len(query_tokens), 1)) * 40)

    return min(score, 100)


def search(query: str, threshold: int = DEFAULT_THRESHOLD) -> list[dict]:
    skills = load_registry()
    query_tokens = tokenize(query)
    results = []
    for skill in skills:
        s = score_skill(skill, query_tokens)
        if s >= threshold:
            results.append({**skill, "_score": s})
    return sorted(results, key=lambda x: x["_score"], reverse=True)


def main():
    parser = argparse.ArgumentParser(description="Busca skills locais por semântica")
    parser.add_argument("--query", required=True, help="Termo de busca")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD,
                        help=f"Score mínimo 0-100 (default: {DEFAULT_THRESHOLD})")
    parser.add_argument("--json", action="store_true", help="Output em JSON")
    args = parser.parse_args()

    results = search(args.query, args.threshold)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    if not results:
        print(f"Nenhuma skill local encontrada para '{args.query}' (threshold={args.threshold}%)")
        return

    print(f"Skills locais para '{args.query}' ({len(results)} encontradas):\n")
    for r in results:
        print(f"  [{r['_score']:3d}%] {r['name']} — {r['role']}")
        print(f"         Tier {r.get('tier','?')} | {r.get('category','?')} | triggers: {', '.join(r.get('triggers',[])[:3])}")
    print()


if __name__ == "__main__":
    main()
