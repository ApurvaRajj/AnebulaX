"""
Nebula v9 — Common Executor Helpers, File Handlers, and Shell Utilities
"""
import os
import re
import sys
import json
import shlex
import difflib
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from config import (
    IS_WIN, IS_MAC, IS_LINUX, NCFG, Log,
    _BOOKMARKS_FILE, _SOFTWARE_FILE, _CONF_DIR, _RICH, _C
)
from matcher import apply_aliases
from tts import _spk_ref

_SOFTWARE_MTIME = 0
_SOFTWARE_CACHE = {}
_DANGEROUS_PENDING = None
_VOICE_MODE_ACTIVE = [False]
_STT_REF = [None]


def _run(cmd, t=5) -> Tuple[bool, str]:
    """Run shell command with timeout."""
    try:
        if isinstance(cmd, str):
            p = subprocess.run(cmd, shell=True, timeout=t, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            p = subprocess.run(cmd, timeout=t, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return p.returncode == 0, ""
    except Exception as e:
        return False, str(e)


def _run_out(cmd, t=8, empty="No output") -> Tuple[bool, str]:
    """Run command and return stdout string."""
    try:
        if isinstance(cmd, str):
            p = subprocess.run(cmd, shell=True, timeout=t, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        else:
            p = subprocess.run(cmd, timeout=t, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out = (p.stdout or "").strip()
        return (True, out if out else empty) if p.returncode == 0 else (False, out or f"Exit {p.returncode}")
    except Exception as e:
        return False, str(e)


def _send_keys(keys: str):
    """Simulate key presses across platforms."""
    try:
        if IS_WIN:
            try:
                import pyautogui
                pyautogui.hotkey(*keys.split("+"))
                return
            except Exception:
                pass
            subprocess.run(["powershell", "-c", f"$ws = New-Object -ComObject wscript.shell; $ws.SendKeys('{{{keys}}}')"], stdout=subprocess.DEVNULL)
        elif IS_MAC:
            subprocess.run(["osascript", "-e", f'tell app "System Events" to keystroke "{keys}"'], stdout=subprocess.DEVNULL)
        else:
            subprocess.run(["xdotool", "key", keys.lower()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def _find_browser_cmd():
    """Find installed browser binary on Linux."""
    if not IS_LINUX:
        return None
    for b in ["google-chrome-stable", "google-chrome", "brave-browser", "brave", "chromium-browser", "chromium", "firefox"]:
        try:
            r = subprocess.run(["which", b], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except Exception:
            pass
    return None


def _open_url(url: str):
    """Open URL in default or configured browser."""
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    pref = NCFG.get("default_browser", "system").lower()
    try:
        if pref != "system":
            if IS_WIN:
                subprocess.Popen(["cmd", "/c", "start", pref, url], shell=True)
                return
            elif IS_MAC:
                subprocess.Popen(["open", "-a", pref, url])
                return
            else:
                subprocess.Popen([pref, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
        # System default
        bcmd = _find_browser_cmd() if IS_LINUX else None
        if bcmd:
            subprocess.Popen([bcmd, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            import webbrowser
            webbrowser.open(url)
    except Exception:
        import webbrowser
        webbrowser.open(url)


def _search_url(query: str) -> str:
    """Build web search URL based on default search engine."""
    engine = NCFG.get("default_search", "google").lower()
    import urllib.parse
    q = urllib.parse.quote_plus(query)
    engines = {
        "google": f"https://www.google.com/search?q={q}",
        "bing": f"https://www.bing.com/search?q={q}",
        "duckduckgo": f"https://duckduckgo.com/?q={q}",
        "brave": f"https://search.brave.com/search?q={q}",
        "yahoo": f"https://search.yahoo.com/search?p={q}",
    }
    return engines.get(engine, engines["google"])


def smart_url_parse(text: str) -> Optional[str]:
    """Parse text into full URL if it matches known sites, fuzzy names, or domains."""
    if not text:
        return None
    t = text.lower().strip().replace(" ", "")
    common_sites = {
        "youtube": "www.youtube.com", "google": "www.google.com",
        "facebook": "www.facebook.com", "twitter": "twitter.com",
        "x": "x.com", "instagram": "www.instagram.com",
        "reddit": "www.reddit.com", "github": "github.com",
        "stackoverflow": "stackoverflow.com", "amazon": "www.amazon.com",
        "netflix": "www.netflix.com", "linkedin": "www.linkedin.com",
        "wikipedia": "www.wikipedia.org", "gmail": "mail.google.com",
        "canva": "www.canva.com", "figma": "www.figma.com",
        "notion": "www.notion.so", "trello": "trello.com",
        "slack": "slack.com", "zoom": "zoom.us",
        "discord": "discord.com", "twitch": "www.twitch.tv",
        "spotify": "open.spotify.com", "chatgpt": "chat.openai.com",
        "claude": "claude.ai", "gemini": "gemini.google.com",
        "messages": "messages.google.com/web", "messages web": "messages.google.com/web",
        "whatsapp": "web.whatsapp.com", "telegram": "web.telegram.org",
        "outlook": "outlook.live.com", "drive": "drive.google.com",
        "docs": "docs.google.com", "sheets": "sheets.google.com",
    }
    if t in common_sites:
        return f"https://{common_sites[t]}"
    matches = difflib.get_close_matches(t, list(common_sites.keys()), n=1, cutoff=0.82)
    if matches:
        return f"https://{common_sites[matches[0]]}"
    if re.match(r'^[a-z0-9\-]+\.(com|org|net|io|co|gov|edu|ai|dev|app|in|me|tv|cc)$', t):
        return f"https://{t}"
    return None


def _load_bookmarks() -> dict:
    try:
        if _BOOKMARKS_FILE.exists():
            with open(_BOOKMARKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_bookmarks(bms: dict):
    try:
        with open(_BOOKMARKS_FILE, "w", encoding="utf-8") as f:
            json.dump(bms, f, indent=2)
    except Exception:
        pass


def find_bookmark(spoken: str) -> Tuple[Optional[str], Optional[str]]:
    """Fuzzy-match spoken phrase against bookmarks. Returns (key, url)."""
    bms = _load_bookmarks()
    if not bms or not spoken:
        return None, None
    key = spoken.lower().strip()
    if key in bms:
        return key, bms[key]
    for k, v in bms.items():
        if k.lower() == key:
            return k, v
    for k, v in bms.items():
        if key in k.lower() or k.lower() in key:
            return k, v
    matches = difflib.get_close_matches(key, list(bms.keys()), n=1, cutoff=0.75)
    if matches:
        return matches[0], bms[matches[0]]
    return None, None


def _load_software() -> dict:
    sw = {}
    try:
        if _SOFTWARE_FILE.exists():
            for line in _SOFTWARE_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "|" in line:
                    parts = line.split("|", 1)
                    k = parts[0].strip().lower()
                    v = parts[1].strip()
                    if k and v:
                        sw[k] = v
    except Exception:
        pass
    return sw


def reload_software() -> dict:
    """Hot-reload software.txt if modified."""
    global _SOFTWARE_MTIME, _SOFTWARE_CACHE
    try:
        mtime = _SOFTWARE_FILE.stat().st_mtime if _SOFTWARE_FILE.exists() else 0
        if mtime != _SOFTWARE_MTIME:
            _SOFTWARE_CACHE = _load_software()
            _SOFTWARE_MTIME = mtime
    except Exception:
        pass
    return _SOFTWARE_CACHE


def find_software(spoken: str) -> Tuple[Optional[str], Optional[str]]:
    """Fuzzy-match spoken app name against software registry."""
    sw = reload_software()
    if not sw or not spoken:
        return None, None
    key = spoken.lower().strip()
    if key in sw:
        return key, sw[key]
    matches = difflib.get_close_matches(key, list(sw.keys()), n=1, cutoff=0.85)
    if matches:
        return matches[0], sw[matches[0]]
    return None, None


def _open_software_by_path(path: str) -> bool:
    """Execute an app path."""
    if not path:
        return False
    try:
        if IS_WIN:
            if path.endswith(":"):
                subprocess.Popen(['start', path], shell=True)
            elif os.path.exists(path):
                subprocess.Popen([path], shell=False)
            else:
                subprocess.Popen([path], shell=True)
        elif IS_MAC:
            subprocess.Popen(["open", "-a", path] if not os.path.exists(path) else [path])
        else:
            if os.path.exists(path):
                subprocess.Popen([path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen(shlex.split(path) if " " in path else [path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def _app(linux_cmd, mac_app, win_proc) -> Tuple[bool, str]:
    """Launch application by platform binary name."""
    try:
        if IS_WIN:
            subprocess.Popen(["cmd", "/c", "start", "", win_proc], shell=True)
        elif IS_MAC:
            subprocess.Popen(["open", "-a", mac_app])
        else:
            subprocess.Popen(shlex.split(linux_cmd) if " " in linux_cmd else [linux_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True, f"{mac_app} opened"
    except Exception as ex:
        return False, f"Could not open {mac_app}: {ex}"


def _confirm_dangerous(action_desc: str) -> bool:
    """
    Ask user to confirm a dangerous action.
    In Voice Mode: speaks the confirmation question and actively listens for voice confirmation ("yes", "confirm").
    In Text Mode: prompts inline via stdin.
    """
    global _DANGEROUS_PENDING
    if _VOICE_MODE_ACTIVE[0] and _spk_ref[0]:
        _spk_ref[0].speak(f"Are you sure you want to {action_desc}? Say yes to confirm.", role="nebula")
        # Actively listen for spoken confirmation
        stt = _STT_REF[0]
        if stt:
            import time
            time.sleep(1.5)  # allow TTS to finish
            heard = stt.listen_phrase(timeout=5.0, phrase_time_limit=3.0)
            if heard:
                heard_clean = heard.strip().lower()
                confirmed = any(w in heard_clean for w in ("yes", "confirm", "proceed", "sure", "ok", "yep", "yeah", "do it"))
                if confirmed:
                    return True
        return False
    else:
        # Text mode inline prompt
        if _RICH and _C:
            _C.print(f"  [bold yellow]⚠ CONFIRM: {action_desc.upper()}?[/bold yellow] ", end="")
            try:
                ans = _C.input("[[bold red]y/n[/bold red]]: ").strip().lower()
            except Exception:
                ans = "n"
        else:
            ans = input(f"  WARNING: {action_desc}? [y/n]: ").strip().lower()
        return ans in ("y", "yes", "1", "ok", "sure", "confirm", "proceed")
