# 🗺️ Plano de Engenharia: Resolução de Caminhos Globais no Sandbox (Leituras de Cognição)

> **Status:** STANDBY MODE (Aguardando aprovação humana)
> **Versão:** Plan v1.0
> **ID do Plano:** `plan_v1_leitura_cognicao_sandbox`
> **Projeto:** Stout Lab CDD
> **Data:** 2026-05-28
> **Especificação Relacionada:** [spec_v1_leitura_cognicao_sandbox.md](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/docs/specs/spec_v1_leitura_cognicao_sandbox.md)

---

## 🚫 Trava de Segurança (Standby Mode)

> [!WARNING]
> **STANDBY MODE ATIVADO:** Este plano foi elaborado seguindo a Fase de Estratégia.
> O agente está impedido de realizar qualquer modificação de código físico nos arquivos de produção até que o Victor aprove explicitamente as alterações propostas.

---

## 🛠️ Proposed Changes (Mudanças Propostas)

O plano de modificações está isolado em 3 componentes e ordenado de forma lógica (dependências primeiro):

### 1. Configurações Globais

#### [MODIFY] [config.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/src/config.py)
* **Objetivo:** Adicionar os diretórios globais de cognição na whitelist padrão de segurança do sandbox.
* **Alteração:** Incluir `"~/.shared-ai-memory"` e `"~/.gemini"` no vetor `sandbox_allowed_dirs` (Linha 39).
* **Trecho Alvo:**
  ```python
  sandbox_allowed_dirs: List[str] = ["src/tools", "Research", "tests", "src/distributed"]
  ```
* **Trecho Novo:**
  ```python
  sandbox_allowed_dirs: List[str] = [
      "src/tools", 
      "Research", 
      "tests", 
      "src/distributed",
      "~/.shared-ai-memory",
      "~/.gemini"
  ]
  ```

---

### 2. Sandbox Engine

#### [MODIFY] [sandbox.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/src/core/sandbox.py)
* **Objetivo:** Suportar a expansão dinâmica do diretório home (`~`) e caminhos relativos ao Windows na inicialização do sandbox.
* **Alteração:** Alterar o list comprehension do construtor `__init__` na Linha 19 para expandir e resolver os caminhos de forma tolerante (`strict=False`), de forma que se a pasta ainda não existir, o sistema não quebre.
* **Trecho Alvo:**
  ```python
  self.allowed_dirs = [Path(d).resolve() for d in config.sandbox_allowed_dirs]
  ```
* **Trecho Novo:**
  ```python
  self.allowed_dirs = [Path(d).expanduser().resolve(strict=False) for d in config.sandbox_allowed_dirs]
  ```

---

### 3. Suite de Testes

#### [MODIFY] [test_sandbox.py](file:///C:/Projetos/Stout/Projetos/Configuration-Driven%20Development/tests/test_sandbox.py)
* **Objetivo:** Adicionar testes de unidade para provar empiricamente a robustez e segurança da expansão do home directory no sandbox.
* **Alteração:** Criar dois novos casos de teste no final do arquivo (`test_sandbox_allows_expanded_global_paths` e `test_sandbox_blocks_path_traversal_on_expanded_paths`), simulando caminhos com `~` expandido.
* **Código Novo a ser Adicionado:**
  ```python
  def test_sandbox_allows_expanded_global_paths(sandbox):
      """Valida que o sandbox permite a execução em caminhos globais expandidos."""
      # Mocks do config para simular ~ nas whitelists
      allowed_path = Path("~/.shared-ai-memory/dummy.py").expanduser().resolve(strict=False)
      
      # Mockamos allowed_dirs diretamente no sandbox
      with patch.object(sandbox, 'allowed_dirs', [allowed_path.parent]):
          # Deve passar sem PermissionError na validação de diretório
          sandbox._validate_action("execute_script", str(allowed_path))
          # Se não levantar exceção, o teste foi bem sucedido

  def test_sandbox_blocks_path_traversal_on_expanded_paths(sandbox):
      """Valida que o sandbox bloqueia tentativas de path traversal fora dos caminhos expandidos."""
      allowed_parent = Path("~/.shared-ai-memory").expanduser().resolve(strict=False)
      malicious_target = allowed_parent / ".." / "secret.txt"
      
      with patch.object(sandbox, 'allowed_dirs', [allowed_parent]):
          with pytest.raises(PermissionError) as exc_info:
              sandbox._validate_action("execute_script", str(malicious_target))
          assert "Acesso negado" in str(exc_info.value)
  ```

---

## 🧪 Verification Plan (Plano de Verificação)

### Automated Tests (Testes Automatizados)
1. **Verificação de Sandbox:** Executar a suite isolada de sandbox para testar as novas proteções:
   ```bash
   pytest tests/test_sandbox.py -v
   ```
2. **Regressão E2E:** Executar a suite completa do motor CDD para validar os 32 cenários históricos:
   ```bash
   pytest tests/ -v
   ```

### Manual Verification (Verificação Manual)
1. Rodar o motor de regras CDD simulando uma chamada de salvamento de contexto:
   ```bash
   python src/main.py
   ```
   *Critério de Aceitação:* O preflight-check e a ativação da regra `stout_unified_context_save` devem ser carregados sem disparar `PermissionError` para a pasta `.shared-ai-memory`.
