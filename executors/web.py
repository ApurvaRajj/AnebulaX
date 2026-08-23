"""
Nebula v9 — Web, Search, Browser Navigation, and Bookmarks Executors
"""
import re
import urllib.parse
import subprocess
from typing import Tuple

from config import IS_WIN, IS_MAC, IS_LINUX, NCFG
from matcher import apply_aliases
from executors.common import (
    _open_url, _search_url, _find_browser_cmd, _send_keys,
    smart_url_parse, find_bookmark, _load_bookmarks, _save_bookmarks,
    find_software, _open_software_by_path, _run
)


def _wb_q(template: str, e: dict, label: str) -> Tuple[bool, str]:
    q = e.get("query", "").strip() or e.get("raw", "").strip()
    # Strip leading trigger terms
    q = re.sub(r'^(?:search|for|in|find|ask|lookup)\s+', '', q, flags=re.IGNORECASE).strip()
    if not q:
        q = "home"
    url = template.format(urllib.parse.quote_plus(q))
    _open_url(url)
    return True, f"Opened {label}: {q}"


def _wb_ask(ai: str, e: dict) -> Tuple[bool, str]:
    q = e.get("query", "").strip() or e.get("raw", "").strip()
    urls = {
        "chatgpt": f"https://chat.openai.com/?q={urllib.parse.quote_plus(q)}" if q else "https://chat.openai.com",
        "claude": f"https://claude.ai/new?q={urllib.parse.quote_plus(q)}" if q else "https://claude.ai",
        "gemini": f"https://gemini.google.com/app" if not q else f"https://gemini.google.com/app?q={urllib.parse.quote_plus(q)}",
        "perplexity": f"https://www.perplexity.ai/search?q={urllib.parse.quote_plus(q)}" if q else "https://www.perplexity.ai",
    }
    target = urls.get(ai.lower(), f"https://google.com/search?q={urllib.parse.quote_plus(q)}")
    _open_url(target)
    return True, f"Opened {ai.capitalize()}: {q}" if q else f"Opened {ai.capitalize()}"


def _web_search(e) -> Tuple[bool, str]:
    q = e.get("query", "").strip() or e.get("raw", "").strip()
    q = re.sub(r'^(?:search|for|google|lookup)\s+', '', q, flags=re.IGNORECASE).strip()
    if not q:
        return False, "What would you like to search for?"
    _open_url(_search_url(q))
    return True, f"Searching for: {q}"


def _web_private(e) -> Tuple[bool, str]:
    """Launch private / incognito browser window."""
    if IS_WIN:
        subprocess.Popen(["cmd", "/c", "start", "chrome", "--incognito"], shell=True)
    elif IS_MAC:
        subprocess.Popen(["open", "-na", "Google Chrome", "--args", "--incognito"])
    else:
        bcmd = _find_browser_cmd() or "firefox"
        flag = "--private-window" if "firefox" in bcmd else "--incognito"
        subprocess.Popen([bcmd, flag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True, "Opened private browser window"


def _web_open_site_smart(e) -> Tuple[bool, str]:
    """Smart 'go to <target>' handler."""
    q = str(e.get("query", "") or e.get("raw", "") or "").strip()
    q = re.sub(r'^\s*(go\s+to|goto|visit|open|navigate\s+to)\s+', '', q, flags=re.IGNORECASE).strip()
    if not q:
        return False, "Where would you like to go?"
    clean_q = apply_aliases(q, {"goto", "open"})
    bm_key, bm_url = find_bookmark(clean_q)
    if bm_url:
        _open_url(bm_url)
        return True, f"Opening bookmark: {bm_key}"
    url = smart_url_parse(clean_q)
    if url:
        _open_url(url)
        return True, f"Opening {clean_q}"
    sw_key, sw_path = find_software(clean_q)
    if sw_path and _open_software_by_path(sw_path):
        return True, f"Opening {sw_key}"
    if re.match(r'^[a-z0-9\-]+\.(com|org|net|io|co|gov|edu|ai|dev|app|in|me|tv|cc)', clean_q.lower()):
        url = clean_q if clean_q.startswith("http") else "https://" + clean_q
        _open_url(url)
        return True, f"Opening {url}"
    _open_url(_search_url(q))
    return True, f"Searching for: {q}"


def _mm_add_bookmark(e) -> Tuple[bool, str]:
    raw = e.get("raw", "") or e.get("query", "") or ""
    raw = re.sub(r'^\s*(add|save|set)\s+bookmark\s+', '', raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r'^\s*bookmark\s+', '', raw, flags=re.IGNORECASE).strip()
    parts = raw.split(None, 1)
    if len(parts) < 2:
        return False, "Usage: add bookmark <name> <url>"
    name = parts[0].strip().lower()
    url = parts[1].strip()
    if not url.startswith("http"):
        url = "https://" + url
    bms = _load_bookmarks()
    bms[name] = url
    _save_bookmarks(bms)
    return True, f"Bookmark added: {name} → {url}"


def _mm_del_bookmark(e) -> Tuple[bool, str]:
    raw = e.get("raw", "") or e.get("query", "") or ""
    name = re.sub(r'^\s*(delete|remove|del)\s+bookmark\s+', '', raw, flags=re.IGNORECASE).strip().lower()
    if not name:
        return False, "Usage: delete bookmark <name>"
    bms = _load_bookmarks()
    if name in bms:
        del bms[name]
        _save_bookmarks(bms)
        return True, f"Bookmark removed: {name}"
    for k in list(bms.keys()):
        if k.lower() == name or name in k.lower():
            del bms[k]
            _save_bookmarks(bms)
            return True, f"Bookmark removed: {k}"
    return False, f"Bookmark '{name}' not found"


def _mm_list_bookmarks(e) -> Tuple[bool, str]:
    bms = _load_bookmarks()
    if not bms:
        return True, "No bookmarks saved yet. Use 'add bookmark <name> <url>'."
    lines = [f"  {k:<20} → {v}" for k, v in bms.items()]
    return True, f"📋 Bookmarks ({len(bms)}):\n" + "\n".join(lines)


# ── Browser Tab Controls ─────────────────────────────────────────────────────
def _bc_close_tab(e) -> Tuple[bool, str]:
    _send_keys("ctrl+w") if (IS_WIN or IS_LINUX) else _send_keys("command+w")
    return True, "Closed tab"


def _bc_new_tab(e) -> Tuple[bool, str]:
    _send_keys("ctrl+t") if (IS_WIN or IS_LINUX) else _send_keys("command+t")
    return True, "New tab opened"


def _bc_refresh(e) -> Tuple[bool, str]:
    _send_keys("F5" if IS_WIN else "ctrl+r")
    return True, "Tab refreshed"


def _bc_back(e) -> Tuple[bool, str]:
    _send_keys("alt+Left")
    return True, "Navigated back"


def _bc_forward(e) -> Tuple[bool, str]:
    _send_keys("alt+Right")
    return True, "Navigated forward"
