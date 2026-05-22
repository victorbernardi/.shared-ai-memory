# Plan v1.0 — Implementação Modo Interativo CLI

## 1. Abordagem Técnica
Criar uma função un_interactive_panel() que encapsula a lógica de busca e exibição em um loop while True. Utilizaremos o componente Prompt da biblioteca ich para capturar a entrada do usuário de forma elegante.

## 2. Passos de Execução
1. **Refatoração do Main:** Modificar o ponto de entrada para detectar se argumentos foram passados. Se não, inicia o modo painel.
2. **Loop de Controle:**
   - Limpar tela (console.clear()).
   - Solicitar entrada (console.input).
   - Processar busca (reutilizando show_cli_layout).
   - Aguardar confirmação antes de limpar novamente.
3. **Otimização:** Garantir que _load_master() seja chamado apenas uma vez no início da sessão interativa.

## 3. Estratégia de Teste (v11.8)
- Executar python scripts/seo_ge_cli.py (sem argumentos).
- Realizar busca por "RIVELLI".
- Realizar nova busca por "JOSE RONALDO" sem sair do script.
- Digitar "0" e validar encerramento gracioso.
- Validar que o comando python scripts/seo_ge_cli.py --busca RIVELLI continua funcionando (retrocompatibilidade).
