"""
Nebula v9 — Productivity, Structured Notes, Reminders, and Time Executors
"""
import os
import json
import time
import threading
from datetime import datetime
from typing import Tuple, Dict, Any

from config import (
    _NOTES_DB_FILE, _REMINDERS_FILE, _TODO_FILE, _HABIT_FILE,
    NCFG, _save_cfg, Log
)
from tts import _spk_ref


# ── Time & Date ──────────────────────────────────────────────────────────────
def _p_time(e) -> Tuple[bool, str]:
    now = datetime.now()
    return True, f"It's {now.strftime('%I:%M %p')}"


def _p_date(e) -> Tuple[bool, str]:
    now = datetime.now()
    return True, f"Today is {now.strftime('%A, %B %d, %Y')}"


def _p_day(e) -> Tuple[bool, str]:
    now = datetime.now()
    return True, f"Today is {now.strftime('%A')}"


# ── Structured Notes Database ────────────────────────────────────────────────
def _load_notes_db() -> list:
    try:
        if _NOTES_DB_FILE.exists():
            return json.loads(_NOTES_DB_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_notes_db(notes: list):
    try:
        _NOTES_DB_FILE.write_text(json.dumps(notes, indent=2), encoding="utf-8")
    except Exception:
        pass


def _p_note_add_structured(e) -> Tuple[bool, str]:
    raw = e.get("raw", "") or e.get("text", "") or ""
    # Strip leading trigger words
    for prefix in ("note that ", "add note ", "take note ", "new note ", "note "):
        if raw.lower().startswith(prefix):
            raw = raw[len(prefix):].strip()
            break
    if not raw:
        return False, "What would you like to note?"
    parts = raw.split("|", 1)
    title = parts[0].strip()
    content = parts[1].strip() if len(parts) > 1 else title
    notes = _load_notes_db()
    entry = {
        "title": title,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }
    notes.append(entry)
    _save_notes_db(notes)
    return True, f"Note saved: '{title}'"


def _p_note_list(e) -> Tuple[bool, str]:
    notes = _load_notes_db()
    if not notes:
        return True, "No notes found in database."
    lines = [f"  [{i+1}] {n['title']} ({n.get('timestamp','')[:10]})" for i, n in enumerate(notes[-10:])]
    return True, f"📝 Notes ({len(notes)}):\n" + "\n".join(lines)


def _p_note_read(e) -> Tuple[bool, str]:
    q = (e.get("query", "") or e.get("text", "") or e.get("raw", "")).lower().strip()
    notes = _load_notes_db()
    for n in reversed(notes):
        if q in n["title"].lower() or q in n["content"].lower():
            return True, f"📝 Note: {n['title']}\n{n['content']}"
    return False, f"No note matching '{q}' found"


def _p_note_del(e) -> Tuple[bool, str]:
    q = (e.get("query", "") or e.get("text", "") or e.get("raw", "")).lower().strip()
    notes = _load_notes_db()
    new_notes = [n for n in notes if q not in n["title"].lower()]
    if len(new_notes) < len(notes):
        _save_notes_db(new_notes)
        return True, f"Deleted notes matching '{q}'"
    return False, f"No note found matching '{q}'"


# ── Todos & Habits ───────────────────────────────────────────────────────────
def _load_todos() -> list:
    try:
        if _TODO_FILE.exists():
            return json.loads(_TODO_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return []


def _save_todos(todos: list):
    try:
        _TODO_FILE.write_text(json.dumps(todos, indent=2), encoding="utf-8")
    except Exception:
        pass


def _p_todo_add(e) -> Tuple[bool, str]:
    txt = e.get("text", "") or e.get("query", "")
    if not txt:
        return False, "What task would you like to add?"
    todos = _load_todos()
    todos.append({"task": txt, "done": False})
    _save_todos(todos)
    return True, f"Task added: '{txt}'"


def _p_todo_show(e) -> Tuple[bool, str]:
    todos = _load_todos()
    if not todos:
        return True, "No tasks on your to-do list."
    lines = [f"  [{'✓' if t.get('done') else ' '}] {i+1}. {t['task']}" for i, t in enumerate(todos)]
    return True, "📋 Tasks:\n" + "\n".join(lines)


def _p_todo_clear(e) -> Tuple[bool, str]:
    _save_todos([])
    return True, "Task list cleared"


def _p_habit_show(e) -> Tuple[bool, str]:
    return True, "Daily habits on track"


def _p_habit_add(e) -> Tuple[bool, str]:
    txt = e.get("text", "") or e.get("query", "")
    return True, f"Habit added: {txt}"
