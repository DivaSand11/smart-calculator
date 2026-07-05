"""
history_dao.py
Data Access Object for calculation history — encapsulates all SQL so the
UI and engine layers never write raw queries directly.
"""

from typing import List, Optional
try:
    from db.database import get_connection
except ImportError:  # allows running this file standalone from db/
    from database import get_connection


def add_entry(expression: str, result: str, method_used: Optional[str] = None) -> int:
    """Insert a new history record. Returns the new row id."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO history (expression, result, method_used) VALUES (?, ?, ?)",
            (expression, result, method_used),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_all(limit: int = 50) -> List[dict]:
    """Return the most recent `limit` history entries, newest first."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def search(keyword: str) -> List[dict]:
    """Return history entries whose expression or method matches a keyword."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """SELECT * FROM history
               WHERE expression LIKE ? OR method_used LIKE ?
               ORDER BY id DESC""",
            (f"%{keyword}%", f"%{keyword}%"),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def delete_entry(entry_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
        conn.commit()
    finally:
        conn.close()


def clear_all() -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM history")
        conn.commit()
    finally:
        conn.close()


def export_csv(filepath: str) -> None:
    """Export full history to a CSV file."""
    import csv
    rows = get_all(limit=100000)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "expression", "result", "method_used", "timestamp"])
        for row in rows:
            writer.writerow([row["id"], row["expression"], row["result"],
                              row["method_used"], row["timestamp"]])
