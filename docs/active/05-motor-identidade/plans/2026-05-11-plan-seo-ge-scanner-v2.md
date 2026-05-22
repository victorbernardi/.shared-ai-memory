# SEO_GE Interactive Scanner — Implementation Plan v2

> **Status:** APROVADO para execução (pós-auditoria de 2026-05-11)
> **Spec de origem:** `docs/specs/2026-05-11-spec-seo-ge-scanner.md`
> **Correções aplicadas:** Auditoria `auditoria_plano_seo_ge_scanner.md`

**Goal:** Criar o `scripts/seo_ge_scanner.py` — ferramenta única e soberana para auditoria de grupos econômicos, operável tanto por humanos (modo interativo) quanto pelo Agente AI (modo autônomo `--auto`).

**Architecture:**
- `seo_ge_scanner.py` é um orquestrador puro: **não duplica lógica**.
- Importa `deep_dive_audit`, `record_decision`, `get_motor_status` de `seo_ge_audit_tool.py`.
- Importa `limpar_cnpj`, `limpar_telefone_c8`, `extrair_raiz_logradouro`, `BLACKLIST_DOMAINS_C8`, `normalizar_nome_base` de `engine/welders.py`.
- Utiliza `seo_ge_diagnostic.py` como referência para busca e listagem de sugestões.

**Tech Stack:** Python 3.x (stdlib apenas: `sys`, `os`, `json`, `re`, `argparse`), Pandas, rapidfuzz.

**Arquivos a criar/modificar:**
- CREATE: `scripts/seo_ge_scanner.py`
- MODIFY: `scripts/seo_ge_audit_tool.py` (refatorar `deep_dive_audit` para aceitar `mode` explícito)
- CREATE: `tests/test_seo_ge_scanner.py`

---

## Task 1: Refatorar `seo_ge_audit_tool.py` — Aceitar `mode` Explícito

**Arquivo:** `scripts/seo_ge_audit_tool.py`

**Problema a corrigir:** `deep_dive_audit()` ignora a preferência do usuário por `cache` ou `fabric`, lendo sempre o GEMINI.md implicitamente.

**Step 1:** Alterar a assinatura da função `deep_dive_audit()`:
```python
# ANTES:
def deep_dive_audit(cgc_a, cgc_b):
    status = get_motor_status()

# DEPOIS:
def deep_dive_audit(cgc_a, cgc_b, mode=None):
    # Se mode for fornecido explicitamente, ele prevalece sobre o GEMINI.md
    status = mode.upper() if mode else get_motor_status()
```

**Step 2:** Atualizar o argparse do `__main__` para passar `mode`:
```python
parser.add_argument("--mode", choices=['cache', 'fabric'], default=None)
# ...
deep_dive_audit(args.a, args.b, mode=args.mode)
```

**Step 3: Verificar sem quebrar comportamento anterior:**
```bash
python scripts/seo_ge_audit_tool.py --a 52987337604 --b 47871261649
# Esperado: "AUDIT: Iniciando Deep Dive (Modo: DEV)" — sem mudança de comportamento
python scripts/seo_ge_audit_tool.py --a 52987337604 --b 47871261649 --mode fabric
# Esperado: "AUDIT: Iniciando Deep Dive (Modo: FABRIC)"
```

---

## Task 2: Criar Testes Unitários Base (TDD — Escrever Antes do Scanner)

**Arquivo:** `tests/test_seo_ge_scanner.py`

**Regra TDD:** Os testes devem ser escritos ANTES do scanner. Eles irão falhar inicialmente (EXPECTED).

**Step 1:** Criar o arquivo de testes:
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import pytest

def test_verdict_discard_por_cep_divergente():
    """Rivelli: CEPs diferentes = DISCARD"""
    from seo_ge_scanner import calculate_verdict_score
    result = calculate_verdict_score(
        {'A1_CEP': '36319000', 'A1_EMAIL': '', 'A1_TEL': '', 'A1_END': 'FAZ DAS AROEIRAS'},
        {'A1_CEP': '35550000', 'A1_EMAIL': '', 'A1_TEL': '', 'A1_END': 'FAZ RENASCENCA'}
    )
    assert result['action'] == 'DISCARD'
    assert 'CEP' in result['reason']

def test_verdict_weld_por_email_corporativo():
    """Email corporativo igual = WELD"""
    from seo_ge_scanner import calculate_verdict_score
    result = calculate_verdict_score(
        {'A1_CEP': '36000000', 'A1_EMAIL': 'joao@empresa.com.br', 'A1_TEL': '', 'A1_END': 'RUA A'},
        {'A1_CEP': '37000000', 'A1_EMAIL': 'maria@empresa.com.br', 'A1_TEL': '', 'A1_END': 'RUA B'}
    )
    assert result['action'] == 'WELD'
    assert 'EMAIL' in result['reason']

def test_verdict_zona_cinza():
    """Apenas 1 elo positivo (telefone) = PENDING"""
    from seo_ge_scanner import calculate_verdict_score
    result = calculate_verdict_score(
        {'A1_CEP': '36000000', 'A1_EMAIL': '', 'A1_TEL': '3199999999', 'A1_END': 'RUA A'},
        {'A1_CEP': '37000000', 'A1_EMAIL': '', 'A1_TEL': '3199999999', 'A1_END': 'RUA B'}
    )
    assert result['action'] == 'PENDING'

def test_record_decision_nao_duplica():
    """Registrar o mesmo par 2x não deve criar entradas duplicadas"""
    import json, tempfile, os
    from seo_ge_scanner import record_decision_safe
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({'negative_welds': []}, f)
        path = f.name
    record_decision_safe('111', '222', 'DISCARD', 'Teste', path)
    record_decision_safe('111', '222', 'DISCARD', 'Teste', path)
    with open(path) as f:
        data = json.load(f)
    assert len(data['negative_welds']) == 1
    os.unlink(path)
```

**Step 2: Executar e confirmar falha (esperado):**
```bash
pytest tests/test_seo_ge_scanner.py -v
# Esperado: FAILED - ImportError: cannot import name 'calculate_verdict_score'
```

---

## Task 3: Implementar `calculate_verdict_score()` usando WeldEngine

**Arquivo:** `scripts/seo_ge_scanner.py` (início da implementação)

**Regra:** Reutilizar 100% das funções do `engine/welders.py`. Zero lógica duplicada.

**Step 1:** Criar o arquivo com boilerplate e a função de veredicto:
```python
import sys, os, json, re, argparse
import pandas as pd
from rapidfuzz import fuzz

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Importar de módulos existentes — NUNCA duplicar lógica
sys.path.insert(0, os.path.dirname(__file__))
from seo_ge_audit_tool import deep_dive_audit, record_decision, get_motor_status
from engine.welders import (
    limpar_cnpj, limpar_telefone_c8, extrair_raiz_logradouro,
    BLACKLIST_DOMAINS_C8, normalizar_nome_base
)

def _get_domain(email):
    if not email or '@' not in str(email): return None
    return str(email).split('@')[-1].strip().lower()

def calculate_verdict_score(row_a, row_b):
    """
    Calcula o veredicto de unificação usando a Matriz de Confiança Multidimensional.
    Retorna dict: {'action': 'WELD'|'DISCARD'|'PENDING', 'score': int, 'reason': str, 'elos': list}
    """
    score = 0
    elos_positivos = []
    elos_negativos = []

    # --- ELO C10: CEP (Exato) ---
    cep_a = re.sub(r'\D', '', str(row_a.get('A1_CEP', '') or ''))
    cep_b = re.sub(r'\D', '', str(row_b.get('A1_CEP', '') or ''))
    if cep_a and cep_b and len(cep_a) >= 8 and cep_a == cep_b:
        score += 3
        elos_positivos.append('C10:CEP_EXATO')
    elif cep_a and cep_b and cep_a != cep_b:
        score -= 2
        elos_negativos.append('C10:CEP_DIVERGENTE')

    # --- ELO GEO: Logradouro (Fuzzy) ---
    end_a = extrair_raiz_logradouro(row_a.get('A1_END', ''))
    end_b = extrair_raiz_logradouro(row_b.get('A1_END', ''))
    if end_a and end_b:
        sim = fuzz.token_sort_ratio(end_a, end_b)
        if sim >= 85:
            score += 2
            elos_positivos.append(f'GEO:LOGRADOURO_SIMILAR({sim}%)')
        elif sim < 40:
            score -= 1
            elos_negativos.append(f'GEO:LOGRADOURO_DIVERGENTE({sim}%)')

    # --- ELO C6/C7: Email Corporativo ---
    dom_a = _get_domain(row_a.get('A1_EMAIL', ''))
    dom_b = _get_domain(row_b.get('A1_EMAIL', ''))
    if dom_a and dom_b:
        if dom_a not in BLACKLIST_DOMAINS_C8 and dom_b not in BLACKLIST_DOMAINS_C8:
            if dom_a == dom_b:
                score += 4
                elos_positivos.append(f'C7:EMAIL_CORPORATIVO({dom_a})')
        elif dom_a == dom_b and dom_a in BLACKLIST_DOMAINS_C8:
            pass  # Email genérico — neutro

    # --- ELO C5: Telefone ---
    tel_a = limpar_telefone_c8(row_a.get('A1_TEL', ''))
    tel_b = limpar_telefone_c8(row_b.get('A1_TEL', ''))
    if tel_a and tel_b and tel_a == tel_b:
        score += 3
        elos_positivos.append(f'C5:TELEFONE({tel_a})')

    # --- DECISÃO FINAL ---
    if score >= 3 and elos_positivos:
        action = 'WELD'
        reason = 'Elos positivos: ' + ', '.join(elos_positivos)
    elif score <= -2 or (not elos_positivos and elos_negativos):
        action = 'DISCARD'
        reason = 'Sem elos. Divergências: ' + ', '.join(elos_negativos)
    else:
        action = 'PENDING'
        reason = f'Zona cinza (score={score}). Requer revisão humana.'

    return {'action': action, 'score': score, 'reason': reason,
            'elos_positivos': elos_positivos, 'elos_negativos': elos_negativos}
```

**Step 2: Rodar os testes:**
```bash
pytest tests/test_seo_ge_scanner.py::test_verdict_discard_por_cep_divergente -v
pytest tests/test_seo_ge_scanner.py::test_verdict_weld_por_email_corporativo -v
# Esperado: PASS
```

---

## Task 4: Implementar `record_decision_safe()` (Anti-Duplicata)

**Arquivo:** `scripts/seo_ge_scanner.py`

**Step 1:** Adicionar a função de persistência com proteção contra duplicatas:
```python
def record_decision_safe(cgc_a, cgc_b, action, reason, path=None):
    """Persiste decisão com proteção anti-duplicata via normalização de IDs."""
    key_map = {'WELD': 'expert_welds', 'DISCARD': 'negative_welds', 'PENDING': 'pending_welds'}
    key = key_map.get(action, 'negative_welds')

    if path is None:
        dir_knowledge = os.path.join(os.path.dirname(__file__), 'knowledge')
        fname = f"{action.lower()}_welds.json" if action != 'WELD' else 'expert_welds.json'
        path = os.path.join(dir_knowledge, fname if action != 'DISCARD' else 'negative_welds.json')

    data = {key: []}
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

    # Normalizar IDs para comparação
    id_a = limpar_cnpj(cgc_a)
    id_b = limpar_cnpj(cgc_b)

    # Verificar duplicata (bidirecional)
    ja_existe = any(
        (limpar_cnpj(e['id_a']) == id_a and limpar_cnpj(e['id_b']) == id_b) or
        (limpar_cnpj(e['id_a']) == id_b and limpar_cnpj(e['id_b']) == id_a)
        for e in data.get(key, [])
    )

    if ja_existe:
        print(f"INFO: Par ({id_a}, {id_b}) já registrado. Ignorando duplicata.")
        return

    data.setdefault(key, []).append({
        'id_a': cgc_a, 'id_b': cgc_b,
        'reason': reason,
        'date': pd.Timestamp.now().strftime('%Y-%m-%d')
    })

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"OK: Decisão '{action}' registrada. Motivo: {reason}")
```

**Step 2: Rodar teste anti-duplicata:**
```bash
pytest tests/test_seo_ge_scanner.py::test_record_decision_nao_duplica -v
# Esperado: PASS
```

---

## Task 5: Implementar Fluxo Interativo (Modo Humano)

**Arquivo:** `scripts/seo_ge_scanner.py`

**Step 1:** Implementar o fluxo linear com estados explícitos:
```
ESTADO 1: Busca
  ↓ (resultado encontrado)
ESTADO 2: Exibe grupo + integrantes
  ↓
ESTADO 3: Exibe lista numerada de sugestões (filtradas pelo negative_welds)
  ↓ (usuário digita número ou 0 para sair)
ESTADO 4: Deep Dive automático entre alvo e sugestão selecionada
  ↓
ESTADO 5: Exibe veredicto sugerido + campos comparativos
  ↓ (usuário digita W=Weld / D=Discard / P=Pending / S=Skip)
ESTADO 6: Persiste decisão via record_decision_safe()
  ↓
FIM
```

**Step 2:** Implementar `run_interactive(busca, mode)`:
```python
def run_interactive(busca, mode):
    """Fluxo interativo guiado para curadoria humana."""
    # [Importar lógica de busca do seo_ge_diagnostic.py]
    # Passos mapeados no diagrama acima
    ...
```

**Regras de Robustez:**
- Input inválido → `"ERR: Opção inválida. Digite um número da lista ou 0 para sair."` (loop sem crash)
- Busca sem resultado → `"ERR: Nenhum registro encontrado para '{busca}'."` (encerrar com código 0)
- Sem sugestões → `"INFO: Nenhuma sugestão preditiva para este grupo."` (encerrar com código 0)

---

## Task 6: Implementar Modo Autônomo (`--auto`)

**Arquivo:** `scripts/seo_ge_scanner.py`

**Threshold de Decisão (obrigatório para modo agente):**

| Condição | Ação Autônoma |
|----------|---------------|
| score >= 3 e elos_positivos não vazio | `WELD` → `expert_welds.json` |
| score <= -2 OU (elos_negativos e sem elos_positivos) | `DISCARD` → `negative_welds.json` |
| Qualquer outro caso | `PENDING` → `pending_welds.json` + log para revisão humana |

**Step 1:** Implementar `run_auto(cgc_a, cgc_b, mode)`:
```python
def run_auto(cgc_a, cgc_b, mode):
    """Executa auditoria completa e persiste decisão sem interação humana."""
    # 1. Buscar dados de ambos os registros (cache ou fabric)
    # 2. Calcular veredicto via calculate_verdict_score()
    # 3. Logar resultado completo (elos encontrados, score, decisão)
    # 4. Persistir via record_decision_safe()
    ...
```

---

## Task 7: Integrar `main()` e Argparse Final

**Arquivo:** `scripts/seo_ge_scanner.py`

**Step 1:** Implementar o `main()` orquestrador:
```python
def main():
    parser = argparse.ArgumentParser(description="SEO_GE Interactive Scanner v1.0")
    parser.add_argument("--busca", help="Termo de busca (Nome ou CNPJ) — Modo Interativo")
    parser.add_argument("--a", help="CGC do Cliente A — Modo Autônomo")
    parser.add_argument("--b", help="CGC do Cliente B — Modo Autônomo")
    parser.add_argument("--mode", choices=['cache', 'fabric'], default='cache',
                        help="Fonte de dados (default: cache)")
    parser.add_argument("--auto", action='store_true',
                        help="Modo Autônomo: executa sem interação e persiste decisão")
    args = parser.parse_args()

    if args.auto and args.a and args.b:
        run_auto(args.a, args.b, args.mode)
    elif args.busca:
        run_interactive(args.busca, args.mode)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

## Task 8: Verificação Final

**Step 1: Rodar toda a suite de testes:**
```bash
pytest tests/test_seo_ge_scanner.py -v
# Esperado: 4/4 PASS
```

**Step 2: Teste interativo real — Grupo RIVELLI:**
```bash
python scripts/seo_ge_scanner.py --busca "CARLOS FABIO NOGUEIRA RIVELLI" --mode cache
# Esperado: Exibir integrantes + sugestões (sem MARCIO DALVIO — já no negative_welds)
```

**Step 3: Teste autônomo real — Jose Ronaldo:**
```bash
python scripts/seo_ge_scanner.py --auto --a 88712184691 --b 76457940625 --mode cache
# Esperado: DISCARD com log "Par já registrado. Ignorando duplicata."
```

**Step 4: Verificar integridade dos arquivos de conhecimento:**
```bash
python -c "import json; d=json.load(open('scripts/knowledge/negative_welds.json')); print(f'{len(d[\"negative_welds\"])} registros no negative_welds')"
# Esperado: 3 registros (sem duplicatas)
```

---

## Resumo das Correções Aplicadas (vs Plano v1)

| Correção | Status |
|----------|--------|
| Importar de `seo_ge_audit_tool.py` (zero DRY) | APLICADO |
| Usar `WeldEngine` para veredicto | APLICADO |
| `deep_dive_audit()` aceita `mode` explícito | TASK 1 |
| Fluxo interativo com estados mapeados | TASK 5 |
| Threshold autônomo + `pending_welds.json` | TASK 6 |
| TDD com 4 testes unitários | TASK 2 |
| Anti-duplicata na persistência | TASK 4 |

---
*Plano v2 aprovado em auditoria interna — 2026-05-11*
*Aguardando execução pelo Gemini CLI.*
