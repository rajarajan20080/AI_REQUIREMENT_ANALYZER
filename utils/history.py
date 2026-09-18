"""
history.py
==========

SQLite-backed persistence layer for storing, retrieving, and managing
SRS document analysis sessions and aggregate statistics.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any

import tempfile
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "history.db")


def _get_db_path() -> str:
    """
    Resolve database path reliably across local and serverless/Vercel environments.
    """
    # Check if running in Vercel or AWS Lambda serverless environment
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        tmp_db = os.path.join(tempfile.gettempdir(), "history.db")
        if not os.path.exists(tmp_db) and os.path.exists(DB_PATH):
            try:
                shutil.copyfile(DB_PATH, tmp_db)
            except Exception:
                pass
        return tmp_db

    try:
        os.makedirs(DB_DIR, exist_ok=True)
        return DB_PATH
    except (OSError, PermissionError):
        return os.path.join(tempfile.gettempdir(), "history.db")


def init_db() -> None:
    """Initialize the SQLite database schema if not already present."""
    db_path = _get_db_path()
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                filename TEXT NOT NULL,
                created_at TEXT NOT NULL,
                total_requirements INTEGER NOT NULL,
                functional_count INTEGER NOT NULL,
                non_functional_count INTEGER NOT NULL,
                ambiguous_count INTEGER NOT NULL,
                duplicate_pairs_count INTEGER NOT NULL,
                quality_score REAL NOT NULL,
                completeness_score REAL NOT NULL,
                overall_confidence REAL NOT NULL,
                complexity_level TEXT NOT NULL,
                complexity_score REAL NOT NULL,
                payload_json TEXT NOT NULL
            )
        """)
        conn.commit()


def save_analysis(
    title: str,
    filename: str,
    data: Dict[str, Any]
) -> int:
    """
    Save an analysis run into SQLite and return the new record ID.
    """
    init_db()
    db_path = _get_db_path()

    summary = data.get("summary", {})
    quality = data.get("quality", {})
    complexity = data.get("complexity", {})
    ambiguity = data.get("ambiguity", {})
    duplicates = data.get("duplicates", {})

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total_reqs = summary.get("total_requirements", len(data.get("classifications", [])))
    func_count = summary.get("functional_count", 0)
    nfr_count = summary.get("non_functional_count", 0)
    amb_count = ambiguity.get("ambiguous_count", 0)
    dup_count = len(duplicates.get("pairs", []))
    qual_score = quality.get("overall_score", 85.0)
    comp_score = summary.get("completeness_score", 85.0)
    conf_score = summary.get("overall_confidence", 90.0)
    comp_level = complexity.get("complexity_level", "Medium")
    comp_score_val = complexity.get("complexity_score", 50.0)

    payload_json = json.dumps(data)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analyses (
                title, filename, created_at, total_requirements,
                functional_count, non_functional_count, ambiguous_count,
                duplicate_pairs_count, quality_score, completeness_score,
                overall_confidence, complexity_level, complexity_score,
                payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, filename, now_str, total_reqs,
            func_count, nfr_count, amb_count,
            dup_count, qual_score, comp_score,
            conf_score, comp_level, comp_score_val,
            payload_json
        ))
        conn.commit()
        return cursor.lastrowid


def get_all_analyses() -> List[Dict[str, Any]]:
    """
    Retrieve list of all saved analyses (summary metadata only, without full JSON).
    """
    init_db()
    db_path = _get_db_path()

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, filename, created_at, total_requirements,
                   functional_count, non_functional_count, ambiguous_count,
                   duplicate_pairs_count, quality_score, completeness_score,
                   overall_confidence, complexity_level, complexity_score
            FROM analyses
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_analysis_by_id(analysis_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve full analysis record by ID, including decoded payload JSON.
    """
    init_db()
    db_path = _get_db_path()

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM analyses WHERE id = ?
        """, (analysis_id,))
        row = cursor.fetchone()
        if not row:
            return None

        result = dict(row)
        result["payload"] = json.loads(result["payload_json"])
        result["payload"]["id"] = result["id"]
        result["payload"]["history_id"] = result["id"]
        return result


def delete_analysis(analysis_id: int) -> bool:
    """
    Delete an analysis from SQLite history.
    """
    init_db()
    db_path = _get_db_path()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_history_stats() -> Dict[str, Any]:
    """
    Calculate aggregate metrics across all historical analyses for the global dashboard.
    """
    init_db()
    db_path = _get_db_path()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*),
                   COALESCE(SUM(total_requirements), 0),
                   COALESCE(SUM(functional_count), 0),
                   COALESCE(SUM(non_functional_count), 0),
                   COALESCE(SUM(ambiguous_count), 0),
                   COALESCE(SUM(duplicate_pairs_count), 0),
                   COALESCE(AVG(quality_score), 0.0),
                   COALESCE(AVG(completeness_score), 0.0),
                   COALESCE(AVG(overall_confidence), 0.0)
            FROM analyses
        """)
        row = cursor.fetchone()

        # Complexity distribution
        cursor.execute("""
            SELECT complexity_level, COUNT(*)
            FROM analyses
            GROUP BY complexity_level
        """)
        comp_rows = cursor.fetchall()
        complexity_dist = {level: count for level, count in comp_rows}

        total_analyses = row[0]
        return {
            "total_analyses": total_analyses,
            "total_requirements": row[1],
            "functional_count": row[2],
            "non_functional_count": row[3],
            "ambiguous_count": row[4],
            "duplicate_pairs_count": row[5],
            "avg_quality_score": round(row[6], 1),
            "avg_completeness_score": round(row[7], 1),
            "avg_confidence": round(row[8], 1),
            "complexity_distribution": complexity_dist
        }
