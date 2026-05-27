#!/usr/bin/env python3
"""
stout-memory-capture.py
Agente local de destilação e persistência de Session-Learning para o ecossistema Stout.
100% offline. Sem chamadas externas. Windows-ready.
"""

import os
import sys
import io
import re
import json
import sqlite3
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

# ---------------------------------------------------------------------------
# CONSTANTES GLOBAIS DE GOVERNANÇA
# ---------------------------------------------------------------------------
GLOBAL_DB_PATH = r"C:\Users\victor.bernardi\.shared-ai-memory\session_learning_golden.db"
PROJETOS_ROOT = r"C:\Projetos"

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO E GUARDRAILS
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "db_path": ".stout/session_learning.db",
    "raw_memory_dir": ".stout/session_memory/raw",
    "active_dir": ".stout/active",
    "min_confidence": 0.7,
    "max_facts_per_session": 20,
    "max_injected_facts": 5,
    "similarity_threshold": 0.85,
    "secret_patterns": [
        r"(sk-[a-zA-Z0-9]{20,})",
        r"(ghp_[a-zA-Z0-9]{36})",
        r"(AKIA[0-9A-Z]{16})",
        r"(private\.key|\.env)",
        r"([A-Za-z0-9+/]{40,}={0,2})",
    ],
    "noise_patterns": [
        r"^\s*DEBUG:",
        r"HTTP\s+\d+\s+OK",
        r"^\s*git\s+status",
        r"^\s*ls\s+-",
        r"^\s*pwd\s*$",
    ],
    "embedding_mode": "lexical",  # "lexical" ou "sentence_transformers"
}

# ---------------------------------------------------------------------------
# UTILITÁRIOS
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]

def redact_secrets(text: str, patterns: List[str]) -> str:
    for pat in patterns:
        text = re.sub(pat, lambda m: f"[REDACTED-{sha256(m.group(0))}]", text)
    return text

def is_noise(line: str, patterns: List[str]) -> bool:
    return any(re.search(p, line) for p in patterns)

def _log_failure(message: str):
    try:
        log_path = Path("notes/failure-log.md")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"- [{timestamp}] {message}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_line)
    except Exception:
        pass

def _is_code_snippet(text: str) -> bool:
    """Detecta se o texto é um fragmento de código, não linguagem natural."""
    score = 0
    # f-string ou interpolação com chaves: {var}, {obj["key"]}, {obj.key}, {func()}
    if re.search(r'\{[\w.\'\"\[\]\(\)]+\}', text):
        score += 3
    # Acesso a dict: ["key"] ou ['key']
    if re.search(r'\[[\'"]\w+[\'"]\]', text):
        score += 3
    # f"..." ou f'...'
    if re.search(r'\bf["\']', text):
        score += 3
    # Imports
    if re.search(r'\b(import|require)\b', text):
        score += 3
    # Package managers
    if re.search(r'\b(pip|npm|yarn|brew|apt|apt-get|conda)\s+(install|run|test|build|start)\b', text):
        score += 3
    # Paths absolutos (Windows/Unix)
    if re.search(r'[A-Z]:\\[^\s]{10,}|/[a-z]+/[a-z]+/[^\s]', text):
        score += 3
    # Regex patterns escapados
    if re.search(r'[\\]{2}[dDwWsS]', text):
        score += 3
    if re.search(r'\(\?[imsxLux]*[:=]', text):
        score += 3
    # SQL keywords
    if re.search(r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE TABLE|ALTER TABLE|DROP TABLE)\b', text, re.IGNORECASE):
        score += 3
    # Operadores de atribuição
    if re.search(r'(\+=|-=|\*=|/=|==|!=|>=|<=|\|\||&&)', text):
        score += 2
    # Chamada de método: .algo(...)
    if re.search(r'\.\w+\(', text):
        score += 2
    # Lista/dict de strings: "x", "y" ou 'x', 'y'
    if re.search(r'[\'"]\w+[\'"]\s*,\s*[\'"]\w+[\'"]', text):
        score += 3
    # Colchetes ou parenteses com string literal
    if re.search(r'[\[\(]\s*[\'"]\w+[\'"]', text):
        score += 2
    # Backtick markdown (inline code)
    if re.search(r'`[^`]{3,}`', text):
        score += 2
    # Termina com "), "), "} - corte de código
    if text.rstrip().endswith(('"}', "')", '")', '"]', '\")')):
        score += 2
    # Termina com : indicando linha de log/erro truncada
    if re.search(r':\s*$', text) and len(text) > 60:
        score += 1
    # Permission errors/logs
    if re.search(r'Permission (denied|prompt)', text):
        score += 2
    # Logs de sistema/IDE
    if re.search(r'in step execution:', text):
        score += 2

    return score >= 3

def shingle_hash(text: str, k: int = 3) -> set:
    """Gera shingles de palavras para dedup aproximada."""
    words = re.findall(r"\b\w+\b", text.lower())
    return set(tuple(words[i:i+k]) for i in range(max(1, len(words)-k+1)))

def shingle_similarity(a: str, b: str, k: int = 3) -> float:
    sa, sb = shingle_hash(a, k), shingle_hash(b, k)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

# ---------------------------------------------------------------------------
# MODELO DE DADOS
# ---------------------------------------------------------------------------

@dataclass
class LearningFact:
    id: str
    category: str
    content: str
    confidence: float
    severity: str = "medium"
    tags: List[str] = None
    related_files: List[str] = None
    embedding_id: str = ""
    occurrence_count: int = 1
    decay_score: float = 1.0
    status: str = "active"

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.related_files is None:
            self.related_files = []

@dataclass
class SessionLearning:
    session_id: str
    timestamp: str
    project: str
    branch: str
    commit_hash: str
    cdd_rule_triggered: str
    facts: List[LearningFact]
    context_summary: str
    agent_version: str

# ---------------------------------------------------------------------------
# FILTROS
# ---------------------------------------------------------------------------

class GuardrailFilter:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg

    def sanitize_log(self, text: str) -> str:
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            if is_noise(line, self.cfg["noise_patterns"]):
                continue
            cleaned.append(redact_secrets(line, self.cfg["secret_patterns"]))
        return "\n".join(cleaned)

    def validate_fact(self, fact: LearningFact) -> bool:
        if fact.confidence < self.cfg["min_confidence"]:
            return False
        if "[REDACTED-" in fact.content:
            return False
        if len(fact.content.strip()) < 20:
            return False
        if _is_code_snippet(fact.content):
            return False
        return True

# ---------------------------------------------------------------------------
# DESTILADOR SEMÂNTICO (offline)
# ---------------------------------------------------------------------------

class OfflineDistiller:
    """
    Destilação semântica 100% local usando heurísticas + templates.
    Não requer GPU nem API externa.
    """

    HEURISTIC_PATTERNS = {
        "decision": [
            r"(?:whitelist|blacklist)\s+\w+\s*(?:substitui|substituir|replace)",
            r"(?:adotar|adota|usar|utilizar)\s+\w+\s+(?:como|para|em vez de)",
            r"(?:remover|removido|excluir|excluído)\s+\w+(?:\s+(?:do|da|dos|das))?",
            r"(?:confirmado|confirmada|validado|validada)\s+(?:que\s+)?(.{20,200})",
            r"(?:filtro|filtragem|classificar)\s+(?:por\s+)?\w+\s*(?:agora|passa a|mantém)",
            r"(?:escolha|decisão|definido|definida)\s*(?::|é|foi|que)\s*(.{20,200})",
            r"(?:fonte|referência)\s+(?:da verdade|oficial|canônica)\s*(?::|é|passa a ser)\s*(.{20,200})",
        ],
        "heuristic": [
            r"(?:sempre que|quando|se|caso)\s+(.{20,200})\s+(?:execute|rode|use|tente|buscar|procurar|verificar)",
            r"(?:workaround|contorno|solução\s+temporária|hack|gambiarra)\s*(?:[:\-]?\s*)(.{20,300})",
            r"(?:padrão|convenção|regra|prática)\s*(?::|é|adotada|definida)\s*(.{20,200})",
        ],
        "bug_workaround": [
            r"(?:corrigir|corrigido|resolvido|solucionado|fix|patch)\s+(?:o\s+)?(?:bug|erro|problema|issue)\s*(?:#?\d+)?\s*(?:de|com|em|:)?\s*(.{20,300})",
            r"(?:causa[\-\s]raiz|causa raiz)\s*(?::|confirmada|é)\s*(.{20,200})",
            r"(?:não\s+contém|ausente|faltando|sem\s+dados)\s+(?:no|na|em)\s+(.{20,200})",
        ],
        "dependency": [
            r"(?:depend[eê]ncia|requer|necessita|precisa de)\s+(?:de\s+)?(.{10,100})",
            r"(?:integrar|conectar|alimentar|consumir)\s+(?:com|do|da|o|a)\s+(.{10,100})",
        ],
        "data_quality": [
            r"(?:delta|divergência|gap|diferença)\s+(?:de\s+)?(?:R\$|%|[+-]?\d+[\.,]?\d*[BMk%]?)",
            r"(?:formato|encoding|varchar|float|tipo)\s+(?:incompatível|divergente|diferente)",
            r"(?:snapshot|replicação|replicar|reprocessar)\s+(?:incompleto|desatualizado|faltando)",
            r"(?:f_vendas_hist|vw_VENDAS|SD2010|SF2010|SD1010|SA1010)\s+(?:não|sem|ausente|faltando)",
        ],
    }

    DOMAIN_TERMS = [
        "fabric", "protheus", "bi", "pipeline", "motor", "sql", "snapshot",
        "sd2010", "sf2010", "sd1010", "sa1010", "vw_vendas", "f_vendas_hist",
        "cbit", "cbpc", "eprc", "leic", "jdpc", "whitelist", "blacklist",
        "cod_grupo", "filial", "descricao_cc", "cpf", "cnpj", "zfill",
        "transform", "extract", "merge", "segmentacao", "faturamento",
        "delta", "divergencia", "nf", "nota fiscal", "imposto", "liquido",
    ]

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.filter = GuardrailFilter(cfg)

    def _domain_boost(self, content: str) -> float:
        lowered = content.lower()
        hits = sum(1 for t in self.DOMAIN_TERMS if t in lowered)
        return min(0.25, hits * 0.03)

    def _extract_sentence_boundary(self, text: str, start_pos: int, max_len: int = 300) -> str:
        """Extrai até a próxima fronteira de sentença, não no meio da frase."""
        end_pos = min(start_pos + max_len, len(text))
        boundary_pattern = r'[.!?]\s+|\n\n|\n(?:##|###|\|)'
        matches = list(re.finditer(boundary_pattern, text[start_pos:end_pos]))
        if matches:
            cut = start_pos + matches[-1].end()
            return text[start_pos:cut].strip()
        return text[start_pos:end_pos].strip()

    def distill(self, raw_text: str, session_meta: Dict[str, str]) -> SessionLearning:
        clean_text = self.filter.sanitize_log(raw_text)
        facts: List[LearningFact] = []
        seen_contents: set = set()

        for category, patterns in self.HEURISTIC_PATTERNS.items():
            for pat in patterns:
                for match in re.finditer(pat, clean_text, re.IGNORECASE):
                    if len(match.groups()) > 1 and match.group(2):
                        content = match.group(2).strip()
                    else:
                        start = max(0, match.start() - 40)
                        raw = clean_text[start:min(len(clean_text), match.end() + 300)]
                        content = self._extract_sentence_boundary(raw, 0, 340)
                    content = content.strip()
                    if len(content) < 20 or content.lower() in seen_contents:
                        continue
                    seen_contents.add(content.lower())

                    confidence = self._score_confidence(content, category, clean_text)
                    if confidence < self.cfg["min_confidence"]:
                        continue

                    fact = LearningFact(
                        id=f"fact-{sha256(content)}",
                        category=category,
                        content=content[:2000],
                        confidence=round(confidence, 3),
                        severity=self._infer_severity(category, content),
                        tags=self._extract_tags(content, category, session_meta),
                        related_files=self._extract_files(clean_text),
                        embedding_id=f"emb-{sha256(content)}",
                        occurrence_count=1,
                        decay_score=1.0,
                        status="active",
                    )
                    if self.filter.validate_fact(fact):
                        facts.append(fact)

        # Resumo semântico via extração de primeira e última ação + contagem
        summary = self._generate_summary(clean_text, facts)

        return SessionLearning(
            session_id=session_meta.get("session_id", "unknown"),
            timestamp=now_iso(),
            project=session_meta.get("project", "unknown"),
            branch=session_meta.get("branch", "main"),
            commit_hash=session_meta.get("commit_hash", "0000000"),
            cdd_rule_triggered=session_meta.get("cdd_rule_triggered", "none"),
            facts=facts[: self.cfg["max_facts_per_session"]],
            context_summary=summary,
            agent_version=session_meta.get("agent_version", "stout-unknown"),
        )

    def _score_confidence(self, content: str, category: str, context: str) -> float:
        score = 0.5  # baseline reduzido (era 0.6)
        if len(content) > 80:
            score += 0.1
        if category in ("decision", "data_quality"):
            score += 0.15
        if category == "bug_workaround":
            score += 0.05
        if "REDACTED" in content:
            score -= 0.5
        if _is_code_snippet(content):
            score -= 0.5
        if len(content.split()) < 5:
            score -= 0.2
        score += self._domain_boost(content)
        return min(score, 0.98)

    def _infer_severity(self, category: str, content: str) -> str:
        if category == "security":
            return "critical"
        if category == "bug_workaround" and any(k in content.lower() for k in ["crash", "quebra", "fatal"]):
            return "high"
        if category == "decision":
            return "medium"
        return "low"

    def _extract_tags(self, content: str, category: str, meta: Dict[str, str]) -> List[str]:
        tags = [category, meta.get("project", "global")]
        tech_keywords = re.findall(r"\b(python|javascript|typescript|sql|api|cli|mcp|llm|sqlite|yaml|json|docker|git)\b", content.lower())
        tags.extend(tech_keywords)
        return list(set(tags))

    def _extract_files(self, text: str) -> List[str]:
        files = re.findall(r"[\w\-]+\.(py|js|ts|yaml|yml|json|md|sql|sh|bat|ps1)", text)
        return list(set(files))

    def _generate_summary(self, text: str, facts: List[LearningFact]) -> str:
        decisions = [f for f in facts if f.category == "decision"]
        bugs = [f for f in facts if f.category == "bug_workaround"]
        dq = [f for f in facts if f.category == "data_quality"]
        parts = []
        if decisions:
            parts.append(f"Decisão principal: {decisions[0].content[:120]}")
        if bugs:
            parts.append(f"Bug: {bugs[0].content[:100]}")
        if dq:
            parts.append(f"Qualidade de dados: {len(dq)} observações")
        return " | ".join(parts) if parts else f"{len(facts)} fatos capturados"

# ---------------------------------------------------------------------------
# PERSISTÊNCIA SQLITE + FTS5 + VECTOR (fallback lexical)
# ---------------------------------------------------------------------------

class SessionLearningDB:
    def __init__(self, db_path: str, cfg: Dict[str, Any]):
        self.db_path = db_path
        self.cfg = cfg
        # Garante a criação física da pasta pai do banco de dados se não existir
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
        self.conn.execute("BEGIN TRANSACTION")
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS session_learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                project TEXT,
                branch TEXT,
                commit_hash TEXT,
                cdd_rule_triggered TEXT,
                context_summary TEXT,
                agent_version TEXT,
                raw_json TEXT NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_id TEXT UNIQUE NOT NULL,
                session_id TEXT NOT NULL,
                category TEXT,
                content TEXT NOT NULL,
                confidence REAL,
                severity TEXT,
                tags TEXT,
                related_files TEXT,
                embedding_id TEXT,
                occurrence_count INTEGER DEFAULT 1,
                decay_score REAL DEFAULT 1.0,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                last_seen TEXT,
                replaces_id TEXT,
                FOREIGN KEY(session_id) REFERENCES session_learnings(session_id)
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS project_links (
                project_path TEXT PRIMARY KEY,
                golden_db_path TEXT NOT NULL,
                link_type TEXT CHECK(link_type IN ('shared','forked','isolated'))
            )
        """)
        # FTS5 para busca léxica rápida
        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS facts_fts USING fts5(
                content, tags, session_id,
                content='learning_facts',
                content_rowid='id'
            )
        """)
        # Índices
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_session ON learning_facts(session_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_status ON learning_facts(status)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_category ON learning_facts(category)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_facts_embedding ON learning_facts(embedding_id)")
        self.conn.commit()

    def insert(self, session: SessionLearning) -> int:
        # 1. Inserção local usando transação segura e imediata
        session_db_id = 0
        try:
            self.conn.execute("BEGIN IMMEDIATE TRANSACTION")
            raw_json = json.dumps(session.__dict__, default=lambda o: asdict(o) if isinstance(o, LearningFact) else str(o), ensure_ascii=False)
            cur = self.conn.execute(
                """INSERT INTO session_learnings
                   (session_id, timestamp, project, branch, commit_hash, cdd_rule_triggered, context_summary, agent_version, raw_json)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (session.session_id, session.timestamp, session.project, session.branch,
                 session.commit_hash, session.cdd_rule_triggered, session.context_summary,
                 session.agent_version, raw_json)
            )
            session_db_id = cur.lastrowid

            for fact in session.facts:
                self._insert_fact_tx(session.session_id, fact)
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            _log_failure(f"Erro transacional local SQLite: {e}")
            raise

        # 2. Persistência Dupla Central (Golden DB central SQLite)
        # Tenta conectar com timeout transacional de 30s
        global_db = str(GLOBAL_DB_PATH)
        if global_db and global_db != self.db_path:
            try:
                # Inicializa ou conecta ao Golden DB global
                g_db = SessionLearningDB(global_db, self.cfg)
                g_conn = g_db.conn
                g_conn.execute("PRAGMA busy_timeout = 30000") # 30 segundos timeout
                g_conn.execute("BEGIN IMMEDIATE TRANSACTION")
                
                # Insere de forma idempotente a sessão no central
                g_conn.execute(
                    """INSERT OR IGNORE INTO session_learnings
                       (session_id, timestamp, project, branch, commit_hash, cdd_rule_triggered, context_summary, agent_version, raw_json)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (session.session_id, session.timestamp, session.project, session.branch,
                     session.commit_hash, session.cdd_rule_triggered, session.context_summary,
                     session.agent_version, raw_json)
                )
                
                for fact in session.facts:
                    # Inserção de fatos no central com verificação de shingle global
                    dup = g_db._find_duplicate(fact.content)
                    if dup:
                        g_conn.execute(
                            "UPDATE learning_facts SET occurrence_count = occurrence_count + 1, last_seen = ?, decay_score = 1.0 WHERE fact_id = ?",
                            (now_iso(), dup["fact_id"])
                        )
                    else:
                        g_conn.execute(
                            """INSERT OR IGNORE INTO learning_facts
                               (fact_id, session_id, category, content, confidence, severity, tags, related_files,
                                embedding_id, occurrence_count, decay_score, status, created_at, last_seen, replaces_id)
                               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                            (fact.id, session.session_id, fact.category, fact.content, fact.confidence, fact.severity,
                             json.dumps(fact.tags, ensure_ascii=False),
                             json.dumps(fact.related_files, ensure_ascii=False),
                             fact.embedding_id, fact.occurrence_count, fact.decay_score, fact.status,
                             now_iso(), now_iso(), None)
                        )
                        g_conn.execute(
                            "INSERT OR IGNORE INTO facts_fts(content, tags, session_id) VALUES (?,?,?)",
                            (fact.content, " ".join(fact.tags), session.session_id)
                        )
                g_conn.commit()
                g_db.close()
                print(f"[stout-memory] Persistência Central: Sessão {session.session_id} espelhada com sucesso.")
            except Exception as e:
                _log_failure(f"Falha ao espelhar no banco de dados central: {e}")

        # 3. Escrita Dupla Central de Markdowns na Wiki central
        global_gov_dir = Path(GLOBAL_DB_PATH).parent / "docs" / "governance"
        try:
            global_gov_dir.mkdir(parents=True, exist_ok=True)
            global_known = global_gov_dir / "known_issues_golden.md"
            global_backlog = global_gov_dir / "evolution_backlog_golden.md"
            
            update_known_issues(session.facts, global_known)
            update_evolution_backlog(session.facts, global_backlog, session.session_id)
        except Exception as e:
            _log_failure(f"Erro ao atualizar markdowns globais na central: {e}")

        return session_db_id

    def _insert_fact(self, session_id: str, fact: LearningFact):
        """Método de compatibilidade."""
        self._insert_fact_tx(session_id, fact)

    def _insert_fact_tx(self, session_id: str, fact: LearningFact):
        """Auxiliar de inserção de fatos dentro de uma transação ativa."""
        dup = self._find_duplicate(fact.content)
        if dup:
            self.conn.execute(
                "UPDATE learning_facts SET occurrence_count = occurrence_count + 1, last_seen = ?, decay_score = 1.0 WHERE fact_id = ?",
                (now_iso(), dup["fact_id"])
            )
            return

        self.conn.execute(
            """INSERT INTO learning_facts
               (fact_id, session_id, category, content, confidence, severity, tags, related_files,
                embedding_id, occurrence_count, decay_score, status, created_at, last_seen, replaces_id)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (fact.id, session_id, fact.category, fact.content, fact.confidence, fact.severity,
             json.dumps(fact.tags, ensure_ascii=False),
             json.dumps(fact.related_files, ensure_ascii=False),
             fact.embedding_id, fact.occurrence_count, fact.decay_score, fact.status,
             now_iso(), now_iso(), None)
        )
        self.conn.execute(
            "INSERT INTO facts_fts(content, tags, session_id) VALUES (?,?,?)",
            (fact.content, " ".join(fact.tags), session_id)
        )

    def _find_duplicate(self, content: str) -> Optional[sqlite3.Row]:
        """Busca duplicata por similaridade de shingles."""
        threshold = self.cfg["similarity_threshold"]
        rows = self.conn.execute(
            "SELECT fact_id, content FROM learning_facts WHERE status = 'active'"
        ).fetchall()
        for row in rows:
            sim = shingle_similarity(content, row["content"])
            if sim >= threshold:
                return row
        return None

    def search_semantic(self, query: str, project: Optional[str] = None, top_k: int = 5) -> List[Dict]:
        """
        Recuperação híbrida: FTS5 léxico + ranking por decay/recency.
        Se sentence_transformers estiver disponível, usa cosine similarity.
        """
        # 1. Busca FTS5
        fts_results = self.conn.execute(
            "SELECT rowid, * FROM facts_fts WHERE facts_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, top_k * 3)
        ).fetchall()

        fact_ids = [r["rowid"] for r in fts_results]
        if not fact_ids:
            return []

        placeholders = ",".join("?" * len(fact_ids))
        sql = f"""SELECT * FROM learning_facts
                    WHERE id IN ({placeholders}) AND status = 'active'"""
        params = fact_ids
        if project:
            sql += " AND session_id IN (SELECT session_id FROM session_learnings WHERE project = ?)"
            params = fact_ids + [project]

        rows = self.conn.execute(sql, params).fetchall()

        # 2. Reranking por decay_score * confidence * recency
        scored = []
        for row in rows:
            base_score = row["decay_score"] * row["confidence"]
            # Penalidade de recência simples (dias desde last_seen)
            try:
                last = datetime.fromisoformat(row["last_seen"])
                days_old = (datetime.now(timezone.utc) - last).days
                time_penalty = max(0.3, 1.0 - (days_old * 0.05))
            except Exception:
                time_penalty = 1.0
            scored.append((base_score * time_penalty, dict(row)))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [s[1] for s in scored[:top_k]]

    def consolidate_decay(self, session_threshold: int = 10):
        """
        Rotina de manutenção: aplica decay em memórias não acessadas,
        consolida memórias com occurrence_count > 3 em sumários.
        """
        # Decay
        self.conn.execute(
            "UPDATE learning_facts SET decay_score = decay_score * 0.9 WHERE status = 'active'"
        )
        # Arquivar se decay < 0.2
        self.conn.execute(
            "UPDATE learning_facts SET status = 'archived' WHERE status = 'active' AND decay_score < 0.2"
        )
        self.conn.commit()

    def close(self):
        self.conn.close()

# ---------------------------------------------------------------------------
# ORQUESTRAÇÃO: CAPTURA DO SISTEMA DE ARQUIVOS
# ---------------------------------------------------------------------------

def load_raw_memory(raw_dir: str) -> str:
    p = Path(raw_dir)
    if not p.exists():
        return ""
    chunks = []
    for f in sorted(p.rglob("*")):
        if f.is_file() and f.stat().st_size < 5 * 1024 * 1024:
            if f.suffix == ".jsonl":
                chunks.append(parse_transcript_file(str(f)))
            elif f.suffix == ".md":
                try:
                    chunks.append(f"--- {f.name} ---\n{f.read_text(encoding='utf-8', errors='ignore')}\n")
                except Exception:
                    pass
    return "\n".join(chunks)

def load_active_context(active_dir: str) -> Dict[str, str]:
    meta = {}
    p = Path(active_dir)
    if p.exists():
        for f in p.glob("*.meta"):
            try:
                meta.update(json.loads(f.read_text(encoding='utf-8')))
            except Exception:
                pass
    return meta

def discover_project_meta() -> Dict[str, str]:
    """Extrai metadados do ambiente Git/CWD."""
    import subprocess
    meta = {
        "project": Path.cwd().name,
        "branch": "main",
        "commit_hash": "0000000",
        "session_id": f"sess-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}",
        "agent_version": "stout-capture-v1",
        "cdd_rule_triggered": os.environ.get("STOUT_CDD_RULE", "none"),
    }
    try:
        meta["branch"] = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    except Exception:
        pass
    try:
        meta["commit_hash"] = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        pass
    return meta

# ---------------------------------------------------------------------------
# GERADOR DE RELATÓRIOS E ATUALIZADOR DE GOVERNANÇA
# ---------------------------------------------------------------------------

def parse_transcript_file(transcript_path: str) -> str:
    path = Path(transcript_path)
    if not path.exists():
        return ""
    
    # 1. Se for Markdown (Claude Desktop)
    if path.suffix.lower() == ".md":
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            _log_failure(f"Erro ao ler markdown do Claude Desktop {path}: {e}")
            return ""
            
    chunks = []
    
    # 2. Se for JSON/JSONL
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    step = json.loads(line)
                    
                    # Caso A: Antigravity CLI (JSONL)
                    if "source" in step:
                        source = step.get("source", "")
                        step_type = step.get("type", "")
                        content = step.get("content", "")
                        if source in ("USER_EXPLICIT", "MODEL") and content:
                            chunks.append(f"[{source} - {step_type}]\n{content}\n")
                            
                    # Caso B: CommandCode (JSONL com role e content array de blocos ou string)
                    elif "role" in step:
                        role = step.get("role", "").upper()
                        content_raw = step.get("content")
                        
                        if isinstance(content_raw, list):
                            block_texts = []
                            for block in content_raw:
                                if isinstance(block, dict) and block.get("type") == "text":
                                    block_texts.append(block.get("text", ""))
                            content_str = "".join(block_texts)
                        elif isinstance(content_raw, str):
                            content_str = content_raw
                        else:
                            content_str = str(content_raw)
                            
                        if role in ("USER", "ASSISTANT") and content_str.strip():
                            chunks.append(f"[{role}]\n{content_str}\n")
                except Exception:
                    pass
    except Exception as e:
        _log_failure(f"Erro ao processar JSONL {path}: {e}")
        
    return "\n".join(chunks)

def generate_session_report(session: SessionLearning, output_path: Path):
    lines = [
        "# 🧠 Aprendizados da Sessão – CDD Session-Learning",
        f"_Gerado de forma autônoma em {session.timestamp}_\n",
        "## 📋 Sumário Executivo",
        session.context_summary or "Nenhum sumário disponível para esta sessão.",
        "\n## 💡 Fatos Destilados",
        "| Categoria | Descrição / Aprendizado | Confiança | Severidade | Tags |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]
    for fact in session.facts:
        tags_str = ", ".join(fact.tags)
        content_sanitized = fact.content.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{fact.category}` | {content_sanitized} | {fact.confidence} | `{fact.severity}` | `{tags_str}` |")
    
    lines.append("\n---\n")
    lines.append("> [!NOTE]")
    lines.append(f"> Sessão ID: `{session.session_id}` | Projeto: `{session.project}` | Branch: `{session.branch}`")
    
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[stout-memory] Relatório de sessão gerado em {output_path}")

def update_known_issues(facts: List[LearningFact], filepath: Path):
    bug_facts = [f for f in facts if f.category == "bug_workaround" or f.severity in ("critical", "high")]
    if not bug_facts:
        return
        
    # Auto-Healing: Cria o arquivo com os cabeçalhos corretos se não existir ou estiver vazio
    if not filepath.exists() or filepath.stat().st_size == 0:
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            initial_content = (
                "# Known Issues\n\n"
                "| Bug ID | Categoria | Descrição | Ocorrências | Workaround | Resolução | Status |\n"
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            )
            filepath.write_text(initial_content, encoding="utf-8")
        except Exception as e:
            _log_failure(f"Erro ao inicializar known_issues.md no auto-healing: {e}")
            return
    
    content = filepath.read_text(encoding="utf-8")
    
    bug_facts = [f for f in facts if f.category == "bug_workaround" or f.severity in ("critical", "high")]
    if not bug_facts:
        return
    
    matches = re.findall(r"(\| \*\*BUG-\d+\*\* \|.*?)(?=\n)", content)
    
    existing_bugs = []
    max_bug_num = 0
    
    for row in matches:
        parts = [p.strip() for p in row.split("|")]
        if len(parts) >= 8:
            bug_id = parts[1].replace("**", "")
            category = parts[2]
            description = parts[3]
            try:
                occurrences = int(parts[4])
            except ValueError:
                occurrences = 1
            workaround = parts[5]
            resolution = parts[6]
            status = parts[7]
            
            existing_bugs.append({
                "id": bug_id,
                "category": category,
                "description": description,
                "occurrences": occurrences,
                "workaround": workaround,
                "resolution": resolution,
                "status": status,
                "row_text": row
            })
            
            num_match = re.search(r"BUG-(\d+)", bug_id)
            if num_match:
                max_bug_num = max(max_bug_num, int(num_match.group(1)))

    updated_rows = []
    new_bugs = []
    
    for fact in bug_facts:
        found = False
        fact_desc = fact.content.replace("\n", " ").strip()
        
        for bug in existing_bugs:
            sim = shingle_similarity(fact_desc, bug["description"])
            if sim >= 0.85:
                bug["occurrences"] += 1
                found = True
                print(f"[stout-memory] Bug existente detectado ({bug['id']}). Incrementando contagem para {bug['occurrences']}.")
                break
        
        if not found:
            max_bug_num += 1
            bug_id = f"BUG-{max_bug_num:03d}"
            
            workaround = "N/A"
            if "workaround" in fact_desc.lower() or "contorno" in fact_desc.lower():
                workaround = fact_desc
            elif len(fact.related_files) > 0:
                workaround = f"Verificar arquivos relacionados: {', '.join(fact.related_files)}"
                
            new_bug = {
                "id": bug_id,
                "category": f"`{fact.category}`",
                "description": fact_desc[:150],
                "occurrences": 1,
                "workaround": workaround[:150],
                "resolution": "Pendente de análise",
                "status": "`Pendente`"
            }
            new_bugs.append(new_bug)
            print(f"[stout-memory] Novo bug detectado! Registrando como {bug_id}.")

    for bug in existing_bugs:
        row_text = f"| **{bug['id']}** | {bug['category']} | {bug['description']} | {bug['occurrences']} | {bug['workaround']} | {bug['resolution']} | {bug['status']} |"
        updated_rows.append(row_text)
        
    for bug in new_bugs:
        row_text = f"| **{bug['id']}** | {bug['category']} | {bug['description']} | {bug['occurrences']} | {bug['workaround']} | {bug['resolution']} | {bug['status']} |"
        updated_rows.append(row_text)
        
    header_idx = content.find("| Bug ID | Categoria |")
    if header_idx != -1:
        table_start = content.find("\n", header_idx) + 1
        divider_end = content.find("\n", table_start) + 1
        
        last_row_end = divider_end
        for row in matches:
            idx = content.find(row)
            if idx != -1:
                last_row_end = max(last_row_end, idx + len(row))
        
        if last_row_end < len(content):
            if content[last_row_end] == '\n':
                last_row_end += 1
            elif content[last_row_end:last_row_end+2] == '\r\n':
                last_row_end += 2
            
        table_content = "\n".join(updated_rows) + "\n"
        new_content = content[:divider_end] + table_content + content[last_row_end:]
        filepath.write_text(new_content, encoding="utf-8")
        print(f"[stout-memory] {filepath} atualizado com sucesso!")
    else:
        print("[stout-memory] Erro: Tabela não encontrada em known_issues.md.")

def update_evolution_backlog(facts: List[LearningFact], filepath: Path, session_id: str):
    sug_facts = [f for f in facts if f.category in ("decision", "performance", "dependency") or any(t in f.tags for t in ("refatoração", "melhoria", "infraestrutura"))]
    if not sug_facts:
        return
        
    # Auto-Healing: Cria o arquivo com os cabeçalhos corretos se não existir ou estiver vazio
    if not filepath.exists() or filepath.stat().st_size == 0:
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            initial_content = (
                "# Evolution Backlog\n\n"
                "| ID | Data | Origem (Sessão) | Proposta | Impacto | Prioridade | Status |\n"
                "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            )
            filepath.write_text(initial_content, encoding="utf-8")
        except Exception as e:
            _log_failure(f"Erro ao inicializar evolution_backlog.md no auto-healing: {e}")
            return
            
    content = filepath.read_text(encoding="utf-8")
    
    sug_facts = [f for f in facts if f.category in ("decision", "performance", "dependency") or any(t in f.tags for t in ("refatoração", "melhoria", "infraestrutura"))]
    if not sug_facts:
        return
        
    matches = re.findall(r"(\| \*\*SUG-\d+\*\* \|.*?)(?=\n)", content)
    
    existing_sugs = []
    max_sug_num = 0
    
    for row in matches:
        parts = [p.strip() for p in row.split("|")]
        if len(parts) >= 8:
            sug_id = parts[1].replace("**", "")
            date = parts[2]
            origin = parts[3]
            proposal = parts[4]
            impact = parts[5]
            priority = parts[6]
            status = parts[7]
            
            existing_sugs.append({
                "id": sug_id,
                "date": date,
                "origin": origin,
                "proposal": proposal,
                "impact": impact,
                "priority": priority,
                "status": status,
                "row_text": row
            })
            
            num_match = re.search(r"SUG-(\d+)", sug_id)
            if num_match:
                max_sug_num = max(max_sug_num, int(num_match.group(1)))

    updated_rows = []
    new_sugs = []
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    for fact in sug_facts:
        fact_desc = fact.content.replace("\n", " ").strip()
        found = False
        
        for sug in existing_sugs:
            sim = shingle_similarity(fact_desc, sug["proposal"])
            if sim >= 0.85:
                found = True
                print(f"[stout-memory] Sugestão existente detectado ({sug['id']}). Ignorando duplicação.")
                break
                
        if not found:
            max_sug_num += 1
            sug_id = f"SUG-{max_sug_num:03d}"
            
            impact = "Otimização local e clareza de código"
            if fact.category == "performance":
                impact = "Melhoria de performance e eficiência"
            elif fact.category == "dependency":
                impact = "Alinhamento e modularidade de dependências"
                
            priority = "`Média`"
            if fact.severity == "critical":
                priority = "`Crítica`"
            elif fact.severity == "high":
                priority = "`Alta`"
                
            new_sug = {
                "id": sug_id,
                "date": today,
                "origin": f"`{session_id[:8]}`",
                "proposal": fact_desc[:150],
                "impact": impact,
                "priority": priority,
                "status": "`Planejado`"
            }
            new_sugs.append(new_sug)
            print(f"[stout-memory] Nova sugestão detectada! Registrando como {sug_id}.")

    for sug in existing_sugs:
        row_text = f"| **{sug['id']}** | {sug['date']} | {sug['origin']} | {sug['proposal']} | {sug['impact']} | {sug['priority']} | {sug['status']} |"
        updated_rows.append(row_text)
        
    for sug in new_sugs:
        row_text = f"| **{sug['id']}** | {sug['date']} | {sug['origin']} | {sug['proposal']} | {sug['impact']} | {sug['priority']} | {sug['status']} |"
        updated_rows.append(row_text)

    header_idx = content.find("| ID | Data | Origem (Sessão) |")
    if header_idx != -1:
        table_start = content.find("\n", header_idx) + 1
        divider_end = content.find("\n", table_start) + 1
        
        last_row_end = divider_end
        for row in matches:
            idx = content.find(row)
            if idx != -1:
                last_row_end = max(last_row_end, idx + len(row))
                
        if last_row_end < len(content):
            if content[last_row_end] == '\n':
                last_row_end += 1
            elif content[last_row_end:last_row_end+2] == '\r\n':
                last_row_end += 2
            
        table_content = "\n".join(updated_rows) + "\n"
        new_content = content[:divider_end] + table_content + content[last_row_end:]
        filepath.write_text(new_content, encoding="utf-8")
        print(f"[stout-memory] {filepath} atualizado com sucesso!")
    else:
        print("[stout-memory] Erro: Tabela não encontrada em evolution_backlog.md.")

def persist_session_id(active_dir: str, conv_id: str, client_type: str = "antigravity"):
    """Grava o Conversation ID e o tipo de cliente de forma persistente e local no projeto."""
    try:
        p = Path(active_dir)
        p.mkdir(parents=True, exist_ok=True)
        meta_file = p / "session.meta"
        
        meta_data = {}
        if meta_file.exists():
            try:
                meta_data = json.loads(meta_file.read_text(encoding='utf-8', errors='ignore'))
            except Exception:
                pass
                
        meta_data["conversation_id"] = conv_id
        meta_data["client_type"] = client_type
        meta_data["updated_at"] = now_iso()
        
        meta_file.write_text(json.dumps(meta_data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[stout-memory] ID [{conv_id}] ({client_type}) registrado localmente em {meta_file}")
    except Exception as e:
        _log_failure(f"Erro ao persistir ID localmente: {e}")

def _copy_to_sandbox_bridge(src: Path, dest: Path):
    """Copia o arquivo do host para a ponte de sandbox local de forma segura."""
    try:
        src = Path(src)
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text(encoding="utf-8", errors="ignore")
        dest.write_text(content, encoding="utf-8")
        print(f"[stout-memory] Ponte de Sandbox: Copiado transcript para cache local em {dest}")
    except Exception as e:
        _log_failure(f"Erro ao copiar para ponte de sandbox de {src} para {dest}: {e}")

def autodetect_transcript(active_dir: str, specified_conv_id: Optional[str] = None) -> Optional[str]:
    """
    Tenta localizar automaticamente o transcript (Antigravity, CommandCode ou Claude Desktop).
    Hierarquia de resolução:
      1. Prioridade local (Ponte de Sandbox): .stout/session_memory/raw/transcript.jsonl
      2. Argumento explicitado pelo CLI (--conversation-id)
      3. Variáveis de ambiente de sessão (COMMANDCODE_SESSION_ID, GEMINI_CONVERSATION_ID, CONVERSATION_ID)
      4. Persistência local do projeto (.stout/active/session.meta)
      5. Triagem por recência de arquivos na home do host (mtime <= 10 min)
    """
    import os
    import time
    from pathlib import Path
    
    local_raw_path = Path(".stout/session_memory/raw/transcript.jsonl")
    local_md_path = Path(".stout/session_memory/raw/transcript.md")
    
    # 1. Ponte de Sandbox (Prioridade local)
    # Se rodando em sandbox sem bypass, se o arquivo já existir localmente, retorna ele imediatamente.
    if local_raw_path.exists() and local_raw_path.stat().st_size > 0:
        print(f"[stout-memory] Ponte de Sandbox: Carregando transcript local prioritário de {local_raw_path}")
        return str(local_raw_path)
    if local_md_path.exists() and local_md_path.stat().st_size > 0:
        print(f"[stout-memory] Ponte de Sandbox: Carregando transcript markdown local de {local_md_path}")
        return str(local_md_path)

    # 2. Resolução do CWD Slug para CommandCode / Claude Desktop
    try:
        cwd_str = str(Path.cwd()).lower()
        project_slug = re.sub(r'[^a-z0-9]', '-', cwd_str)
        project_slug = re.sub(r'-+', '-', project_slug).strip('-')
    except Exception:
        project_slug = "unknown-project"

    # 3. Resolução da Home do Host
    home_dir = Path.home()

    # 4. Tentar ler de variável de ambiente customizada se injetada
    env_path = os.environ.get("ANTIGRAVITY_TRANSCRIPT_PATH")
    if env_path and Path(env_path).exists():
        print(f"[stout-memory] Transcript detectado via env var ANTIGRAVITY_TRANSCRIPT_PATH: {env_path}")
        # Copia para cache local para ponte de sandbox futura
        if Path(env_path).suffix.lower() == ".md":
            _copy_to_sandbox_bridge(env_path, local_md_path)
            return str(local_md_path)
        else:
            _copy_to_sandbox_bridge(env_path, local_raw_path)
            return str(local_raw_path)

    # 5. Tentar variáveis de ambiente de ID de sessão dos múltiplos clientes
    # A. CommandCode
    cc_session_id = os.environ.get("COMMANDCODE_SESSION_ID")
    if cc_session_id:
        cc_path = home_dir / ".commandcode" / "projects" / project_slug / f"{cc_session_id}.jsonl"
        if cc_path.exists():
            print(f"[stout-memory] Transcript CommandCode detectado via env COMMANDCODE_SESSION_ID: {cc_path}")
            persist_session_id(active_dir, cc_session_id, "commandcode")
            _copy_to_sandbox_bridge(cc_path, local_raw_path)
            return str(local_raw_path)

    # B. Antigravity CLI (Gemini)
    conv_id = specified_conv_id or os.environ.get("GEMINI_CONVERSATION_ID") or os.environ.get("CONVERSATION_ID")
    if conv_id:
        gemini_path = home_dir / ".gemini" / "antigravity-cli" / "brain" / conv_id / ".system_generated" / "logs" / "transcript.jsonl"
        if gemini_path.exists():
            print(f"[stout-memory] Transcript Antigravity detectado via ID [{conv_id}]: {gemini_path}")
            persist_session_id(active_dir, conv_id, "antigravity")
            _copy_to_sandbox_bridge(gemini_path, local_raw_path)
            return str(local_raw_path)

    # 6. Tentar ler da persistência local (.stout/active/session.meta)
    meta_file = Path(active_dir) / "session.meta"
    if meta_file.exists():
        try:
            meta_data = json.loads(meta_file.read_text(encoding='utf-8', errors='ignore'))
            saved_id = meta_data.get("conversation_id")
            client_type = meta_data.get("client_type", "antigravity")
            if saved_id:
                if client_type == "commandcode":
                    cc_path = home_dir / ".commandcode" / "projects" / project_slug / f"{saved_id}.jsonl"
                    if cc_path.exists():
                        print(f"[stout-memory] Transcript CommandCode recuperado do meta local: {cc_path}")
                        _copy_to_sandbox_bridge(cc_path, local_raw_path)
                        return str(local_raw_path)
                elif client_type == "claudedesktop":
                    # Claude Desktop usa arquivos .md
                    local_md_file = Path(".stout/session_memory/raw/transcript.md")
                    if local_md_file.exists():
                        return str(local_md_file)
                else:
                    gemini_path = home_dir / ".gemini" / "antigravity-cli" / "brain" / saved_id / ".system_generated" / "logs" / "transcript.jsonl"
                    if gemini_path.exists():
                        print(f"[stout-memory] Transcript Antigravity recuperado do meta local: {gemini_path}")
                        _copy_to_sandbox_bridge(gemini_path, local_raw_path)
                        return str(local_raw_path)
        except Exception as e:
            _log_failure(f"Erro ao ler session.meta: {e}")

    # 7. Triagem por recência de arquivos na home do host (mtime nos últimos 10 minutos = 600 segundos)
    # Procuramos nos 3 clientes principais
    active_threshold = 10 * 60
    candidates = []

    # A. Varredura CommandCode
    cc_project_dir = home_dir / ".commandcode" / "projects" / project_slug
    if cc_project_dir.exists():
        for f in cc_project_dir.glob("*.jsonl"):
            age = time.time() - f.stat().st_mtime
            if age < active_threshold:
                candidates.append((age, f, "commandcode"))

    # B. Varredura Antigravity CLI
    gemini_brain = home_dir / ".gemini" / "antigravity-cli" / "brain"
    if gemini_brain.exists():
        for f in gemini_brain.rglob("transcript.jsonl"):
            age = time.time() - f.stat().st_mtime
            if age < active_threshold:
                candidates.append((age, f, "antigravity"))

    # C. Varredura Claude Desktop (conceito Markdown)
    claude_project_slug = project_slug.replace("-", "--")
    claude_mem_dir = home_dir / ".claude" / "projects" / claude_project_slug / "memory"
    if claude_mem_dir.exists():
        for f in claude_mem_dir.glob("*.md"):
            age = time.time() - f.stat().st_mtime
            if age < active_threshold:
                candidates.append((age, f, "claudedesktop"))

    if candidates:
        # Ordena por recência (mais recente primeiro)
        candidates.sort(key=lambda x: x[0])
        best_age, best_file, best_client = candidates[0]
        
        # Alerta de concorrência se houver múltiplos candidatos recentes
        if len(candidates) > 1:
            print("[stout-memory] ⚠️ MÚLTIPLAS SESSÕES ATIVAS DETECTADAS NOS ÚLTIMOS 10 MINUTOS!")
            for idx, (age, f, client) in enumerate(candidates):
                marker = "⭐ (Selecionado)" if idx == 0 else "   "
                print(f"  {marker} [{client.upper()}] {f.name} (Modificado há {int(age)}s)")
                
        print(f"[stout-memory] Autodetectado transcript mais recente de [{best_client.upper()}]: {best_file}")
        
        # Copia para cache de sandbox
        if best_client == "claudedesktop":
            _copy_to_sandbox_bridge(best_file, local_md_path)
            persist_session_id(active_dir, best_file.stem, best_client)
            return str(local_md_path)
        else:
            _copy_to_sandbox_bridge(best_file, local_raw_path)
            persist_session_id(active_dir, best_file.stem, best_client)
            return str(local_raw_path)

    return None

def run_retrofit(projetos_root: str, global_db_path: str):
    """
    Executa a consolidação retroativa (retrofit) unificada de uma única vez.
    Busca recursivamente por bases SQLite e markdowns avulsos históricos,
    processa e deduplica registros com shingle similarity >= 85%.
    """
    print(f"[stout-retrofit] Iniciando varredura em {projetos_root}...")
    root_path = Path(projetos_root)
    if not root_path.exists():
        print(f"[stout-retrofit] Erro: {projetos_root} não existe.")
        return

    # Garante inicialização da base global
    cfg = DEFAULT_CONFIG.copy()
    cfg["db_path"] = global_db_path
    global_db = SessionLearningDB(global_db_path, cfg)
    
    sqlite_paths = []
    markdown_paths = []
    
    # 1. Varredura recursiva de bancos SQLite locais e markdowns avulsos
    for item in root_path.rglob("*"):
        try:
            if item.is_file():
                # Bancos locais em .stout/
                if item.name == "session_learning.db" and ".stout" in item.parts:
                    if item.resolve() != Path(global_db_path).resolve():
                        sqlite_paths.append(item)
                # Markdowns avulsos contendo 'aprendizado' ou 'learning' no nome
                elif item.suffix.lower() == ".md":
                    name_lower = item.name.lower()
                    if "aprendizado" in name_lower or "learning" in name_lower:
                        if ".stout" not in item.parts and "node_modules" not in item.parts:
                            markdown_paths.append(item)
        except Exception:
            pass

    print(f"[stout-retrofit] Encontrados {len(sqlite_paths)} bancos locais SQLite e {len(markdown_paths)} markdowns avulsos.")

    # 2. Ingestão de bancos SQLite locais
    facts_imported = 0
    for sq_path in sqlite_paths:
        try:
            print(f"[stout-retrofit] Ingerindo banco: {sq_path}")
            local_conn = sqlite3.connect(str(sq_path), isolation_level=None)
            local_conn.row_factory = sqlite3.Row
            
            # Lê learnings
            learnings = local_conn.execute("SELECT * FROM session_learnings").fetchall()
            for learn in learnings:
                global_db.conn.execute(
                    """INSERT OR IGNORE INTO session_learnings
                       (session_id, timestamp, project, branch, commit_hash, cdd_rule_triggered, context_summary, agent_version, raw_json)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (learn["session_id"], learn["timestamp"], learn["project"], learn["branch"],
                     learn["commit_hash"], learn["cdd_rule_triggered"], learn["context_summary"],
                     learn["agent_version"], learn["raw_json"])
                )
                
            # Lê fatos
            facts = local_conn.execute("SELECT * FROM learning_facts WHERE status = 'active'").fetchall()
            for f in facts:
                fact_obj = LearningFact(
                    id=f["fact_id"],
                    category=f["category"],
                    content=f["content"],
                    confidence=f["confidence"],
                    severity=f["severity"],
                    tags=json.loads(f["tags"]) if f["tags"] else [],
                    related_files=json.loads(f["related_files"]) if f["related_files"] else [],
                    embedding_id=f["embedding_id"],
                    occurrence_count=f["occurrence_count"],
                    decay_score=f["decay_score"],
                    status=f["status"]
                )
                global_db._insert_fact(f["session_id"], fact_obj)
                facts_imported += 1
                
            local_conn.close()
            global_db.conn.commit()
        except Exception as e:
            _log_failure(f"Erro ao processar retrofit do banco {sq_path}: {e}")

    # 3. Ingestão e processamento lexical offline de markdowns avulsos
    distiller = OfflineDistiller(cfg)
    for md_path in markdown_paths:
        try:
            print(f"[stout-retrofit] Processando markdown avulso: {md_path}")
            md_text = md_path.read_text(encoding="utf-8", errors="ignore")
            
            pseudo_meta = {
                "session_id": f"retro-{sha256(str(md_path))[:8]}",
                "project": md_path.parent.name,
                "branch": "main",
                "commit_hash": "retrofit",
                "cdd_rule_triggered": "retrofit-ingest",
                "agent_version": "stout-retrofit-v1"
            }
            session = distiller.distill(md_text, pseudo_meta)
            global_db.insert(session)
            facts_imported += len(session.facts)
        except Exception as e:
            _log_failure(f"Erro ao processar retrofit do markdown {md_path}: {e}")

    try:
        global_db.conn.commit()
    except Exception:
        pass

    print(f"[stout-retrofit] Retrofit completo. {facts_imported} fatos ingeridos/processados de forma unificada.")
    global_db.close()

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _archive_raw_files(raw_dir: str):
    """Move arquivos processados de raw/ para processed/ com timestamp, evitando reprocessamento."""
    p = Path(raw_dir)
    processed = p.parent / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    for f in p.iterdir():
        if f.is_file():
            dest = processed / f"{ts}_{f.name}"
            f.rename(dest)


def main():
    parser = argparse.ArgumentParser(description="Stout Memory Capture - Destilação e Persistência de Session-Learning")
    parser.add_argument("--raw-dir", default=DEFAULT_CONFIG["raw_memory_dir"])
    parser.add_argument("--active-dir", default=DEFAULT_CONFIG["active_dir"])
    parser.add_argument("--db", default=DEFAULT_CONFIG["db_path"])
    parser.add_argument("--transcript", default=None, help="Caminho para o transcript.jsonl do Antigravity CLI")
    parser.add_argument("--conversation-id", "--conv-id", default=None, help="UUID da sessão ativa do Antigravity CLI")
    parser.add_argument("--project", default=None, help="Override do nome do projeto")
    parser.add_argument("--inject", action="store_true", help="Modo recuperação: gera ACTIVE_CONTEXT.md com fatos relevantes")
    parser.add_argument("--query", default="", help="Query semântica para recuperação (modo --inject)")
    parser.add_argument("--maintenance", action="store_true", help="Executa rotina de decay/consolidação")
    parser.add_argument("--retrofit", action="store_true", help="Executa a migração retroativa de bases SQLite e markdowns no host")
    args = parser.parse_args()

    cfg = DEFAULT_CONFIG.copy()
    cfg["db_path"] = args.db

    # Se for retrofit, executa run_retrofit antes de inicializar o banco padrão (que seria o local)
    if args.retrofit:
        run_retrofit(PROJETOS_ROOT, GLOBAL_DB_PATH)
        print("[stout-memory] Retrofit concluído com sucesso.")
        return

    db = SessionLearningDB(args.db, cfg)

    if args.maintenance:
        db.consolidate_decay()
        print("[stout-memory] Manutenção de decay/consolidação concluída.")
        db.close()
        return

    if args.inject:
        project = args.project or discover_project_meta()["project"]
        results = db.search_semantic(args.query or project, project=project, top_k=cfg["max_injected_facts"])
        out_path = Path(args.active_dir) / "ACTIVE_CONTEXT.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# ACTIVE CONTEXT – Aprendizados Injetados\n", f"_Projeto: {project}_\n", "---\n"]
        for r in results:
            lines.append(f"## [{r['category'].upper()}] {r['content'][:100]}...\n")
            lines.append(f"- **Confiança:** {r['confidence']} | **Decay:** {r['decay_score']:.2f}\n")
            lines.append(f"- **Tags:** {r['tags']}\n")
            lines.append(f"- **Arquivos:** {r['related_files']}\n")
            lines.append("\n")
        out_path.write_text("\n".join(lines), encoding='utf-8')
        print(f"[stout-memory] {len(results)} fatos injetados em {out_path}")
        db.close()
        return

    # MODO CAPTURA (default)
    meta = discover_project_meta()
    if args.project:
        meta["project"] = args.project

    # 1. Carregar transcript se fornecido ou autodetectado
    transcript_text = ""
    transcript_path = args.transcript
    
    if not transcript_path:
        transcript_path = autodetect_transcript(args.active_dir, args.conversation_id)
        
    if transcript_path:
        print(f"[stout-memory] Carregando transcript de: {transcript_path}")
        transcript_text = parse_transcript_file(transcript_path)

    raw_text = load_raw_memory(args.raw_dir)
    
    # Combinar transcript com raw memory
    combined_text = ""
    if transcript_text:
        combined_text += f"\n=== TRANSCRIPT DA SESSÃO ===\n{transcript_text}\n"
    if raw_text:
        combined_text += f"\n=== MEMÓRIA FÍSICA RAW ===\n{raw_text}\n"
        
    active_meta = load_active_context(args.active_dir)
    meta.update(active_meta)

    if not combined_text.strip():
        print("[stout-memory] Nenhuma raw memory ou transcript encontrado. Abortando.")
        db.close()
        return

    distiller = OfflineDistiller(cfg)
    session = distiller.distill(combined_text, meta)

    db.insert(session)
    print(f"[stout-memory] Sessão {session.session_id} persistida com {len(session.facts)} fatos.")
    _archive_raw_files(cfg["raw_memory_dir"])
    
    # Gerar os artefatos de governança e relatórios automáticos
    project_root = Path.cwd()
    
    # 1. aprendizados_sessao.md na raiz do projeto
    report_path = project_root / "aprendizados_sessao.md"
    generate_session_report(session, report_path)
    
    # 2. docs/governance/known_issues.md
    known_issues_path = project_root / "docs" / "governance" / "known_issues.md"
    update_known_issues(session.facts, known_issues_path)
    
    # 3. docs/governance/evolution_backlog.md
    evolution_backlog_path = project_root / "docs" / "governance" / "evolution_backlog.md"
    update_evolution_backlog(session.facts, evolution_backlog_path, session.session_id)
    
    db.close()

if __name__ == "__main__":
    main()
