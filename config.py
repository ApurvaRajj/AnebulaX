"""
Nebula v9 — Configuration, Paths, and Logging
"""
import os
import sys
import json
import platform
from pathlib import Path

VERSION = "9.0"

IS_WIN = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

try:
    from rich import print as rprint
    from rich.panel import Panel
    from rich.table import Table
    from rich.console import Console
    RICH = True
    _RICH = True
    _C = Console()
except ImportError:
    RICH = False
    _RICH = False
    _C = None
    def rprint(*a, **k): print(*a)
    def Panel(x, **k): return str(x)
    def Table(**k): pass

class Cfg:
    OPENAI_KEY    = os.getenv("OPENAI_API_KEY", "")    or {}
    ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "") or {}
    GEMINI_KEY    = os.getenv("GEMINI_API_KEY", "")    or {}
    OPENEX_KEY    = os.getenv("OPENEXCHANGERATES_KEY", "")
    LOCAL = "nebula"; CLOUD = "nova"
    HOME  = Path.home(); DESK  = HOME / "Desktop"
    DOCS  = HOME / ("My Documents" if IS_WIN else "Documents")
    DL    = HOME / "Downloads"; PICS = HOME / "Pictures"; MUS = HOME / "Music"
    VIDEOS = HOME / "Videos"
    TTS_RATE = 145; TTS_VOL = 0.95
    P_TH = 0.04; I_TH = 0.04; DEBUG = False
    LOG       = Path("nebula.log"); NOTES = HOME / ".nebula_notes.txt"
    TODOS     = HOME / ".nebula_todos.json"; HABITS = HOME / ".nebula_habits.json"
    SETUP_DONE = HOME / ".nebula_setup_done"
    KEY_FILE   = HOME / ".nebula_key"
    JOURNAL    = HOME / ".nebula_journal.txt"
    JARVIS = ("You are JARVIS from Iron Man. Respond in 1-3 sentences max. "
              "Direct, confident, witty. Address user as 'sir' occasionally.")

# ── Paths ─────────────────────────────────────────────────────────────────────
_HOME = Path.home()
_CONF_DIR = _HOME / ".nebula"
_CFG_FILE = _HOME / ".nebula_config.json"
_NOTES_FILE = _CONF_DIR / "notes.txt"
_NOTES_DB_FILE = _HOME / ".nebula_notes_db.json"
_TODO_FILE = _CONF_DIR / "todos.json"
_HABIT_FILE = _CONF_DIR / "habits.json"
_REMINDERS_FILE = _HOME / ".nebula_reminders.json"
_CMD_HISTORY_FILE = _HOME / ".nebula_cmd_history.json"
_ALIASES_FILE = _HOME / ".nebula_aliases.json"
_BOOKMARKS_FILE = _HOME / ".nebula_bookmarks.json"
_SOFTWARE_FILE = _HOME / ".nebula_software.txt"
_LOG_FILE = _HOME / "nebula.log"
_VOSK_MODEL_DIR = _HOME / ".nebula" / "vosk-model-small-en-us-0.15"

# ── Logging ───────────────────────────────────────────────────────────────────
class Log:
    @staticmethod
    def _write(lvl, msg):
        import time
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] [{lvl}] {msg}\n")
        except Exception:
            pass

    @staticmethod
    def info(m): Log._write("INFO", m)
    @staticmethod
    def warn(m): Log._write("WARN", m)
    @staticmethod
    def error(m): Log._write("ERROR", m)
    @staticmethod
    def debug(m): Log._write("DEBUG", m)


# ── Configuration defaults ────────────────────────────────────────────────────
_DEF_CFG = {
    "default_ai": "gemini",
    "default_browser": "system",
    "gemini_yolo": False,
    "gemini_yolo_asked": False,
    "tts_on": True,
    "tts_nebula": True,
    "tts_nova": True,
    "nova_confirm": True,
    "voice_energy": 300,
    "dynamic_energy": True,
    "pause_threshold": 0.50,
    "nova_enabled": True,
    "default_search": "google",
    "maximize_browser": True,
    "pomodoro_work": 25,
    "pomodoro_break": 5,
    "theme": "blue",
    "stt_engine": "google",
    "vosk_model_path": "",
    "mic_device_index": None,
}


def _load_cfg():
    if _CFG_FILE.exists():
        try:
            with open(_CFG_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
                cfg = dict(_DEF_CFG)
                cfg.update(d)
                return cfg
        except Exception as e:
            Log.error(f"Config load error: {e}")
    return dict(_DEF_CFG)


def _save_cfg(cfg):
    try:
        with open(_CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        Log.error(f"Config save error: {e}")


def _init_user_files():
    """Ensure user-configurable files exist with helpful initial contents on first run."""
    _CONF_DIR.mkdir(parents=True, exist_ok=True)
    if not _ALIASES_FILE.exists():
        initial_aliases = {
            "not bad": "notepad",
            "not bad plus plus": "notepad++",
            "you tube": "youtube",
            "v s code": "vscode",
            "sub lime": "sublime",
            "sub line": "sublime",
            "fire fox": "firefox",
            "goo gle": "google",
            "what's app": "whatsapp",
            "whats app": "whatsapp",
            "face book": "facebook",
            "git hub": "github",
        }
        try:
            _ALIASES_FILE.write_text(json.dumps(initial_aliases, indent=2), encoding="utf-8")
        except Exception:
            pass

    if not _BOOKMARKS_FILE.exists():
        initial_bookmarks = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "canva": "https://www.canva.com",
            "reddit": "https://reddit.com",
            "netflix": "https://netflix.com",
            "chatgpt": "https://chat.openai.com",
            "claude": "https://claude.ai",
            "gemini": "https://gemini.google.com",
        }
        try:
            _BOOKMARKS_FILE.write_text(json.dumps(initial_bookmarks, indent=2), encoding="utf-8")
        except Exception:
            pass

    if not _SOFTWARE_FILE.exists():
        initial_sw = (
            "# Custom software registry for Nebula\n"
            "# Format: spoken_name | executable_path_or_command\n"
            "# Examples:\n"
            "# code | /usr/bin/code\n"
            "# brave | /usr/bin/brave-browser\n"
        )
        try:
            _SOFTWARE_FILE.write_text(initial_sw, encoding="utf-8")
        except Exception:
            pass

    if not _CMD_HISTORY_FILE.exists():
        try:
            _CMD_HISTORY_FILE.write_text("[]", encoding="utf-8")
        except Exception:
            pass
    if not _NOTES_DB_FILE.exists():
        try:
            _NOTES_DB_FILE.write_text("[]", encoding="utf-8")
        except Exception:
            pass
    if not _REMINDERS_FILE.exists():
        try:
            _REMINDERS_FILE.write_text("[]", encoding="utf-8")
        except Exception:
            pass


_init_user_files()
NCFG = _load_cfg()


def _theme():
    return NCFG.get("theme", "blue")
