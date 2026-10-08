"""Lambe arse ki yaaddasht: alag alag chats me bhi yaad rehta hai."""
import re
import time
from typing import Dict, List

from . import db


def add(text: str) -> int:
    text = (text or "").strip()[:500]
    if not text:
        return 0
    for row in db.fetchall("SELECT id, text FROM memories ORDER BY id DESC LIMIT 300"):
        if row["text"].strip().lower() == text.lower():
            return row["id"]
    return db.execute("INSERT INTO memories(text, created) VALUES(?, ?)", (text, time.time()))


def list_all(limit: int = 300) -> List[Dict]:
    return db.fetchall("SELECT id, text, created FROM memories ORDER BY id DESC LIMIT ?", (limit,))


def delete(memory_id: int) -> None:
    db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))


def search(query: str, limit: int = 8) -> List[Dict]:
    rows = list_all(500)
    words = [w for w in re.findall(r"\w+", (query or "").lower()) if len(w) > 2]
    if not words:
        return rows[:limit]
    scored = []
    for r in rows:
        low = r["text"].lower()
        score = sum(1 for w in words if w in low)
        if score:
            scored.append((score, r["id"], r))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    return [r for _, _, r in scored[:limit]]


def prompt_block(max_items: int = 40, max_chars: int = 1800) -> str:
    lines: List[str] = []
    used = 0
    for r in list_all(max_items):
        line = f"- (#{r['id']}) {r['text']}"
        if used + len(line) > max_chars:
            break
        lines.append(line)
        used += len(line)
    return "\n".join(lines)
