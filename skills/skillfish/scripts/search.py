#!/usr/bin/env python3
"""Busca skills compatíveis com Stout no npm registry."""
import argparse
import json
import urllib.request
import urllib.parse

NPM_SEARCH_URL = "https://registry.npmjs.org/-/v1/search"
STOUT_PREFIX = "skillfish"


def search_npm(query: str, size: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"text": f"{STOUT_PREFIX} {query}", "size": size})
    url = f"{NPM_SEARCH_URL}?{params}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read())
    return data.get("objects", [])


def is_stout_compatible(pkg: dict) -> bool:
    keywords = pkg.get("package", {}).get("keywords", [])
    return "stout" in keywords or "skillfish" in (pkg.get("package", {}).get("name", ""))


def main():
    parser = argparse.ArgumentParser(description="Busca skills no npm")
    parser.add_argument("--query", required=True, help="Termo de busca")
    parser.add_argument("--size", type=int, default=10, help="Máximo de resultados")
    args = parser.parse_args()

    print(f"Buscando skills para: '{args.query}'\n")
    results = search_npm(args.query, args.size)

    if not results:
        print("Nenhuma skill encontrada.")
        return

    compatible = [r for r in results if is_stout_compatible(r)]
    others = [r for r in results if not is_stout_compatible(r)]

    if compatible:
        print(f"✅ Skills compatíveis com Stout ({len(compatible)}):")
        for r in compatible:
            pkg = r["package"]
            print(f"  • {pkg['name']} v{pkg['version']} — {pkg.get('description', 'sem descrição')}")

    if others:
        print(f"\n⚠️  Outros resultados ({len(others)}):")
        for r in others[:5]:
            pkg = r["package"]
            print(f"  • {pkg['name']} v{pkg['version']} — {pkg.get('description', 'sem descrição')}")

    print("\nPara instalar: python scripts/install.py --package <nome>")


if __name__ == "__main__":
    main()
