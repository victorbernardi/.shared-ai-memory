# Spec: Ecossistema Maestro de Grupos Econômicos (v10) - FINAL

## 1. Objetivo
Criar um ecossistema modular para unificação de identidade, auditoria de integridade e diagnóstico preditivo de grupos econômicos.

## 2. Camadas de Inteligência

### 2.1. Weld Engine (Motor de Soldagem)
- Lógica modularizada (C1-C8).
- **Confidence Scoring:** Atribuição de pesos para cada tipo de evidência.

### 2.2. Integrity Scanner (Auditoria de Soldas)
- **Detecção de Soldas Fracas:** Identificar e sinalizar unificações com score < 70% ou muito próximos ao threshold.
- **Inconsistências Lógicas:** Cruzamento de perfis incompatíveis.
- **Mega-Bridge Prevention:** Bloqueio de grupos > 5 integrantes sem validação.

### 2.3. Maestro Diagnostic (Investigador Preditivo)
- **Grafo de Linhagem:** Visualização completa do porquê de cada unificação.
- **Sugestão de Vizinhos (Predictive):** Analisar a base em tempo real para sugerir clientes que poderiam pertencer ao grupo, mas não atingiram o threshold automático (ex: Fuzzy Match 80% ou elo digital único).

## 3. Estrutura e Governança
- **Localização:** Todos os scripts em `/scripts/`.
- **Arquivos Core:**
    - `engine/welders.py`: As regras.
    - `engine/scanner.py`: A inteligência de auditoria.
    - `maestro_batch.py`: Processador massivo.
    - `maestro_diagnostic.py`: Interface interativa e preditiva.

## 4. Segurança (Soberania)
- Blacklist de Dealers (Inova) com **Soberania Zero**.
- Filtro de Chassis Bridge (Locadoras).

---
*Aprovado em: 2026-05-08*
*Assinado: Gemini CLI (Antigravity Engine)*
