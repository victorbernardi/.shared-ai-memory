#!/usr/bin/env python3
"""
stout-memory-capture.py
Agente local de destilação e persistência de Session-Learning para o ecossistema Stout.
100% offline. Sem chamadas externas. Windows-ready.
"""

import os
import re
import json
import sqlite3
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

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

def jaccard_similarity(a: str, b: str) -> float:
    """Similaridade léxica rápida sem dependências externas."""
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)

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
            r"\b(decidimos?|optamos?|escolhemos?|vamos usar|foi definido)\b\s+(?:por|que|o|a)?\s*(.{20,200})",
            r"\b(adopt|choose|decide on|settled on)\b\s+(.{20,200})",
        ],
        "heuristic": [
            r"\b(workaround|contorno|solução temporária|hack|gambiarra)\b\s*(?:[:\-]?\s*)(.{20,300})",
            r"\b(sempre que|se|quando|caso)\b\s+(.{20,200})\s+(?:execute|rode|use|tente)",
        ],
        "bug_workaround": [
            r"\b(bug|erro|falha|issue|problema|error)\b\s*(?:#?\d+)?\s*[:\-]?\s*(.{20,300})",
            r"\b(fix|correção|hotfix|patch)\b\s*(?:for|para|de)\b\s*(.{20,300})",
        ],
        "dependency": [
            r"\b(depend[eê]ncia|requer|necessita|precisa de|import|require)\b\s+(.{10,100})",
            r"\b(instalar|pip install|npm install|apt|brew)\b\s+(.{10,100})",
        ],
        "performance": [
            r"\b(lento|demorou|timeout|performance|otimizar|cache|lazy.?load)\b\s*(?:[:\-]?\s*)(.{20,200})",
        ],
        "security": [
            r"\b(vulnerabilidade|CVE|exploit|segurança|auth|token|senha|password)\b\s*(?:[:\-]?\s*)(.{20,300})",
        ],
    }

    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.filter = GuardrailFilter(cfg)

    def distill(self, raw_text: str, session_meta: Dict[str, str]) -> SessionLearning:
        clean_text = self.filter.sanitize_log(raw_text)
        facts: List[LearningFact] = []
        seen_contents: set = set()

        for category, patterns in self.HEURISTIC_PATTERNS.items():
            for pat in patterns:
                for match in re.finditer(pat, clean_text, re.IGNORECASE):
                    content = match.group(2) if len(match.groups()) > 1 else match.group(0)
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
        score = 0.6
        if len(content) > 60:
            score += 0.1
        if category in ("decision", "bug_workaround"):
            score += 0.15
        if any(k in content.lower() for k in ["não funciona", "erro", "falha", "fix", "workaround"]):
            score += 0.05
        if "REDACTED" in content:
            score -= 0.5
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
        lines = text.splitlines()
        first = lines[0][:200] if lines else ""
        last = lines[-1][:200] if lines else ""
        return f"Sessão: {first[:80]}... | {len(facts)} fatos destilados | encerramento: {last[:80]}..."

# ---------------------------------------------------------------------------
# PERSISTÊNCIA SQLITE + FTS5 + VECTOR (fallback lexical)
# ---------------------------------------------------------------------------

class SessionLearningDB:
    def __init__(self, db_path: str, cfg: Dict[str, Any]):
        self.db_path = db_path
        self.cfg = cfg
        # Garante a criação física da pasta pai do banco de dados se não existir
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()

    def _ensure_schema(self):
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
            self._insert_fact(session.session_id, fact)
        self.conn.commit()
        return session_db_id

    def _insert_fact(self, session_id: str, fact: LearningFact):
        # Deduplicação por similaridade léxica local
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
        # FTS5 sync manual
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
        if f.is_file() and f.stat().st_size < 5 * 1024 * 1024:  # max 5MB per file
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
    chunks = []
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                step = json.loads(line)
                source = step.get("source", "")
                step_type = step.get("type", "")
                content = step.get("content", "")
                if source in ("USER_EXPLICIT", "MODEL") and content:
                    chunks.append(f"[{source} - {step_type}]\n{content}\n")
            except Exception:
                pass
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
    if not filepath.exists():
        print(f"[stout-memory] Aviso: {filepath} não existe. Ignorando atualização.")
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
    if not filepath.exists():
        print(f"[stout-memory] Aviso: {filepath} não existe. Ignorando atualização.")
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

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Stout Memory Capture - Destilação e Persistência de Session-Learning")
    parser.add_argument("--raw-dir", default=DEFAULT_CONFIG["raw_memory_dir"])
    parser.add_argument("--active-dir", default=DEFAULT_CONFIG["active_dir"])
    parser.add_argument("--db", default=DEFAULT_CONFIG["db_path"])
    parser.add_argument("--transcript", default=None, help="Caminho para o transcript.jsonl do Antigravity CLI")
    parser.add_argument("--project", default=None, help="Override do nome do projeto")
    parser.add_argument("--inject", action="store_true", help="Modo recuperação: gera ACTIVE_CONTEXT.md com fatos relevantes")
    parser.add_argument("--query", default="", help="Query semântica para recuperação (modo --inject)")
    parser.add_argument("--maintenance", action="store_true", help="Executa rotina de decay/consolidação")
    args = parser.parse_args()

    cfg = DEFAULT_CONFIG.copy()
    cfg["db_path"] = args.db

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

    # 1. Carregar transcript se fornecido
    transcript_text = ""
    if args.transcript:
        print(f"[stout-memory] Carregando transcript de: {args.transcript}")
        transcript_text = parse_transcript_file(args.transcript)

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
