import sys
import argparse
from pathlib import Path

# Garante que o diretório raiz e o src estejam no path
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.router import router

def list_skills():
    """Lista todas as habilidades descobertas."""
    print(f"\n{'ID':<25} {'NOME':<30} {'DOMÍNIO':<20} {'LVL':<5}")
    print("-" * 80)
    for skill in router.skills_cache:
        sid = skill.get('id', 'N/A')
        name = skill.get('name', 'N/A')[:28]
        domain = skill.get('domain', 'N/A')
        level = skill.get('level', 'N/A')
        print(f"{sid:<25} {name:<30} {domain:<20} {level:<5}")
    print(f"\nTotal: {len(router.skills_cache)} habilidades encontradas.")

def show_info(skill_id):
    """Exibe metadados detalhados de uma habilidade."""
    skill = router.get_skill_by_id(skill_id)
    if not skill:
        print(f"[-] Erro: Skill '{skill_id}' nao encontrada.")
        return

    print(f"\n--- METADADOS DA SKILL: {skill_id} ---")
    for key, value in skill.items():
        if key != 'path':
            print(f"{key.upper()}: {value}")
    print(f"PATH: {skill['path']}")

def test_skill(skill_id, query):
    """Testa a geração de instruções e recursos da habilidade."""
    skill = router.get_skill_by_id(skill_id)
    if not skill:
        print(f"[-] Erro: Skill '{skill_id}' nao encontrada.")
        return

    context = {"query": query, "intent": "cli_test"}
    instruction = router.build_instruction(skill_id, context)
    resources = router.resolve_resources(skill_id)

    print(f"\n--- TESTANDO SKILL: {skill_id} ---")
    print(f"[CONTEXTO] Query: {query}")
    
    print("\n[PROMPT GERADO (LEVEL 2)]")
    print("-" * 40)
    print(instruction)
    print("-" * 40)

    if resources:
        print("\n[RECURSOS MAPEADOS (LEVEL 3)]")
        for res in resources:
            print(f"-> {res}")
    else:
        print("\n[RECURSOS] Nenhum recurso tecnico mapeado para esta skill.")

def main():
    parser = argparse.ArgumentParser(description="Stout Skill Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponiveis")

    # Comando: list
    subparsers.add_parser("list", help="Listar todas as habilidades disponiveis")

    # Comando: info
    info_parser = subparsers.add_parser("info", help="Exibir detalhes de uma habilidade")
    info_parser.add_argument("skill_id", help="ID da habilidade")

    # Comando: test
    test_parser = subparsers.add_parser("test", help="Testar geracao de instrucoes")
    test_parser.add_argument("skill_id", help="ID da habilidade")
    test_parser.add_argument("--query", required=True, help="Query de teste para o prompt")

    args = parser.parse_args()

    if args.command == "list":
        list_skills()
    elif args.command == "info":
        show_info(args.skill_id)
    elif args.command == "test":
        test_skill(args.skill_id, args.query)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
