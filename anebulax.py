"""
AnebulaX — AI Voice + OS Assistant Entrypoint
"""
import sys
import os

from config import (
    VERSION, IS_WIN, IS_MAC, IS_LINUX, NCFG, Cfg, Log, RICH, _RICH, rprint,
    Panel, Table, _HOME, _CONF_DIR, _CFG_FILE, _NOTES_FILE, _NOTES_DB_FILE,
    _TODO_FILE, _HABIT_FILE, _REMINDERS_FILE, _CMD_HISTORY_FILE, _ALIASES_FILE,
    _BOOKMARKS_FILE, _SOFTWARE_FILE, _LOG_FILE, _VOSK_MODEL_DIR, _theme,
    _load_cfg, _save_cfg, _init_user_files, no_c_stderr
)

from licensing import (
    EMBEDDED_PUBLIC_KEY_HEX, DEFAULT_COMMUNITY_LICENSE, LICENSE_FILE_PATH,
    get_machine_fingerprint, generate_keypair, sign_license, verify_license,
    save_license_file, ensure_default_license
)

from intents_db import (
    _CMD_TABLE, _SPEAK_EXECUTORS, _SILENT_EXECUTORS, _FACTS, _QUOTES,
    _AFFIRMATIONS, _MAGIC8
)

from matcher import (
    Matcher, _extract, _clean_for_match, _typo_correct, apply_aliases, _TYPOS
)

from tts import (
    TTS, _tts_clean, _should_speak, _spk_ref
)

from stt import (
    STT, _ensure_vosk_model
)

from executors import (
    _e, find_bookmark, find_software, reload_software, _open_software_by_path,
    smart_url_parse, _confirm_dangerous
)

from main import (
    AnebulaX, Nebula, GeminiProvider, main, _add_cmd_history
)

if __name__ == "__main__":
    main()
