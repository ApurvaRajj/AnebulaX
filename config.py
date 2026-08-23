"""
AnebulaX — Configuration, Paths, and Audio Stderr Suppression
"""
import os
import sys
import json
import ctypes
import platform
from pathlib import Path
from contextlib import contextmanager

# ── Kill JACK / ALSA / PortAudio spam BEFORE any audio import ────────────────
os.environ.update({
    'PYGAME_HIDE_SUPPORT_PROMPT': '1',
    'PYTHONWARNINGS': 'ignore',
    'JACK_NO_AUDIO_RESERVATION': '1',
    'JACK_NO_START_SERVER': '1',
    'PA_ALSA_PLUGHW': '1',
})

VERSION = "1.0"

IS_WIN = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"
IS_LINUX = platform.system() == "Linux"

# ── Silence C-level ALSA / JACK libraries ────────────────────────────────────
if IS_LINUX:
    try:
        _ALS = ctypes.cdll.LoadLibrary("libasound.so.2")
        _AEH = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
        _ALS.snd_lib_error_set_handler(_AEH(lambda *_: None))
    except Exception:
        pass
    for _jlib in ("libjack.so.0", "libjack.so", "libjack64.so.0"):
        try:
            _JL = ctypes.cdll.LoadLibrary(_jlib)
            _JEH = ctypes.CFUNCTYPE(None, ctypes.c_char_p)
            _NOP = _JEH(lambda *_: None)
            try:
                _JL.jack_set_error_function(_NOP)
            except Exception:
                pass
            try:
                _JL.jack_set_info_function(_NOP)
            except Exception:
                pass
            break
        except Exception:
            pass


@contextmanager
def no_c_stderr():
    """Suppress low-level C stderr (fd 2) output during ALSA / JACK / PortAudio device probing."""
    try:
        stderr_fd = sys.stderr.fileno()
    except Exception:
        stderr_fd = 2
    try:
        sys.stderr.flush()
        saved_stderr_fd = os.dup(stderr_fd)
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, stderr_fd)
        os.close(devnull_fd)
        try:
            yield
        finally:
            sys.stderr.flush()
            os.dup2(saved_stderr_fd, stderr_fd)
            os.close(saved_stderr_fd)
    except Exception:
        yield


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
    LOCAL = "anebulax"; CLOUD = "nova"
    HOME  = Path.home(); DESK  = HOME / "Desktop"
    DOCS  = HOME / ("My Documents" if IS_WIN else "Documents")
    DL    = HOME / "Downloads"; PICS = HOME / "Pictures"; MUS = HOME / "Music"
    VIDEOS = HOME / "Videos"
    TTS_RATE = 145; TTS_VOL = 0.95
    P_TH = 0.04; I_TH = 0.04; DEBUG = False
    LOG       = Path("anebulax.log"); NOTES = HOME / ".anebulax_notes.txt"
    TODOS     = HOME / ".anebulax_todos.json"; HABITS = HOME / ".anebulax_habits.json"
    SETUP_DONE = HOME / ".anebulax_setup_done"
    KEY_FILE   = HOME / ".anebulax_key"
    JOURNAL    = HOME / ".anebulax_journal.txt"
    JARVIS = ("You are JARVIS from Iron Man. Respond in 1-3 sentences max. "
              "Direct, confident, witty. Address user as 'sir' occasionally.")

# ── Paths ─────────────────────────────────────────────────────────────────────
_HOME = Path.home()
_CONF_DIR = _HOME / ".anebulax"
_CFG_FILE = _HOME / ".anebulax_config.json"
_NOTES_FILE = _CONF_DIR / "notes.txt"
_NOTES_DB_FILE = _HOME / ".anebulax_notes_db.json"
_TODO_FILE = _CONF_DIR / "todos.json"
_HABIT_FILE = _CONF_DIR / "habits.json"
_REMINDERS_FILE = _HOME / ".anebulax_reminders.json"
_CMD_HISTORY_FILE = _HOME / ".anebulax_cmd_history.json"
_ALIASES_FILE = _HOME / ".anebulax_aliases.json"
_BOOKMARKS_FILE = _HOME / ".anebulax_bookmarks.json"
_SOFTWARE_FILE = _HOME / ".anebulax_software.txt"
_LICENSE_FILE = _HOME / ".anebulax_license.key"
_LOG_FILE = _CONF_DIR / "anebulax.log"
_VOSK_MODEL_DIR = _CONF_DIR / "vosk-model"


# ── Configuration Defaults ───────────────────────────────────────────────────
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
    "nova_enabled": None,
    "default_search": "google",
    "maximize_browser": True,
    "pomodoro_work": 25,
    "pomodoro_break": 5,
    "theme": "blue",
    "stt_engine": "google",
    "vosk_model_path": "",
    "mic_device_index": None,
    "dynamic_energy": True,
    "agy_model": "flash",  # "flash_lite" (cheapest), "flash" (better), "pro" (best)
}


def _load_cfg() -> dict:
    cfg = dict(_DEF_CFG)
    # Check new config file, fallback to legacy if exists
    target = _CFG_FILE if _CFG_FILE.exists() else (_HOME / ".nebula_config.json")
    if target.exists():
        try:
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    cfg.update(data)
        except Exception:
            pass
    return cfg


def _save_cfg(cfg: dict):
    _CONF_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(_CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass


NCFG = _load_cfg()


def _theme() -> str:
    return NCFG.get("theme", "blue")


class Log:
    @staticmethod
    def _write(level: str, msg: str):
        import datetime
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {level}: {msg}"
        if NCFG.get("debug", False) or level in ("ERROR", "WARN"):
            if RICH and _C:
                _C.print(f"[dim]{line}[/dim]")
            else:
                print(line)
        try:
            _CONF_DIR.mkdir(parents=True, exist_ok=True)
            with open(_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    @staticmethod
    def info(msg: str): Log._write("INFO", msg)
    @staticmethod
    def warn(msg: str): Log._write("WARN", msg)
    @staticmethod
    def error(msg: str): Log._write("ERROR", msg)
    @staticmethod
    def debug(msg: str):
        if NCFG.get("debug", False):
            Log._write("DEBUG", msg)


def _init_user_files():
    """Auto-generate default configuration and data files in ~/.anebulax_*."""
    _CONF_DIR.mkdir(parents=True, exist_ok=True)

    if not _ALIASES_FILE.exists():
        default_aliases = {
            "not bad": "notepad",
            "you tube": "youtube",
            "vs code": "code",
            "visual studio": "code",
            "chrome browser": "chrome",
        }
        try:
            _ALIASES_FILE.write_text(json.dumps(default_aliases, indent=2), encoding="utf-8")
        except Exception:
            pass

    if not _BOOKMARKS_FILE.exists():
        default_bookmarks = {
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
            _BOOKMARKS_FILE.write_text(json.dumps(default_bookmarks, indent=2), encoding="utf-8")
        except Exception:
            pass

    if not _SOFTWARE_FILE.exists():
        default_software = (
            "# AnebulaX Custom Software Registry\n"
            "# Format: app_name | path_to_executable\n"
            "# Example:\n"
            "# spotify | /usr/bin/spotify\n"
            "# pycharm | /opt/pycharm/bin/pycharm.sh\n"
        )
        try:
            _SOFTWARE_FILE.write_text(default_software, encoding="utf-8")
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
