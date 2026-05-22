# Spec: SEO_GE Interactive Scanner (v1.0)

## 1. Objetivo
Criar uma interface única para auditoria, busca e unificação de grupos econômicos no projeto Motor Identidade. A ferramenta deve servir tanto para curadoria humana manual quanto para automação via agente de IA.

## 2. Requisitos Funcionais
- **RF01 (Busca Híbrida):** Alternar entre Cache Parquet (Velocidade) e Microsoft Fabric (Integridade).
- **RF02 (Diagnóstico SEO_GE):** Listar integrantes atuais de um grupo e sugerir potenciais vizinhos via algoritmo Fuzzy/NetworkX.
- **RF03 (Deep Dive Audit):** Cruzar dados de endereço, CEP, e-mail e telefone entre dois registros para validar elos.
- **RF04 (Veredicto Inteligente):** Sugerir ação (Weld/Discard) com base em pontuação multidimensional.
- **RF05 (Persistência):** Salvar decisões em `negative_welds.json` ou `expert_welds.json`.

## 3. Requisitos Não-Funcionais
- **RNF01 (Interface):** Texto puro (Standard Output/Input). Sem dependências de UI externas.
- **RNF02 (Encoding):** Forçar UTF-8 para compatibilidade com terminais Windows.
- **RNF03 (Performance):** Resposta de busca em cache < 2 segundos.

## 4. Arquitetura de Dados
- **Input:** `dataset_ouro_v11_7.xlsx` (Lista mestre de grupos).
- **Audit Source:** `m0_cache_sa1010_983280b9.parquet` ou Tabela `SA1010` do Fabric.
- **Rules:** `engine/welders.py`.

## 5. Fluxo de Validação
1. O sistema recebe um CNPJ ou Nome.
2. Identifica o grupo atual.
3. Propõe uma lista numerada de potenciais soldas.
4. Ao selecionar, realiza o "Deep Dive".
5. Apresenta o veredicto sugerido.
6. Registra a decisão na base de conhecimento.

---
**Status:** Aprovado em Brainstorming (2026-05-11)
**Autor:** Antigravity (Engineered for Victor Bernardi)
