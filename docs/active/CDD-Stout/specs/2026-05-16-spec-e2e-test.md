# Especificação Técnica: End-to-End CDD Test (Hello Stout)

**Data:** 2026-05-16
**Status:** Aprovada
**ID:** FR-001

## 1. Objetivo

Criar um script simples (`src/tools/hello_stout.py`) que imprima uma mensagem formatada para comprovar que a Linha de Montagem de Subagentes consegue executar código TDD de ponta a ponta.

## 2. Requisitos Funcionais

- **FR-001:** O script deve ter uma função `get_hello_message()` que retorne a string "Hello, Stout Elite!".
- **T-001:** Deve existir um teste em `tests/test_hello_stout.py` que valide essa função.

## 3. Matriz de Rastreabilidade

| SOW | FR | Teste |
| :--- | :--- | :--- |
| AC-1 | FR-001 | T-001 |
