"""
Nebula v9 — Intent Matcher, Entity Extraction, and Typo/Alias Normalization
"""
import re
import json
from typing import Optional, Tuple, Dict, Any, Set

from config import _ALIASES_FILE
from intents_db import _CMD_TABLE

_ALIAS_CACHE = None
_ALIAS_MTIME = 0


def _load_aliases() -> dict:
    global _ALIAS_CACHE, _ALIAS_MTIME
    try:
        if _ALIASES_FILE.exists():
            mtime = _ALIASES_FILE.stat().st_mtime
            if mtime != _ALIAS_MTIME or _ALIAS_CACHE is None:
                with open(_ALIASES_FILE, "r", encoding="utf-8") as f:
                    _ALIAS_CACHE = json.load(f)
                _ALIAS_MTIME = mtime
            return _ALIAS_CACHE or {}
    except Exception:
        pass
    return {}


def apply_aliases(text: str, context_triggers: Optional[Set[str]] = None) -> str:
    """Apply user-defined word substitutions from ~/.nebula_aliases.json."""
    if not text:
        return text
    aliases = _load_aliases()
    if not aliases:
        return text

    lo = text.lower()
    app_triggers = {"open", "launch", "start", "run", "goto", "go to", "close", "kill"}
    is_app_context = context_triggers and bool(context_triggers.intersection(app_triggers))
    has_app_word = any(lo.startswith(t + " ") or (" " + t + " ") in lo for t in app_triggers)

    if not is_app_context and not has_app_word:
        return text

    for raw_phrase, canonical in aliases.items():
        pattern = r'\b' + re.escape(raw_phrase.lower()) + r'\b'
        lo = re.sub(pattern, canonical.lower(), lo)
    return lo


_TYPOS = {
    "volune": "volume", "voume": "volume", "voulme": "volume", "voiume": "volume", "volum": "volume",
    "connfig": "config", "confg": "config", "conifg": "config", "ocnfig": "config",
    "shwo": "show", "sohw": "show", "shpw": "show",
    "searh": "search", "serach": "search", "seach": "search",
    "helpp": "help", "hlep": "help", "helo": "help",
    "tiem": "time", "timme": "time", "itme": "time",
    "statsu": "status", "stauts": "status", "statis": "status",
    "pasword": "password", "passwrod": "password", "passowrd": "password",
    "dowonload": "download", "downolad": "download", "donwload": "download",
    "schreenshot": "screenshot", "sceenshot": "screenshot", "screnshot": "screenshot",
    "calander": "calendar", "calender": "calendar",
    "remider": "reminder", "remainder": "reminder",
    "brwoser": "browser", "broswer": "browser", "borwser": "browser",
    "toglle": "toggle", "togle": "toggle", "toogle": "toggle", "toggel": "toggle", "toggll": "toggle", "toggl": "toggle",
    "dynami": "dynamic", "dymamic": "dynamic", "dynamc": "dynamic",
    "recieve": "receive", "seperate": "separate", "occured": "occurred",
    "tommorrow": "tomorrow", "tommorow": "tomorrow", "tomorrrow": "tomorrow",
    "calaculator": "calculator", "calculater": "calculator",
    "ststem": "system", "sustem": "system", "sysem": "system",
    "updat": "update", "updaet": "update",
    "intall": "install", "insatll": "install", "isntall": "install",
    "giit": "git", "gti": "git", "gigt": "git",
    "docekr": "docker", "dokcer": "docker", "dcoker": "docker",
    "pythno": "python", "pythn": "python", "pyhton": "python",
    "notbook": "notebook", "noteboook": "notebook",
    "rmeove": "remove", "remvoe": "remove", "rmove": "remove",
    "delte": "delete", "deelte": "delete", "dleet": "delete",
    "cretae": "create", "creat": "create", "craete": "create",
    "opne": "open", "oen": "open", "opeen": "open",
    "coyp": "copy", "ocpy": "copy", "cpoy": "copy",
    "mvoe": "move", "moe": "move",
    "ziip": "zip", "unizip": "unzip", "unpzip": "unzip",
    "clsoe": "close", "clos": "close",
    "wether": "weather", "wheather": "weather", "weathr": "weather",
    "jorunal": "journal", "jounral": "journal", "jouranl": "journal",
    "pmodoro": "pomodoro", "pomoodro": "pomodoro", "pomoro": "pomodoro",
    "laucnh": "launch", "lauch": "launch", "lnuach": "launch",
    "defien": "define", "defne": "define", "dfine": "define", "defiin": "define",
    "forumn": "forum", "forun": "forum", "fourm": "forum",
    "pff": "off", "of": "off",
    "reduc": "reduce", "reudce": "reduce", "redce": "reduce",
    "brightnes": "brightness", "birghtness": "brightness", "britness": "brightness",
    "volumn": "volume", "volm": "volume", "volue": "volume",
}


def _typo_correct(text: str) -> str:
    """Correct common typos and misspellings."""
    if not text:
        return text
    words = text.split()
    corrected = [_TYPOS.get(w.lower(), w) for w in words]
    return " ".join(corrected)


def _clean_for_match(text: str) -> set:
    """Extract normalized word set from input string."""
    clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return set(clean.split())


def _extract(text: str, executor: str) -> dict:
    """Extract entities from natural language text."""
    e = {"raw": text}
    lo = text.lower().strip()

    # URL
    m = re.search(r'https?://[^\s]+', text)
    if m:
        e["url"] = m.group(0)
    elif re.search(r'\bwww\.[^\s]+', lo):
        m2 = re.search(r'\bwww\.[^\s]+', lo)
        if m2:
            e["url"] = "https://" + m2.group(0)

    # Duration
    total = 0
    for pat, fn in [
        (r'(\d+)\s*h(?:our|r)s?', lambda n: int(n) * 3600),
        (r'(\d+)\s*m(?:in(?:ute)?)?s?', lambda n: int(n) * 60),
        (r'(\d+)\s*s(?:ec(?:ond)?)?s?', int),
    ]:
        for m2 in re.finditer(pat, lo):
            total += fn(m2.group(1))
    if total:
        e["duration"] = total

    # Level / Volume / Brightness
    _lv_patterns = [
        r'\b(\d+)\s*(?:percent|%)',
        r'volume\s+(?:to\s+|set\s+|at\s+)?(\d+)',
        r'(?:set|change|adjust)\s+(?:volume\s+)?(?:to\s+)?(\d+)',
        r'(?:brightness|volume)\s*[=:]?\s*(\d+)',
        r'\b(\d{1,3})\b(?!\s*(?:sec|min|hour|ms|hz|gb|mb|kb))',
    ]
    for _lp in _lv_patterns:
        _lm = re.search(_lp, lo)
        if _lm:
            _lv = int(next(g for g in _lm.groups() if g is not None))
            if 0 <= _lv <= 100:
                e["level"] = _lv
                break

    # Triggers for query extraction
    _TRIGGERS_ORDERED = [
        "in youtube search", "in claude search", "in gemini search", "in chatgpt search",
        "in perplexity search", "in reddit search", "in github search", "in amazon search",
        "in google search", "in wikipedia search",
        "search youtube for", "search claude for", "search gemini for", "search chatgpt for",
        "search reddit for", "search github for", "search amazon for", "search wikipedia for",
        "search for", "search", "google", "bing", "duckduckgo",
        "ask chatgpt", "ask claude", "ask gemini", "ask perplexity", "ask ai", "ask",
        "tell me about", "what is", "what are", "how to", "how do",
        "explain", "define", "weather in", "weather", "ping", "whois", "traceroute",
        "encrypt", "decrypt", "hash text", "hash", "slugify", "rot13",
        "fibonacci", "factorial", "bmi", "tip", "mortgage", "statistics",
        "prime factors", "is prime", "convert", "exchange rate",
        "crypto price", "bitcoin price", "news", "stock price", "stock", "download",
        "find duplicate", "find empty", "find large", "find", "qr code", "qr",
        "password", "say", "speak", "calc", "calculate", "math",
    ]

    for trig in _TRIGGERS_ORDERED:
        pattern = r'\b' + re.escape(trig) + r'\b\s*(.*)'
        match = re.search(pattern, lo)
        if match:
            extracted = text[match.start(1):].strip()
            if extracted:
                e["query"] = extracted
                break

    # Text (notes, reminders, todos)
    for trigger in (
        "note that ", "note ", "journal ", "diary ", "remind me to ",
        "remind me ", "todo ", "add todo ", "task ", "add task "
    ):
        if trigger in lo:
            t2 = lo.split(trigger, 1)[1].strip()
            if t2:
                e["text"] = t2
                break

    # App name
    if executor in (
        "app_open", "app_close", "si_proc_kill", "app_chrome", "app_firefox",
        "app_edge", "app_brave", "app_terminal", "app_vscode", "app_spotify",
        "mm_minimize_app", "mm_maximize_app", "mm_restore_app", "mm_open_software"
    ):
        m = re.search(r'(?:open|close|kill|launch|quit|stop|terminate|minimize|maximize|restore|expand|shrink)\s+([\w.-]+)', lo)
        if m:
            e["app_name"] = m.group(1)
        elif "name" in e:
            e["app_name"] = e["name"]

    # Fallback query
    if "query" not in e:
        skip = {
            "a", "an", "the", "my", "me", "please", "it", "in", "to", "for", "of", "and", "or",
            "at", "on", "with", "is", "are", "what", "how", "show", "tell", "give", "get", "check",
            "can", "do", "does", "will", "make", "run", "start", "stop", "let"
        }
        meaningful = [w for w in lo.split() if w not in skip and len(w) > 1]
        if meaningful:
            e["query"] = " ".join(meaningful)

    return e


class Matcher:
    """High-speed word-set intersection scoring intent matcher."""

    def __init__(self, table=None):
        self._table = table or _CMD_TABLE
        # Pre-compile triggers to frozensets
        self._compiled = [(frozenset(trig), (ex, weight)) for trig, (ex, weight) in self._table]

    def match(self, text: str) -> Optional[Tuple[str, float, dict]]:
        if not text or not text.strip():
            return None
        corrected = _typo_correct(text.strip())
        aliased = apply_aliases(corrected)
        words = _clean_for_match(aliased)
        if not words:
            return None

        best_ex = None
        best_score = 0.0
        n_words = len(words)

        for trig_set, (ex, weight) in self._compiled:
            if trig_set.issubset(words):
                n_trig = len(trig_set)
                spec = n_trig / n_words
                score = weight * (1.0 + spec * 0.5) * (1.0 + n_trig * 0.1)
                if score > best_score:
                    best_score = score
                    best_ex = ex

        if best_ex and best_score >= 0.5:
            entities = _extract(aliased, best_ex)
            return best_ex, best_score, entities
        return None
