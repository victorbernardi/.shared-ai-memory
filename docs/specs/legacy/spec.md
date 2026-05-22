# Spec: Arquitetura Dual-Motor Antigravity (Stout Edition)

## Objetivo

Resolver a instabilidade sistêmica e o estouro de limite de ferramentas MCP através da criação de um ambiente de desenvolvimento isolado (Stout) que não polua o ambiente de negócio (Inova).

## Arquitetura Proposta

1. **Motor Produção (PROD):** Localizado em `c:\Motores-LLM\antigravity`. Usado para execução estável.
2. **Motor Desenvolvimento (STOUT):** Localizado em `C:\Projetos\Stout\antigravity`. Usado para modificações em skills e configurações.
3. **Memória Universal:** Pastas `brain/`, `knowledge/` e `scratch/` permanecem no diretório global para persistência.
4. **Troca de Perfil:** Script PowerShell para alternar symlinks/junctions entre PROD e STOUT.

## Critérios de Sucesso

- Antigravity operando com < 100 ferramentas.
- Configurações carregadas do Stout quando o agente for iniciado em `C:\Projetos\Inova`.
- Nenhuma modificação direta nos arquivos de IA dentro da pasta de negócio.

---

# Spec: Gemini CLI Builder (Resilient Architecture)

## Objetivo

Estabelecer o motor `gemini-cli` em `C:\Motores-LLM` como o "Builder" oficial do ecossistema, utilizando uma arquitetura resiliente que previna a perda de regras devido ao comportamento nativo de sobreposição (save_memory) do CLI.

## Protocolo de Separação de Responsabilidades (Dual-File)

Para evitar poluição da Golden Copy e destruição das regras de instrução, a arquitetura usará dois arquivos:

### 1. `ANTIGRAVITY.md` (As Regras do Builder)

- **Função:** Manifesto cognitivo e mandamentos do agente.
- **Resiliência:** Imune a sobreposições do motor nativo.
- **Conteúdo:**
  - Regra de Soberania (Usar `canary-deployment` para alterar a Golden Copy).
  - Regra de Validação de Junctions.
  - Lógica de sincronização do ambiente de desenvolvimento (`Stout`) para a Golden Copy.

### 2. `GEMINI.md` (O Template de Telemetria)

- **Função:** Arquivo de inicialização "zerado" para atuar como template base da Golden Copy.
- **Resiliência:** Espera-se que seja sobrescrito no runtime.
- **Conteúdo:** Apenas cabeçalhos de identificação da versão do motor e placeholders estruturais (Runtime State, MCP Status). **Nenhuma** regra de comportamento deve residir aqui.

## Proteção da Golden Copy

O agente é expressamente proibido de registrar telemetria de sessão (runtime) nos arquivos dentro de `C:\Motores-LLM\`. A telemetria real será gerenciada pelo wrapper no ambiente onde o junction está ativo (ex: `~/.gemini/`).

## Validação

- Ambos os arquivos (`GEMINI.md` e `ANTIGRAVITY.md`) devem ser gerados em `C:\Motores-LLM\gemini-cli\`.
- O plano deve prever a criação de ambos com seus respectivos propósitos.
