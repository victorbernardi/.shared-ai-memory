# Protocolos de Scaffolding ICM

## Fase 1: Inicialização

1. Confirmar domínio (`Stout` ou `Inova`)
2. Confirmar nome do projeto (kebab-case)
3. Criar/confirmar diretório do projeto em `<raiz>\<dominio>\Projetos\<projeto>\`

## Fase 2: Templates

1. Criar `00_research/` com `CONTEXT.md` (cold storage) e `references/`
2. Gerar `SKILL.md` fino a partir do template
3. Gerar `CONTEXT.md` do pipeline a partir do template
4. Para cada estágio na lista:
   - Criar diretório `NN_nome-do-estagio/`
   - Gerar `CONTEXT.md` a partir do template de estágio
   - Criar `output/`
   - Criar `scripts/` (se aplicável)
5. Gerar `requirements.txt` na raiz do projeto com as dependências comuns (pandas, numpy, etc.)
6. Para cada estágio que tenha dependências específicas: gerar `requirements.txt` dentro do estágio

## Fase 3: Infraestrutura

1. Criar `.GCC/branches/<projeto>/` na raiz do domínio
2. Criar thin wrappers em `.gemini/skills/` apontando para o projeto
3. Criar thin wrappers em `.agents/skills/` para Antigravity

**Bootstrap Python/uv (obrigatório para projetos Python):**

```powershell
cd <raiz-do-projeto>
uv venv --python 3.12
uv pip install -r requirements.txt
```

Para estágios com `requirements.txt` próprio:

```powershell
cd <raiz-do-projeto>\<estagio>
uv venv --python 3.12
uv pip install -r requirements.txt
```

Validar:

```powershell
uv run python -c "import sys; print(f'Python {sys.version[:5]} OK')"
```

**NÃO assumir** que o Anaconda está disponível. Todo projeto nasce com `uv` como runtime.

## Fase 4: Validação

1. Verificar que todos os CONTEXT.md têm as 8 seções
2. Verificar encoding UTF-8
3. Verificar que SKILL.md tem YAML frontmatter válido
4. Verificar estrutura de diretórios completa
5. Verificar que `.venv` existe e `uv run python` resolve para Python 3.12
