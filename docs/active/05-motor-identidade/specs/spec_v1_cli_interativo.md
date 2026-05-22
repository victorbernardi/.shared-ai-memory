# Spec v1.0 — Modo Interativo SEO_GE CLI

## 1. Problema
Atualmente, o script seo_ge_cli.py exige que o usuário execute o comando no terminal para cada busca (--busca "NOME"). Isso gera fricção na auditoria de múltiplos clientes, pois o script encerra após cada execução, obrigando a reinicialização e o recarregamento do Dataset Ouro (que é pesado).

## 2. Objetivo
Transformar o seo_ge_cli.py em uma ferramenta de "Painel de Controle" persistente, que permita buscas sucessivas em um loop interativo, mantendo o estado da aplicação e limpando a tela para uma melhor experiência visual (Dashboard).

## 3. Requisitos
- R1 (Loop): O script deve permanecer aberto até que o usuário digite "sair" ou "0".
- R2 (Input Dinâmico): Deve oferecer um prompt amigável via biblioteca rich.
- R3 (Higiene Visual): A tela deve ser limpa (console.clear()) a cada nova busca para manter o foco no cliente atual.
- R4 (Compatibilidade): Manter suporte ao modo de linha de comando direto (--busca) para casos de automação.

## 4. Design UI/UX
- Cabeçalho fixo com o status do motor.
- Prompt: 🔍 Digite o Nome ou CNPJ (sair=0): 
- Painel de resultados centralizado.

## 5. Critérios de Aceite
- O usuário consegue fazer 3 buscas seguidas sem o script fechar.
- O script fecha imediatamente ao digitar "0" ou "sair".
- O carregamento do Excel (_load_master) deve ocorrer apenas uma vez (se possível) para ganho de performance.
