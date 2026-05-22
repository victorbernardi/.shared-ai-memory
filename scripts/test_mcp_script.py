# test_mcp_script.py
import os


def load_get_access_token():
    """Extrai e compila apenas a função get_access_token do script."""
    script_path = os.path.join(os.path.dirname(__file__), "google-dev-knowledge-mcp.py")
    with open(script_path) as f:
        source = f.read()
    func_source = source.split("token = get_access_token()")[0]
    namespace = {}
    exec(compile(func_source, script_path, "exec"), namespace)
    return namespace["get_access_token"]


def test_get_access_token_returns_string():
    get_access_token = load_get_access_token()
    token = get_access_token()
    assert isinstance(token, str), f"Esperado str, recebeu {type(token)}"
    assert len(token) > 20, "Token parece inválido (muito curto)"
    print(f"[OK] Token gerado: {token[:20]}...")


if __name__ == "__main__":
    test_get_access_token_returns_string()
    print("Todos os testes passaram.")
