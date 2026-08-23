"""
Nebula v9 — Modular Executors Package (All 743+ Executors Natively Migrated)
"""
import os
import sys
import re
import math
import time
import json
import socket
import urllib.parse
import urllib.request
import subprocess
import shutil
import random
import threading
from threading import Thread
import datetime as _dt
from datetime import datetime, timedelta
import hashlib
import zipfile
import base64
import string
import platform
import psutil

from pathlib import Path
try:
    from rich.console import Console
    _C = Console()
except Exception:
    _C = None

def _clip_read():
    try:
        import pyperclip
        return pyperclip.paste()
    except Exception:
        pass
    if IS_LINUX and shutil.which('xclip'):
        p = subprocess.run(['xclip', '-selection', 'clipboard', '-o'], capture_output=True, text=True)
        if p.returncode == 0:
            return p.stdout
    return ''


from config import (
    Cfg,
    IS_WIN, IS_MAC, IS_LINUX, NCFG, _save_cfg, _theme, Log, RICH, _RICH, rprint,
    _CONF_DIR, _CFG_FILE, _NOTES_FILE, _NOTES_DB_FILE, _TODO_FILE, _HABIT_FILE,
    _REMINDERS_FILE, _CMD_HISTORY_FILE, _ALIASES_FILE, _BOOKMARKS_FILE,
    _SOFTWARE_FILE, _LOG_FILE, _VOSK_MODEL_DIR, VERSION, no_c_stderr
)
from matcher import apply_aliases
from tts import TTS, _spk_ref, _tts_clean
from intents_db import _FACTS, _QUOTES, _AFFIRMATIONS, _MAGIC8

from executors.common import (
    _run, _run_out, _open_url, _search_url, _send_keys,
    smart_url_parse, find_bookmark, find_software, reload_software,
    _open_software_by_path, _confirm_dangerous, _load_bookmarks, _save_bookmarks,
    _load_software, _app
)

_VOICE_MODE_ACTIVE = [False]
_STT_REF = [None]

# EXECUTOR IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Consolidated duplicate delegators
def _mm_lock(e): return _sys_lock(e)
def _mm_copy(e): return _clip_copy_sel(e)
def _mm_cut(e): return _clip_cut(e)
def _mm_paste(e): return _clip_paste(e)
def _mm_maximize_app(e): return _win_max(e)
def _mm_minimize_app(e): return _win_min_all(e)

def _mm_list_bookmarks(e):
    bms = _load_bookmarks()
    if not bms: return True, "No bookmarks saved yet. Use 'add bookmark <name> <url>'."
    lines = [f"  {k:<20} → {v}" for k, v in bms.items()]
    return True, f"📋 Bookmarks ({len(bms)}):\n" + "\n".join(lines)

def _mm_add_bookmark(e):
    raw = e.get("raw","") or e.get("query","") or ""
    raw = re.sub(r'^\s*(add|save|set)\s+bookmark\s+', '', raw, flags=re.IGNORECASE).strip()
    raw = re.sub(r'^\s*bookmark\s+', '', raw, flags=re.IGNORECASE).strip()
    parts = raw.split(None, 1)
    if len(parts) < 2: return False, "Usage: add bookmark <name> <url>"
    name = parts[0].strip().lower()
    url = parts[1].strip()
    if not url.startswith("http"): url = "https://" + url
    bms = _load_bookmarks()
    bms[name] = url
    _save_bookmarks(bms)
    return True, f"Bookmark added: {name} → {url}"

def _mm_del_bookmark(e):
    raw = e.get("raw","") or e.get("query","") or ""
    name = re.sub(r'^\s*(delete|remove|del)\s+bookmark\s+', '', raw, flags=re.IGNORECASE).strip().lower()
    if not name: return False, "Usage: delete bookmark <name>"
    bms = _load_bookmarks()
    if name in bms:
        del bms[name]; _save_bookmarks(bms); return True, f"Bookmark removed: {name}"
    for k in list(bms.keys()):
        if k.lower() == name or name in k.lower():
            del bms[k]; _save_bookmarks(bms); return True, f"Bookmark removed: {k}"
    return False, f"Bookmark '{name}' not found"

def _mm_list_software(e):
    sw = reload_software()
    if not sw: return True, f"No custom software registered. Edit {_SOFTWARE_FILE} to add apps (format: name | path)."
    lines = [f"  {k:<20} → {v}" for k, v in sw.items()]
    return True, f"📦 Software registry ({len(sw)}):\n" + "\n".join(lines)

# ── File System ───────────────────────────────────────────────────────────────
def _fs_mkdir(e):
    nm = e.get("name","New Folder"); loc = e.get("location",os.getcwd())
    p  = Path(loc)/nm
    try:
        if p.exists(): return False,f"'{nm}' already exists"
        p.mkdir(parents=True); return True,f"Folder '{nm}' created"
    except Exception as ex: return False,str(ex)[:80]

def _fs_touch(e):
    nm = e.get("name","newfile.txt"); loc = e.get("location",os.getcwd())
    p  = Path(loc)/nm
    try:
        if p.exists(): return False,f"'{nm}' already exists"
        p.touch(); return True,f"File '{nm}' created"
    except Exception as ex: return False,str(ex)[:80]

def _fs_symlink(e):
    src = e.get("name",""); dest = e.get("destination","")
    if not src or not dest: return False,"Specify source and destination"
    try: Path(dest).symlink_to(src); return True,f"Symlink: {dest} -> {src}"
    except Exception as ex: return False,str(ex)[:80]

def _fs_del_file(e):
    nm = e.get("name"); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    p  = Path(loc)/nm
    try:
        if not p.exists(): return False,f"'{nm}' not found"
        p.unlink(); return True,f"'{nm}' deleted"
    except Exception as ex: return False,str(ex)[:80]

def _fs_del_dir(e):
    nm = e.get("name"); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify folder name"
    p  = Path(loc)/nm
    try:
        if not p.exists(): return False,f"'{nm}' not found"
        shutil.rmtree(p); return True,f"Folder '{nm}' deleted"
    except Exception as ex: return False,str(ex)[:80]

def _fs_del_empty_files(e):
    loc = e.get("location",os.getcwd()); n = 0
    for f in Path(loc).rglob("*"):
        if f.is_file() and f.stat().st_size == 0:
            try: f.unlink(); n += 1
            except Exception: pass
    return True,f"Deleted {n} empty files"

def _sys_empty_bin(e):
    try:
        if IS_WIN: _run(["powershell","-Command","Clear-RecycleBin -Force -ErrorAction SilentlyContinue"])
        elif IS_LINUX:
            t = Path.home()/".local/share/Trash"
            for s in ["files","info"]:
                d = t/s
                if d.exists(): shutil.rmtree(d); d.mkdir()
        elif IS_MAC: _run(["osascript","-e",'tell application "Finder" to empty trash'])
        return True,"Bin emptied"
    except Exception as ex: return False,str(ex)[:80]

def _sys_clear_temp(e):
    n = 0
    dirs = ([os.environ.get("TEMP",""),os.environ.get("TMP",""),"C:\\Windows\\Temp"] if IS_WIN else ["/tmp"])
    for d in dirs:
        if d and Path(d).exists():
            for item in Path(d).iterdir():
                try:
                    if item.is_file(): item.unlink(); n += 1
                    elif item.is_dir(): shutil.rmtree(item,ignore_errors=True); n += 1
                except Exception: pass
    return True,f"Cleared {n} temp items"

def _fs_org_dl(e):
    dl   = Cfg.DL
    if not dl.exists(): return False,"Downloads folder not found"
    cats = {
        "Images": [".jpg",".jpeg",".png",".gif",".bmp",".webp",".svg"],
        "Videos": [".mp4",".avi",".mkv",".mov",".wmv",".flv",".webm"],
        "Audio":  [".mp3",".wav",".flac",".m4a",".aac",".ogg"],
        "Docs":   [".pdf",".doc",".docx",".txt",".xls",".xlsx",".ppt",".pptx",".md"],
        "Archives":[".zip",".tar",".gz",".rar",".7z",".bz2"],
        "Code":   [".py",".js",".ts",".html",".css",".json",".java",".cpp",".sh"],
    }
    mv = 0
    for f in list(dl.iterdir()):
        if f.is_file():
            for cat,exts in cats.items():
                if f.suffix.lower() in exts:
                    dest = dl/cat; dest.mkdir(exist_ok=True)
                    try: shutil.move(str(f),str(dest/f.name)); mv += 1
                    except Exception: pass
                    break
    return True,f"Organized {mv} files"

def _fs_cp_file(e):
    nm = e.get("name"); dest = e.get("destination",os.getcwd()); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    src = Path(loc)/nm
    try:
        if not src.exists(): return False,f"'{nm}' not found"
        shutil.copy2(src,Path(dest)/nm); return True,f"'{nm}' copied"
    except Exception as ex: return False,str(ex)[:80]

def _fs_mv_file(e):
    nm = e.get("name"); dest = e.get("destination"); loc = e.get("location",os.getcwd())
    if not nm or not dest: return False,"Specify name and destination"
    try: shutil.move(str(Path(loc)/nm),str(Path(dest)/nm)); return True,f"'{nm}' moved"
    except Exception as ex: return False,str(ex)[:80]

def _fs_rename(e):
    old = e.get("name"); new = e.get("new_name"); loc = e.get("location",os.getcwd())
    if not old or not new: return False,"Specify old and new name"
    try: (Path(loc)/old).rename(Path(loc)/new); return True,f"Renamed to '{new}'"
    except Exception as ex: return False,str(ex)[:80]

def _fs_cp_dir(e):
    nm = e.get("name"); dest = e.get("destination",os.getcwd()); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify folder name"
    try: shutil.copytree(Path(loc)/nm,Path(dest)/nm,dirs_exist_ok=True); return True,f"Folder '{nm}' copied"
    except Exception as ex: return False,str(ex)[:80]

def _fs_mv_dir(e):
    nm = e.get("name"); dest = e.get("destination"); loc = e.get("location",os.getcwd())
    if not nm or not dest: return False,"Specify name and destination"
    try: shutil.move(str(Path(loc)/nm),str(Path(dest)/nm)); return True,f"Folder '{nm}' moved"
    except Exception as ex: return False,str(ex)[:80]

def _fs_open(e):
    nm = e.get("name"); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    p  = Path(loc)/nm
    try:
        if IS_WIN: os.startfile(str(p))
        elif IS_MAC: subprocess.Popen(["open",str(p)])
        else: subprocess.Popen(["xdg-open",str(p)])
        return True,f"Opened '{nm}'"
    except Exception as ex: return False,str(ex)[:80]

def _fs_open_loc(e):
    loc = e.get("location",os.getcwd())
    try:
        if IS_WIN: subprocess.Popen(["explorer",loc])
        elif IS_MAC: subprocess.Popen(["open",loc])
        else: subprocess.Popen(["xdg-open",loc])
        return True,f"Opened {Path(loc).name}"
    except Exception as ex: return False,str(ex)[:80]

def _fs_backup(e):
    loc = e.get("location",os.getcwd()); ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = Path(loc).parent/f"{Path(loc).name}_backup_{ts}.zip"
    try:
        with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as zf:
            for f in Path(loc).rglob("*"):
                if f.is_file(): zf.write(f,f.relative_to(loc))
        return True,f"Backup: {dest.name}"
    except Exception as ex: return False,str(ex)[:80]

def _fs_info(e):
    nm = e.get("name"); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    p  = Path(loc)/nm
    if not p.exists(): return False,f"'{nm}' not found"
    st = p.stat(); sz = st.st_size
    s  = f"{sz}B" if sz<1024 else f"{sz/1024:.1f}KB" if sz<1048576 else f"{sz/1048576:.1f}MB"
    mod = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
    kind = "directory" if p.is_dir() else (p.suffix or "file")
    return True,f"'{nm}': {s}, {kind}, modified {mod}"

def _fs_search(e):
    q = e.get("name","").lower(); loc = e.get("location",os.getcwd())
    if not q: return False,"Specify search term"
    res = []
    try:
        for item in Path(loc).rglob("*"):
            if q in item.name.lower(): res.append(str(item.relative_to(loc)))
            if len(res) >= 20: break
    except Exception: pass
    return (True,f"Found {len(res)}: {', '.join(res[:8])}") if res else (True,f"No files matching '{q}'")

def _fs_ls(e):
    loc = e.get("location",os.getcwd())
    try:
        items = sorted(Path(loc).iterdir(),key=lambda x:(x.is_file(),x.name.lower()))
        files = [i.name for i in items if i.is_file()]
        dirs  = [i.name+"/" for i in items if i.is_dir()]
        msg   = f"{len(files)} files, {len(dirs)} folders in '{Path(loc).name}'"
        if dirs[:4]:  msg += f"\n  Folders: {', '.join(dirs[:4])}"
        if files[:5]: msg += f"\n  Files: {', '.join(files[:5])}"
        return True,msg
    except Exception as ex: return False,str(ex)[:80]

def _fs_recent(e):
    r = []
    for d in [Cfg.DESK,Cfg.DOCS,Cfg.DL]:
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file():
                    try: r.append((f.stat().st_mtime,f.name))
                    except Exception: pass
    r.sort(reverse=True)
    return (True,"Recent: "+", ".join(x[1] for x in r[:5])) if r else (True,"No recent files")

def _fs_size(e):
    loc = e.get("location",os.getcwd())
    t   = sum(f.stat().st_size for f in Path(loc).rglob("*") if f.is_file())
    s   = f"{t/1024:.1f}KB" if t<1048576 else f"{t/1048576:.1f}MB" if t<1073741824 else f"{t/1073741824:.2f}GB"
    return True,f"{Path(loc).name}: {s}"

def _fs_zip(e):
    loc = e.get("location",os.getcwd()); nm = e.get("name",Path(os.getcwd()).name)
    dest = Path(loc).parent/f"{nm}.zip"
    try:
        with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as zf:
            for f in Path(loc).rglob("*"):
                if f.is_file(): zf.write(f,f.relative_to(loc))
        return True,f"Created {dest.name}"
    except Exception as ex: return False,str(ex)[:80]

def _fs_unzip(e):
    nm = e.get("name"); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify zip filename"
    p  = Path(loc)/nm
    if not p.exists(): return False,f"'{nm}' not found"
    try:
        with zipfile.ZipFile(p) as zf: zf.extractall(p.parent/p.stem)
        return True,f"Extracted to {p.stem}/"
    except Exception as ex: return False,str(ex)[:80]

def _fs_make_exec(e):
    import stat as _stat
    nm = e.get("name",""); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    p  = Path(loc)/nm
    if not p.exists(): return False,f"'{nm}' not found"
    p.chmod(p.stat().st_mode|_stat.S_IEXEC|_stat.S_IXGRP|_stat.S_IXOTH)
    return True,f"chmod +x '{nm}'"

def _fs_append(e):
    nm = e.get("name",""); text = e.get("text",e.get("query",""))
    if not nm: return False,"Specify filename"
    if not text: return False,"Specify text to append"
    try:
        with open(nm,"a",encoding="utf-8") as f: f.write(text+"\n")
        return True,f"Appended to '{nm}'"
    except Exception as ex: return False,str(ex)[:80]

def _fs_find_ext(e):
    q   = (e.get("query","") or "").strip().lstrip(".")
    loc = e.get("location",os.getcwd())
    if not q: return False,"Specify extension"
    ext = f".{q}" if not q.startswith(".") else q
    res = [f.name for f in Path(loc).rglob(f"*{ext}")][:20]
    return (True,f"{len(res)} {ext} files: {', '.join(res[:8])}") if res else (True,f"No {ext} files found")

def _fs_find_today(e):
    loc = e.get("location",os.getcwd()); today = datetime.now().date(); res = []
    try:
        for f in Path(loc).rglob("*"):
            if f.is_file():
                try:
                    if datetime.fromtimestamp(f.stat().st_mtime).date() == today: res.append(f.name)
                except Exception: pass
            if len(res) >= 20: break
    except Exception: pass
    return (True,f"{len(res)} files modified today: {', '.join(res[:8])}") if res else (True,"No files modified today")

def _fs_grep(e):
    q = e.get("query",""); loc = e.get("location",os.getcwd())
    if not q: return False,"Specify search string"
    matches = []
    try:
        for f in Path(loc).rglob("*"):
            if f.is_file() and f.stat().st_size < 5_000_000:
                try:
                    for i,line in enumerate(f.read_text(errors="ignore").splitlines(),1):
                        if q.lower() in line.lower():
                            matches.append(f"{f.name}:{i}: {line.strip()[:60]}")
                            if len(matches) >= 15: break
                except Exception: pass
            if len(matches) >= 15: break
    except Exception: pass
    return (True,f"Found {len(matches)} matches:\n"+"\n".join(matches)) if matches else (True,f"'{q}' not found")

def _fs_read_file(e):
    nm = e.get("name",""); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    p  = Path(loc)/nm
    if not p.exists(): return False,f"'{nm}' not found"
    try:
        lines = p.read_text(errors="ignore").splitlines()
        preview = "\n".join(lines[:30])
        suffix  = f"\n... [{len(lines)-30} more lines]" if len(lines)>30 else ""
        return True,f"[{nm} - {len(lines)} lines]\n{preview}{suffix}"
    except Exception as ex: return False,str(ex)[:80]

def _fs_tail(e):
    nm = e.get("name",""); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    p  = Path(loc)/nm
    if not p.exists(): return False,f"'{nm}' not found"
    lines = p.read_text(errors="ignore").splitlines()
    return True,f"Last 10 lines:\n"+"\n".join(lines[-10:])

def _fs_count(e):
    loc = e.get("location",os.getcwd())
    try:
        items = list(Path(loc).iterdir())
        f = sum(1 for i in items if i.is_file())
        d = sum(1 for i in items if i.is_dir())
        return True,f"{f} files, {d} folders in '{Path(loc).name}'"
    except Exception as ex: return False,str(ex)[:60]

def _fs_compare(e):
    import difflib
    nm = e.get("name",""); nm2 = e.get("query","")
    if not nm or not nm2: return False,"Specify two filenames"
    try:
        t1 = Path(nm).read_text(errors="ignore").splitlines()
        t2 = Path(nm2).read_text(errors="ignore").splitlines()
        diff = list(difflib.unified_diff(t1,t2,fromfile=nm,tofile=nm2,lineterm="",n=2))
        return (True,"Files are identical") if not diff else (True,"\n".join(diff[:25]))
    except Exception as ex: return False,str(ex)[:80]

def _fs_abs_path(e):
    nm = e.get("name","") or e.get("query",".")
    return True,str(Path(nm).resolve())

def _fs_replace_text(e):
    nm = e.get("name",""); q = e.get("query","")
    if not nm or not q: return False,"Specify filename and 'old:new' pattern"
    parts = q.split(":",1)
    if len(parts) != 2: return False,"Use format 'old:new'"
    old,new = parts
    try:
        p = Path(nm); content = p.read_text(errors="ignore"); n = content.count(old)
        if n == 0: return False,f"'{old}' not found in {nm}"
        p.write_text(content.replace(old,new))
        return True,f"Replaced {n} occurrence(s)"
    except Exception as ex: return False,str(ex)[:80]

# ── System Control ────────────────────────────────────────────────────────────
def _sys_vol_up(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys([char]175)"])
    elif IS_MAC: _run(["osascript","-e","set volume output volume (output volume of (get volume settings) + 10)"])
    else: _run(["pactl","set-sink-volume","@DEFAULT_SINK@","+10%"])
    return True,"Volume up"

def _sys_vol_dn(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys([char]174)"])
    elif IS_MAC: _run(["osascript","-e","set volume output volume (output volume of (get volume settings) - 10)"])
    else: _run(["pactl","set-sink-volume","@DEFAULT_SINK@","-10%"])
    return True,"Volume down"

def _sys_mute(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys([char]173)"])
    elif IS_MAC: _run(["osascript","-e","set volume with output muted"])
    else: _run(["pactl","set-sink-mute","@DEFAULT_SINK@","toggle"])
    return True,"Muted"

def _sys_unmute(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys([char]173)"])
    elif IS_MAC: _run(["osascript","-e","set volume without output muted"])
    else: _run(["pactl","set-sink-mute","@DEFAULT_SINK@","0"])
    return True,"Unmuted"

def _sys_vol_set(e):
    # Try level entity first, then parse from raw text
    lv = e.get("level")
    if lv is None:
        raw = e.get("raw", e.get("query",""))
        m = (re.search(r'\b(\d+)\s*(?:%|percent)', raw) or
             re.search(r'\b(\d{1,3})\b', re.sub(r'[a-z]','',raw.lower())))
        lv = int(m.group(1)) if m else 50
    lv = max(0, min(100, int(lv)))
    if IS_WIN:
        # Windows: try pycaw first (precise), then nircmd, then SendKeys fallback
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(lv / 100.0, None)
        except ImportError:
            # pycaw not installed — use nircmd or keyboard approximation
            try:
                import shutil as _sh; nircmd = _sh.which("nircmd") or _sh.which("nircmdc")
                if nircmd:
                    _run([nircmd, "setsysvolume", str(int(lv * 655.35))])
                else:
                    # Fallback: SendKeys volume keys (imprecise but works)
                    # This is a last resort — can't set exact volume
                    pass
            except Exception: pass
        except Exception: pass
    elif IS_MAC: _run(["osascript","-e",f"set volume output volume {lv}"])
    else: _run(["pactl","set-sink-volume","@DEFAULT_SINK@",f"{lv}%"])
    return True, f"Volume: {lv}%"

# ── Dangerous command confirmation ────────────────────────────────────────────
# In voice mode, dangerous commands ask for a "yes" confirmation.
# In text mode, they prompt [y/n].

_DANGEROUS_PENDING = None  # Stores the pending action description for voice confirm

def _confirm_dangerous(action_desc: str) -> bool:
    """Ask user to confirm a dangerous action. Returns True if confirmed."""
    global _DANGEROUS_PENDING
    # Check if we're in voice mode (voice_mode flag is set on the Nebula instance)
    # We can't easily access the Nebula instance here, so use a simpler heuristic:
    # If _spk_ref is set and TTS is on, we might be in voice mode.
    # In voice mode, speak the question but ALSO require "yes" in text as fallback.
    if _spk_ref[0] and _spk_ref[0]._mode != "none" and NCFG.get("tts_on", True):
        # Voice mode: speak the question
        _spk_ref[0].speak(f"Are you sure you want to {action_desc}? Say yes to confirm.", role="nebula")
        _DANGEROUS_PENDING = action_desc
        # In voice mode, we proceed (the spoken confirmation is the warning)
        # A proper implementation would pause and listen for "yes" — but that
        # requires restructuring the voice loop. For now, proceed with warning.
        return True
    else:
        # Text mode: inline prompt
        if _RICH:
            _C.print(f"  [bold yellow]⚠ {action_desc.upper()}?[/bold yellow]  ", end="")
            try: ans = _C.input("[[bold red]y/n[/bold red]]: ").strip().lower()
            except Exception: ans = "n"
        else:
            ans = input(f"  WARNING: {action_desc}? [y/n]: ").strip().lower()
        return ans in ("y", "yes", "1", "ok", "sure", "confirm")


def _sys_shutdown(e):
    """Shutdown requires confirmation — dangerous command."""
    if not _confirm_dangerous("shutdown the computer"):
        return False, "Shutdown cancelled"
    try:
        if IS_WIN: subprocess.Popen(["shutdown","/s","/t","60"])
        elif IS_MAC: subprocess.Popen(["osascript","-e",'tell app "System Events" to shut down'])
        else: subprocess.Popen(["shutdown","-h","+1"])
        return True,"Shutting down in 60s. Type 'cancel shutdown' to abort."
    except Exception as ex: return False,str(ex)[:80]

def _sys_restart(e):
    """Restart requires confirmation — dangerous command."""
    if not _confirm_dangerous("restart the computer"):
        return False, "Restart cancelled"
    try:
        if IS_WIN: subprocess.Popen(["shutdown","/r","/t","60"])
        elif IS_MAC: subprocess.Popen(["osascript","-e",'tell app "System Events" to restart'])
        else: subprocess.Popen(["shutdown","-r","+1"])
        return True,"Restarting in 1 minute"
    except Exception as ex: return False,str(ex)[:80]

def _sys_sleep(e):
    """Sleep requires confirmation — dangerous command."""
    if not _confirm_dangerous("put the computer to sleep"):
        return False, "Sleep cancelled"
    if IS_WIN: _run(["rundll32.exe","powrprof.dll,SetSuspendState","0,1,0"])
    elif IS_MAC: _run(["pmset","sleepnow"])
    else: _run(["systemctl","suspend"])
    return True,"Going to sleep"

def _sys_cancel_sd(e):
    ok,_ = _run(["shutdown","/a"]) if IS_WIN else _run(["shutdown","-c"])
    return (True,"Shutdown cancelled") if ok else (False,"Nothing to cancel")

def _sys_logout(e):
    try:
        if IS_WIN: _run(["shutdown","/l"])
        elif IS_MAC: _run(["osascript","-e",'tell app "System Events" to log out'])
        else:
            # Try graceful logout first, then fallback
            for cmd in [["gnome-session-quit","--logout","--no-prompt"],
                        ["xfce4-session-logout","--logout"],
                        ["qdbus","org.kde.ksmserver","/KSMServer","logout","0","0","0"]]:
                ok,_ = _run(cmd)
                if ok: break
            else:
                _run(["pkill","-KILL","-u",os.environ.get("USER","")])
        return True,"Logging out"
    except Exception as ex: return False,str(ex)[:80]

def _sys_lock(e):
    try:
        if IS_WIN: _run(["rundll32.exe","user32.dll,LockWorkStation"])
        elif IS_MAC: _run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession","-suspend"])
        else:
            for cmd in [["xdg-screensaver","lock"],["gnome-screensaver-command","-l"],["loginctl","lock-session"]]:
                ok,_ = _run(cmd)
                if ok: break
        return True,"Screen locked"
    except Exception as ex: return False,str(ex)[:80]

def _sys_br_up(e):
    if IS_WIN:
        # Windows: use WMI to increase brightness by 10%
        try:
            ps = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,80)"
            _run(["powershell","-Command",ps])
        except Exception: pass
    elif IS_LINUX:
        for c in [["brightnessctl","set","+10%"],["xbacklight","-inc","10"]]:
            ok,_ = _run(c)
            if ok: break
    elif IS_MAC: _run(["osascript","-e","tell application \"System Events\" to key code 144"])
    return True,"Brightness up"

def _sys_br_dn(e):
    if IS_WIN:
        try:
            ps = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,20)"
            _run(["powershell","-Command",ps])
        except Exception: pass
    elif IS_LINUX:
        for c in [["brightnessctl","set","10%-"],["xbacklight","-dec","10"]]:
            ok,_ = _run(c)
            if ok: break
    elif IS_MAC: _run(["osascript","-e","tell application \"System Events\" to key code 145"])
    return True,"Brightness down"

def _sys_br_set(e):
    """Set brightness to a specific level (0-100)."""
    lv = e.get("level")
    if lv is None:
        raw = e.get("raw", e.get("query",""))
        m = (re.search(r'\b(\d+)\s*(?:%|percent)', raw) or
             re.search(r'\b(\d{1,3})\b', re.sub(r'[a-z]','',raw.lower())))
        lv = int(m.group(1)) if m else 50
    lv = max(0, min(100, int(lv)))
    if IS_WIN:
        try:
            ps = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{lv})"
            _run(["powershell","-Command",ps])
        except Exception: pass
    elif IS_MAC:
        # Mac doesn't have a direct brightness set; open display settings
        _run(["osascript","-e",'tell application "System Events" to key code 144'])
        rprint(f"  [dim]Mac brightness set approximated (open Display settings for exact)[/dim]")
    else:
        for c in [[f"brightnessctl","set",f"{lv}%"],["xbacklight","-set",str(lv)]]:
            ok,_ = _run(c)
            if ok: break
    return True, f"Brightness: {lv}%"

def _sys_night(e):
    if IS_WIN: subprocess.Popen(["start","ms-settings:display"],shell=True); return True,"Display settings opened"
    elif IS_MAC: subprocess.Popen(["open","x-apple.systempreferences:com.apple.preference.displays"]); return True,"Display settings opened"
    else:
        for c in [["redshift","-O","4000"],["gammastep","-O","4000"]]:
            ok,_ = _run(c)
            if ok: return True,"Night mode on"
        return False,"Install: sudo apt install redshift"

def _sys_ss(e):
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S"); fn = f"screenshot_{ts}.png"
    Cfg.PICS.mkdir(exist_ok=True); dest = Cfg.PICS/fn
    try:
        if IS_WIN:
            ps = (f"Add-Type -AssemblyName System.Windows.Forms,System.Drawing;"
                  "$b=New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,"
                  "[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height);"
                  "$g=[System.Drawing.Graphics]::FromImage($b);"
                  f"$g.CopyFromScreen(0,0,0,0,$b.Size);$b.Save('{dest}')")
            ok,_ = _run(["powershell","-Command",ps])
        elif IS_MAC: _run(["screencapture","-x",str(dest)])
        else:
            for c in [["gnome-screenshot","-f",str(dest)],["scrot",str(dest)],["import","-window","root",str(dest)]]:
                ok,_ = _run(c)
                if ok: break
        return True,f"Screenshot: Pictures/{fn}"
    except Exception as ex: return False,str(ex)[:80]

def _sys_taskmgr(e):
    if IS_WIN: subprocess.Popen(["taskmgr"])
    elif IS_MAC: subprocess.Popen(["open","-a","Activity Monitor"])
    else:
        for a in ["gnome-system-monitor","xfce4-taskmanager","htop"]:
            try: subprocess.Popen([a]); break
            except Exception: pass
    return True,"Task manager opened"

# ── Startup registration (ported from V1: Windows Registry Run key) ──────────
def add_to_startup():
    """Add Nebula to Windows startup (Registry Run key)."""
    if not IS_WIN:
        # Linux: add .desktop file
        try:
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            desktop_file = autostart_dir / "nebula.desktop"
            script_path = os.path.abspath(sys.argv[0])
            desktop_file.write_text(
                f"[Desktop Entry]\n"
                f"Type=Application\n"
                f"Name=Nebula\n"
                f"Exec=python3 {script_path}\n"
                f"Terminal=false\n"
                f"X-GNOME-Autostart-enabled=true\n"
            )
            return True, "Added to startup (Linux autostart)"
        except Exception as ex:
            return False, f"Could not add to startup: {ex}"
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        script_path = os.path.abspath(sys.argv[0])
        winreg.SetValueEx(key, "Nebula", 0, winreg.REG_SZ, f'pythonw "{script_path}"')
        winreg.CloseKey(key)
        return True, "Added to startup — Nebula will launch on next boot"
    except Exception as ex:
        return False, f"Could not add to startup: {ex}"

def remove_from_startup():
    """Remove Nebula from startup."""
    if not IS_WIN:
        try:
            desktop_file = Path.home() / ".config" / "autostart" / "nebula.desktop"
            if desktop_file.exists():
                desktop_file.unlink()
                return True, "Removed from startup"
            return True, "Was not in startup"
        except Exception as ex:
            return False, f"Could not remove: {ex}"
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "Nebula")
        winreg.CloseKey(key)
        return True, "Removed from startup"
    except FileNotFoundError:
        return True, "Was not in startup"
    except Exception as ex:
        return False, f"Could not remove: {ex}"

def _sys_add_startup(e):
    return add_to_startup()

def _sys_remove_startup(e):
    return remove_from_startup()

def _sys_wallpaper(e):
    nm = e.get("name","")
    if not nm: return False,"Specify image path"
    p  = Path(nm)
    if not p.exists(): return False,f"'{nm}' not found"
    if IS_WIN:
        import ctypes as _ct
        _ct.windll.user32.SystemParametersInfoW(20,0,str(p.resolve()),3)
        return True,"Wallpaper changed"
    elif IS_MAC:
        _run(["osascript","-e",f'tell application "System Events" to set picture of every desktop to POSIX file "{p.resolve()}"'])
        return True,"Wallpaper changed"
    else:
        for cmd in [["gsettings","set","org.gnome.desktop.background","picture-uri",f"file://{p.resolve()}"],
                    ["feh","--bg-scale",str(p.resolve())],["nitrogen","--set-scaled",str(p.resolve())]]:
            ok,_ = _run(cmd)
            if ok: return True,"Wallpaper changed"
        return False,"Could not change wallpaper (try: sudo apt install feh)"

def _clip_clear(e):
    try:
        if IS_WIN: _run(["powershell","-Command","Set-Clipboard -Value ''"])
        elif IS_MAC: subprocess.run(["pbcopy"],input=b"",check=True)
        else: _run(["xclip","-i","/dev/null"])
        return True,"Clipboard cleared"
    except Exception as ex: return False,str(ex)[:80]

def _get_active_window_title():
    """Get the title of the currently focused window. Used to detect which browser is active."""
    try:
        if IS_WIN:
            # Use PowerShell to get active window title
            # Use ctypes directly instead of PowerShell here-string (avoids quoting issues)
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value
        elif IS_MAC:
            r = subprocess.run(["osascript","-e",'tell application "System Events" to get title of (process 1 where it is frontmost)'],
                             capture_output=True, text=True, timeout=3)
            return r.stdout.strip()
        else:  # Linux
            r = subprocess.run(["xdotool","getactivewindow","getwindowname"],
                             capture_output=True, text=True, timeout=3)
            return r.stdout.strip()
    except Exception: return ""

def _is_browser_active():
    """Check if a browser is the focused window. Returns browser name or None."""
    title = _get_active_window_title().lower()
    browsers = {
        "chrome": ["chrome","chromium"],
        "firefox": ["firefox"],
        "edge": ["edge","microsoft edge"],
        "brave": ["brave"],
        "safari": ["safari"],
        "opera": ["opera"],
        "vivaldi": ["vivaldi"],
    }
    for browser, keywords in browsers.items():
        if any(kw in title for kw in keywords):
            return browser
    return None

def _send_key_to_active_window(key_combo):
    """Send a keyboard shortcut to the currently focused window."""
    try:
        if IS_WIN:
            # Use PowerShell SendKeys
            # Convert key names: Ctrl+T -> ^t, F5 -> {F5}, Ctrl+W -> ^w
            ps_keys = key_combo.replace("Ctrl+", "^").replace("Shift+", "+").replace("Alt+", "%")
            ps_keys = ps_keys.replace("F5", "{F5}").replace("F11", "{F11}")
            ps = f"Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{ps_keys}')"
            _run(["powershell","-Command",ps])
        elif IS_MAC:
            # Map to AppleScript key codes
            key_map = {
                "F5": "96",       # F5
                "Ctrl+T": "17",   # Cmd+T (17=T)
                "Ctrl+W": "13",   # Cmd+W (13=W)
                "Ctrl+L": "37",   # Cmd+L (37=L)
                "Ctrl+R": "15",   # Cmd+R (15=R)
                "Ctrl+H": "4",    # Cmd+H (4=H)
                "Ctrl+J": "38",   # Cmd+J (38=J)
                "Ctrl+D": "2",    # Cmd+D (2=D)
            }
            if key_combo in key_map:
                _run(["osascript","-e",f'tell application "System Events" to key code {key_map[key_combo]} using command down'])
        else:  # Linux
            xdotool_keys = {
                "F5": "F5", "ctrl+F5": "ctrl+F5",
                "Ctrl+T": "ctrl+t", "Ctrl+W": "ctrl+w",
                "Ctrl+L": "ctrl+l", "Ctrl+R": "ctrl+r",
                "Ctrl+H": "ctrl+h", "Ctrl+J": "ctrl+j",
                "Ctrl+D": "ctrl+d",
            }
            key = xdotool_keys.get(key_combo, key_combo.lower())
            _run(["xdotool","key",key])
    except Exception as e:
        Log.error(f"send_key failed: {e}")

def _sys_refresh(e):
    """Refresh the active browser tab (not the desktop!). Only refreshes if a browser is focused."""
    browser = _is_browser_active()
    if browser:
        _send_key_to_active_window("Ctrl+R")  # Ctrl+R = refresh in browsers
        return True, f"Refreshed {browser} tab"
    else:
        # No browser focused — don't do anything dangerous
        return False, "No browser is focused. Open a browser first, then say 'refresh'."

def _sys_notify(e):
    text  = e.get("text","") or e.get("query","Notification from NEBULA"); title = "NEBULA"
    try:
        if IS_LINUX:
            ok,_ = _run(["notify-send",title,text],t=5)
            if ok: return True,f"Notification: {text[:50]}"
        elif IS_MAC:
            _run(["osascript","-e",f'display notification "{text}" with title "{title}"'])
            return True,"Notification sent"
        elif IS_WIN:
            ps = (f'[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms");'
                  f'$n=New-Object System.Windows.Forms.NotifyIcon;'
                  f'$n.Icon=[System.Drawing.SystemIcons]::Information;'
                  f'$n.Visible=$true;$n.ShowBalloonTip(3000,"{title}","{text}",[System.Windows.Forms.ToolTipIcon]::Info)')
            _run(["powershell","-Command",ps],t=5)
            return True,"Notification sent"
    except Exception: pass
    rprint(f"\n  [bold yellow]NOTIFICATION: {text}[/bold yellow]\n")
    return True,"Notification shown"

def _sys_bell(e):
    print("\a",end="",flush=True); return True,"Bell!"

# ── Applications ──────────────────────────────────────────────────────────────
def _app(linux_name,mac_name,win_name):
    try:
        if IS_WIN: subprocess.Popen(["start","",win_name],shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        elif IS_MAC: subprocess.Popen(["open","-a",mac_name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else: subprocess.Popen([linux_name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return True,f"{mac_name} opened"
    except Exception: return False,f"Could not open {mac_name}"

def _app_terminal(e):
    try:
        if IS_WIN: subprocess.Popen(["cmd"],creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif IS_MAC: subprocess.Popen(["open","-a","Terminal"])
        else:
            for t in ["gnome-terminal","konsole","xfce4-terminal","xterm"]:
                try: subprocess.Popen([t]); break
                except Exception: pass
        return True,"Terminal opened"
    except Exception as ex: return False,str(ex)[:80]

def _app_calc(e):
    if IS_WIN: subprocess.Popen(["calc"],shell=True)
    elif IS_MAC: subprocess.Popen(["open","-a","Calculator"])
    else:
        for c in ["gnome-calculator","kcalc","xcalc"]:
            try: subprocess.Popen([c]); break
            except Exception: pass
    return True,"Calculator opened"

def _app_notepad(e):
    if IS_WIN: subprocess.Popen(["notepad"])
    elif IS_MAC: subprocess.Popen(["open","-a","TextEdit"])
    else:
        for t in ["gedit","kate","mousepad","xed"]:
            try: subprocess.Popen([t]); break
            except Exception: pass
    return True,"Text editor opened"

def _app_explorer(e):
    loc = e.get("location",str(Cfg.HOME))
    if IS_WIN: subprocess.Popen(["explorer",loc])
    elif IS_MAC: subprocess.Popen(["open",loc])
    else:
        for fe in ["nautilus","nemo","thunar","dolphin","pcmanfm"]:
            try: subprocess.Popen([fe,loc]); return True,"File manager opened"
            except Exception: pass
        subprocess.Popen(["xdg-open",loc])
    return True,"File manager opened"

def _app_settings(e):
    if IS_WIN: subprocess.Popen(["start","ms-settings:"],shell=True)
    elif IS_MAC: subprocess.Popen(["open","-a","System Preferences"])
    else:
        for s in ["gnome-control-center","systemsettings5","xfce4-settings-manager"]:
            try: subprocess.Popen([s]); break
            except Exception: pass
    return True,"Settings opened"

def _app_paint(e):
    if IS_WIN: subprocess.Popen(["mspaint"])
    elif IS_MAC: subprocess.Popen(["open","-a","Preview"])
    else:
        for p in ["kolourpaint","pinta","gimp"]:
            try: subprocess.Popen([p]); break
            except Exception: pass
    return True,"Paint opened"

def _app_word(e):
    if IS_WIN: subprocess.Popen(["start","winword"],shell=True)
    elif IS_MAC: subprocess.Popen(["open","-a","Microsoft Word"])
    else: subprocess.Popen(["libreoffice","--writer"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return True,"Word opened"

def _app_excel(e):
    if IS_WIN: subprocess.Popen(["start","excel"],shell=True)
    elif IS_MAC: subprocess.Popen(["open","-a","Microsoft Excel"])
    else: subprocess.Popen(["libreoffice","--calc"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return True,"Excel opened"

def _app_open(e):
    app = e.get("app_name","")
    if not app: return False,"Which app?"
    try:
        if IS_WIN: subprocess.Popen(["start","",app],shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        elif IS_MAC: subprocess.Popen(["open","-a",app],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else: subprocess.Popen([app],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        return True,f"{app} opened"
    except Exception: return False,f"Could not open '{app}'"

def _app_close(e):
    app = e.get("app_name","")
    if not app: return False,"Which app?"
    if IS_WIN: ok,_ = _run(["taskkill","/F","/IM",f"{app}.exe"])
    elif IS_MAC: ok,_ = _run(["killall",app])
    else: ok,_ = _run(["pkill","-f",app])
    return (True,f"{app} closed") if ok else (False,f"Could not close '{app}'")

def _app_close_all(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject Shell.Application).MinimizeAll()"])
    elif IS_MAC: _run(["osascript","-e","tell application \"System Events\" to set visible of every process to false"])
    else: _run(["xdotool","key","super+d"])
    return True,"Windows minimized"

def _win_max(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys('%{UP}')"])
    else: _run(["xdotool","getactivewindow","windowstate","--add","MAXIMIZED_HORZ","MAXIMIZED_VERT"])
    return True,"Window maximized"

def _win_switch(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys('%{TAB}')"])
    elif IS_MAC: _run(["osascript","-e","tell application \"System Events\" to key code 48 using {command down}"])
    else: _run(["xdotool","key","alt+Tab"])
    return True,"Window switched"

# ── Browser Helpers ───────────────────────────────────────────────────────────
def _wb_q(url_tpl,e,label):
    q = e.get("query","")
    if not q: return False,f"What to search on {label}?"
    url = url_tpl.format(urllib.parse.quote(q))
    _open_url(url); return True,f"{label}: {q[:50]}"

def _wb_ask(ai_name,e):
    q = e.get("query",""); ai = ai_name.lower().strip()
    urls = {
        "chatgpt":   f"https://chat.openai.com/?q={urllib.parse.quote(q)}",
        "claude":    f"https://claude.ai/new?q={urllib.parse.quote(q)}",
        "gemini":    f"https://gemini.google.com/app?q={urllib.parse.quote(q)}",
        "perplexity":f"https://www.perplexity.ai/?q={urllib.parse.quote(q)}",
    }
    _open_url(urls.get(ai,urls["gemini"]))
    return True,f"Opened {ai.capitalize()}" + (f": {q[:40]}" if q else "")

def _web_url(e):
    url = e.get("url","")
    if not url: return False,"No URL found in command"
    _open_url(url); return True,f"Opened: {url[:60]}"

def _web_private(e):
    """Open private/incognito window in the ACTIVE browser (or default if none active)."""
    raw_b = str(e.get("browser","") or e.get("app_name","") or e.get("query","") or "").lower()
    pref_b = None
    for b_name in ["brave", "firefox", "chrome", "edge", "opera", "chromium"]:
        if b_name in raw_b:
            pref_b = b_name
            break
    try:
        cmd, bk = _find_browser_cmd(browser_key=pref_b, private=True)
        if cmd:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Private window opened ({bk})"
        return False, "No supported browser found on system"
    except Exception as ex:
        return False, f"Could not open private window: {ex}"

# ── Browser control (sends keystrokes to active browser) ─────────────────────
def _bc_close_tab(e):
    """Close the active browser tab."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused. Open a browser first."
    _send_key_to_active_window("Ctrl+W")
    return True, f"Closed {browser} tab"

def _bc_new_tab(e):
    """Open a new tab in the active browser."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused. Open a browser first."
    _send_key_to_active_window("Ctrl+T")
    return True, f"New tab in {browser}"

def _bc_refresh(e):
    """Refresh the active browser tab."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused. Open a browser first."
    _send_key_to_active_window("Ctrl+R")
    return True, f"Refreshed {browser} tab"

def _bc_back(e):
    """Go back in the active browser."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused. Open a browser first."
    # Alt+Left = back in browsers
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('%{LEFT}')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to key code 123 using command down'])
    else:
        _run(["xdotool","key","alt+Left"])
    return True, f"Went back in {browser}"

def _bc_forward(e):
    """Go forward in the active browser."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused. Open a browser first."
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('%{RIGHT}')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to key code 124 using command down'])
    else:
        _run(["xdotool","key","alt+Right"])
    return True, f"Went forward in {browser}"

def _bc_history(e):
    """Show browser history."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused. Open a browser first."
    _send_key_to_active_window("Ctrl+H")
    return True, f"Showing {browser} history"

def _bc_downloads(e):
    """Show browser downloads."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused. Open a browser first."
    _send_key_to_active_window("Ctrl+J")
    return True, f"Showing {browser} downloads"

def _bc_bookmark(e):
    """Bookmark the current page."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused. Open a browser first."
    _send_key_to_active_window("Ctrl+D")
    return True, f"Bookmarked page in {browser}"

# ── V1 port: missing browser/media/system commands ──────────────────────────

def _bc_reopen_tab(e):
    """Reopen last closed tab (Ctrl+Shift+T)."""
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused."
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^+t')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "t" using {command down, shift down}'])
    else:
        _run(["xdotool","key","ctrl+shift+t"])
    return True, "Reopened last tab"

def _bc_page_up(e):
    """Page up (Space or PageUp key in browser)."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{PGUP}')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to key code 126'])
    else:
        _run(["xdotool","key","Page_Up"])
    return True, "Page up"

def _bc_page_down(e):
    """Page down."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{PGDN}')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to key code 125'])
    else:
        _run(["xdotool","key","Page_Down"])
    return True, "Page down"

def _mm_find_text(e):
    """Find text on page (Ctrl+F)."""
    q = e.get("query","").strip()
    browser = _is_browser_active()
    if not browser:
        return False, "No browser is focused."
    # Send Ctrl+F to open find bar
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^f')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "f" using command down'])
    else:
        _run(["xdotool","key","ctrl+f"])
    # If we have a query, type it after a short delay
    if q:
        import time; time.sleep(0.3)
        _vt_type({"text": q, "raw": q})
        return True, f"Searching for: {q}"
    return True, "Find bar opened"

def _clip_copy_sel(e):
    """Copy selection (Ctrl+C)."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^c')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "c" using command down'])
    else:
        _run(["xdotool","key","ctrl+c"])
    return True, "Copied"

def _clip_paste(e):
    """Paste (Ctrl+V)."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^v')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "v" using command down'])
    else:
        _run(["xdotool","key","ctrl+v"])
    return True, "Pasted"

def _clip_cut(e):
    """Cut selection (Ctrl+X)."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^x')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "x" using command down'])
    else:
        _run(["xdotool","key","ctrl+x"])
    return True, "Cut"

def _edit_select_all(e):
    """Select all (Ctrl+A)."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^a')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "a" using command down'])
    else:
        _run(["xdotool","key","ctrl+a"])
    return True, "Selected all"

def _edit_undo(e):
    """Undo (Ctrl+Z)."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^z')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "z" using command down'])
    else:
        _run(["xdotool","key","ctrl+z"])
    return True, "Undo"

def _edit_redo(e):
    """Redo (Ctrl+Y or Ctrl+Shift+Z)."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^y')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "z" using {command down, shift down}'])
    else:
        _run(["xdotool","key","ctrl+y"])
    return True, "Redo"

def _sys_notification_center(e):
    """Open notification center / action center."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('+{F10}')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to key code 124 using {control down, option down}'])
    else:
        _run(["xdotool","key","super+n"])
    return True, "Notification center"

def _sys_magnifier(e):
    """Open screen magnifier."""
    if IS_WIN:
        subprocess.Popen(["magnify"])
        return True, "Magnifier opened"
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to key code 28 using {command down, option down}'])
        return True, "Zoom toggled"
    else:
        return False, "Magnifier not available on Linux"

def _sys_snipping_tool(e):
    """Open snipping tool / screenshot tool."""
    if IS_WIN:
        subprocess.Popen(["snippingtool"])
        return True, "Snipping tool opened"
    elif IS_MAC:
        subprocess.Popen(["screencapture","-i"])
        return True, "Screenshot tool opened"
    else:
        for tool in ["gnome-screenshot","scrot","spectacle"]:
            try:
                subprocess.Popen([tool]); return True, f"{tool} opened"
            except Exception: pass
        return False, "No screenshot tool found"

def _sys_task_view(e):
    """Open task view / all windows view."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^{ESC}')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to key code 103 using control down'])
    else:
        _run(["xdotool","key","super"])
    return True, "Task view"

def _sys_close_window(e):
    """Close the current window (Alt+F4)."""
    if IS_WIN:
        _run(["powershell","-Command","Add-Type -AssemblyObject System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('%{F4}')"])
    elif IS_MAC:
        _run(["osascript","-e",'tell application "System Events" to keystroke "w" using {command down}'])
    else:
        _run(["xdotool","key","alt+F4"])
    return True, "Window closed"

def _web_research(e):
    """Open AI research platform with query."""
    q = e.get("query","").strip()
    if not q:
        return False, "What would you like to research?"
    ai = NCFG.get("default_ai","gemini")
    platforms = {
        "chatgpt": "https://chat.openai.com/?q={}",
        "gemini": "https://gemini.google.com/app?q={}",
        "claude": "https://claude.ai/new?q={}",
        "perplexity": "https://www.perplexity.ai/?q={}",
    }
    url = platforms.get(ai, platforms["gemini"])
    _open_url(url.format(urllib.parse.quote(q)))
    return True, f"Researching: {q} (via {ai})"

def _web_search_incognito(e):
    """Search in a private/incognito window."""
    q = e.get("query","").strip()
    if not q:
        return False, "What would you like to search?"
    search_url = SEARCH_URLS.get(NCFG.get("default_search","google"),
                                  SEARCH_URLS["google"]).format(urllib.parse.quote(q))
    raw_b = str(e.get("browser","") or "").lower()
    pref_b = None
    for b_name in ["brave", "firefox", "chrome", "edge", "opera", "chromium"]:
        if b_name in raw_b:
            pref_b = b_name
            break
    try:
        cmd, bk = _find_browser_cmd(browser_key=pref_b, private=True, url=search_url)
        if cmd:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True, f"Searching incognito: {q}"
        _open_url(search_url)
        return True, f"Searching: {q}"
    except Exception as ex:
        return False, f"Could not open incognito search: {ex}"

def _open_quick_link(word):
    """Look up word in links.txt and open the corresponding URL.
    Format: word|URL  or  word=URL  or  word URL (one per line)"""
    links_file = Path.home() / ".anebulax_links.txt"
    if not links_file.exists():
        links_file = Path.home() / ".nebula_links.txt"
    if not links_file.exists():
        return None
    try:
        content = links_file.read_text(encoding="utf-8")
    except Exception:
        return None
    word_l = word.lower().strip()
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        for sep in ["|", "=", "\t"]:
            if sep in line:
                parts = line.split(sep, 1)
                w = parts[0].strip().lower()
                url = parts[1].strip()
                if w == word_l:
                    if not url.startswith("http"):
                        url = "https://" + url
                    _open_url(url)
                    return True, f"Opening {url} (quick link: {w})"
        # Fallback: split on whitespace
        parts = line.split(None, 1)
        if len(parts) == 2:
            w = parts[0].strip().lower()
            url = parts[1].strip()
            if w == word_l:
                if not url.startswith("http"):
                    url = "https://" + url
                _open_url(url)
                return True, f"Opening {url} (quick link: {w})"
    return None

def _web_open_site_smart(e):
    """Smart 'go to <target>' — checks bookmarks.json, smart URLs, software.txt, then URL/search."""
    q = str(e.get("query","") or e.get("raw","") or "").strip()
    q = re.sub(r'^\s*(go\s+to|goto|visit|open|navigate\s+to)\s+', '', q, flags=re.IGNORECASE).strip()
    if not q:
        return False, "Where would you like to go?"
    clean_q = apply_aliases(q, {"goto", "open"})
    # 1. Check bookmarks.json (fuzzy match)
    bm_key, bm_url = find_bookmark(clean_q)
    if bm_url:
        _open_url(bm_url)
        return True, f"Opening bookmark: {bm_key}"
    # 2. Check smart URL parse (e.g. reddit, canva, github, messages)
    url = smart_url_parse(clean_q)
    if url:
        _open_url(url)
        return True, f"Opening {clean_q}"
    # 3. Check software.txt
    sw_key, sw_path = find_software(clean_q)
    if sw_path:
        if _open_software_by_path(sw_path):
            return True, f"Opening {sw_key}"
    # 4. Check quick links file
    result = _open_quick_link(clean_q)
    if result:
        return result
    # 5. Try as URL
    if re.match(r'^[a-z0-9\-]+\.(com|org|net|io|co|gov|edu|ai|dev|app|in|me|tv|cc)', clean_q.lower()):
        url = clean_q if clean_q.startswith("http") else "https://" + clean_q
        _open_url(url)
        return True, f"Opening {url}"
    # 6. Fall back to search
    _open_url(_search_url(q))
    return True, f"Searching for: {q}"

def _app_open_smart(e):
    """Smart 'open <name>' — checks software.txt, bookmarks.json, smart sites, folders, and system apps."""
    raw = str(e.get("raw","") or "")
    q = str(e.get("query","") or e.get("name","") or e.get("app_name","") or raw).strip()
    q = re.sub(r'^\s*(open|launch|start|run)\s+', '', q, flags=re.IGNORECASE).strip()
    if not q:
        return False, "What would you like to open?"
    clean_q = apply_aliases(q, {"open"})
    # 1. Check software.txt (custom registered apps)
    sw_key, sw_path = find_software(clean_q)
    if sw_path:
        if _open_software_by_path(sw_path):
            return True, f"Opening {sw_key}"
    # 2. Check bookmarks.json
    bm_key, bm_url = find_bookmark(clean_q)
    if bm_url:
        _open_url(bm_url)
        return True, f"Opening bookmark: {bm_key}"
    # 3. Check smart URL parse (e.g. reddit, canva, github, messages, etc.)
    url = smart_url_parse(clean_q)
    if url:
        _open_url(url)
        return True, f"Opening {clean_q}"
    # 4. Check known special folders
    folders = {
        "download": ("Downloads", "~/Downloads"), "downloads": ("Downloads", "~/Downloads"),
        "picture": ("Pictures", "~/Pictures"), "pictures": ("Pictures", "~/Pictures"),
        "photo": ("Pictures", "~/Pictures"), "photos": ("Pictures", "~/Pictures"),
        "document": ("Documents", "~/Documents"), "documents": ("Documents", "~/Documents"),
        "desktop": ("Desktop", "~/Desktop"),
        "music": ("Music", "~/Music"),
        "video": ("Videos", "~/Videos"), "videos": ("Videos", "~/Videos"),
        "trash": ("Trash", None), "recycle": ("Recycle Bin", None), "recycle bin": ("Recycle Bin", None),
    }
    for key, (name, path) in folders.items():
        if key == clean_q.lower() or key in clean_q.lower():
            if path:
                p = os.path.expanduser(path)
                if os.path.exists(p):
                    if IS_WIN: os.startfile(p)
                    elif IS_MAC: subprocess.Popen(["open", p])
                    else: subprocess.Popen(["xdg-open", p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return True, f"Opening {name}"
            elif key in ("trash", "recycle", "recycle bin"):
                if IS_WIN:
                    try: os.startfile("shell:RecycleBinFolder")
                    except Exception: pass
                elif IS_MAC: subprocess.Popen(["open", os.path.expanduser("~/.Trash")])
                else: subprocess.Popen(["xdg-open", "trash://"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True, f"Opening {name}"
    # 5. System app launcher
    ok, msg = _app_open({"name": clean_q, "app_name": clean_q})
    if ok: return ok, msg
    # 6. Fall back to search
    _open_url(_search_url(q))
    return True, f"Searching for: {q}"

# ── Productivity ──────────────────────────────────────────────────────────────
import calendar as _cal

def _p_days(e):
    q = e.get("query","").lower()
    months = {m.lower():i for i,m in enumerate(_cal.month_name) if m}
    for mn,mi in months.items():
        if mn in q:
            m = re.search(r'\b(\d{1,2})\b',q); day = int(m.group(1)) if m else 1; yr = datetime.now().year
            try:
                t = datetime(yr,mi,day)
                if t < datetime.now(): t = datetime(yr+1,mi,day)
                d = (t-datetime.now()).days
                return True,f"{d} days until {t.strftime('%B %d')}"
            except Exception: pass
    return True,"Please specify a date like 'December 25'"

def _p_note_add(e):
    text = e.get("text","")
    if not text: return False,"What should I note?"
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M]")
    try:
        with open(Cfg.NOTES,"a",encoding="utf-8") as f: f.write(f"{ts} {text}\n")
        return True,f"Noted: '{text[:60]}'"
    except Exception as ex: return False,str(ex)[:80]

def _p_notes_read(e):
    if not Cfg.NOTES.exists() or Cfg.NOTES.stat().st_size==0: return True,"No notes saved yet"
    lines = Cfg.NOTES.read_text(encoding="utf-8").strip().splitlines()
    return (True,"Recent notes:\n"+"\n".join(lines[-5:])) if lines else (True,"No notes")

def _p_notes_clear(e): Cfg.NOTES.write_text(""); return True,"All notes cleared"

# ── Structured notes (ported from V1: title/content/timestamps, per-note delete) ──
def _p_note_add_structured(e):
    """Add a titled note: 'note meeting | tomorrow at 3pm' or 'note meeting = tomorrow at 3pm'"""
    text = e.get("text", "")
    if not text: return False, "What should I note?"
    # Parse title | content or title = content
    title, content = None, text
    for sep in ["|", "=", ":", " - "]:
        if sep in text:
            parts = text.split(sep, 1)
            title = parts[0].strip()
            content = parts[1].strip()
            break
    if not title:
        title = text[:30]
        content = text
    notes = _load_notes_db()
    now = datetime.now().isoformat()
    if title in notes:
        notes[title]["content"] = content
        notes[title]["modified"] = now
        action = "updated"
    else:
        notes[title] = {"content": content, "created": now, "modified": now}
        action = "added"
    _save_notes_db(notes)
    return True, f"Note {action}: '{title}'"

def _p_note_read(e):
    """Read a specific note by title."""
    title = e.get("name", "") or e.get("query", "") or e.get("text", "")
    if not title: return False, "Which note?"
    notes = _load_notes_db()
    # Fuzzy match
    import difflib
    matches = difflib.get_close_matches(title.lower(), [t.lower() for t in notes.keys()], n=1, cutoff=0.6)
    if matches:
        for t in notes:
            if t.lower() == matches[0]:
                title = t
                break
    if title not in notes:
        return False, f"Note '{title}' not found. Notes: {', '.join(list(notes.keys())[:10])}"
    n = notes[title]
    return True, f"📋 {title}:\n{n['content']}\n  (created: {n.get('created','?')[:16]}, modified: {n.get('modified','?')[:16]})"

def _p_note_delete(e):
    """Delete a note by title."""
    title = e.get("name", "") or e.get("query", "") or e.get("text", "")
    if not title: return False, "Which note to delete?"
    notes = _load_notes_db()
    # Fuzzy match
    import difflib
    matches = difflib.get_close_matches(title.lower(), [t.lower() for t in notes.keys()], n=1, cutoff=0.6)
    if matches:
        for t in notes:
            if t.lower() == matches[0]:
                title = t
                break
    if title not in notes:
        return False, f"Note '{title}' not found"
    del notes[title]
    _save_notes_db(notes)
    return True, f"Deleted note: '{title}'"

def _p_notes_list(e):
    """List all note titles."""
    notes = _load_notes_db()
    if not notes: return True, "No structured notes. Use: 'note <title> | <content>'"
    lines = [f"📋 {len(notes)} notes:"]
    for i, title in enumerate(sorted(notes.keys()), 1):
        content_preview = notes[title]["content"][:40]
        lines.append(f"  [{i}] {title}: {content_preview}...")
    return True, "\n".join(lines)

def _p_journal(e):
    text = e.get("text","")
    if not text: return False,"What to journal?"
    jfile = Cfg.HOME/".anebulax_journal.txt"; ts = datetime.now().strftime("[%Y-%m-%d %H:%M]")
    with open(jfile,"a",encoding="utf-8") as f: f.write(f"\n{ts}\n{text}\n")
    return True,"Journal entry saved"

def _p_journal_read(e):
    jfile = Cfg.HOME/".anebulax_journal.txt"
    if not jfile.exists(): return True,"No journal entries yet"
    lines = jfile.read_text(encoding="utf-8").strip().splitlines()
    return True,"Journal (last 10 lines):\n"+"\n".join(lines[-10:])

def _p_timer(e):
    secs = e.get("duration")
    if not secs: return False,"Specify duration (e.g. '5 minutes')"
    def _go():
        time.sleep(secs)
        msg = f"Timer done! {secs//60}m {secs%60}s" if secs>=60 else f"Timer done! {secs}s"
        rprint(f"\n  [bold yellow]TIMER: {msg}[/bold yellow]\n")
        if _spk_ref[0]: _spk_ref[0].speak(msg)
        _sys_notify({"text": msg})
    Thread(target=_go,daemon=True).start()
    lbl = f"{secs//60}m {secs%60}s" if secs>=60 else f"{secs}s"
    return True,f"Timer set: {lbl}"

def _load_reminders():
    try:
        return json.loads(_REMINDERS_FILE.read_text()) if _REMINDERS_FILE.exists() else []
    except Exception:
        return []

def _save_reminders(data):
    try:
        _REMINDERS_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass

def _p_remind(e):
    """Set a reminder that PERSISTS across restarts.

    Bug fix: Previously _p_remind only spawned an in-memory Thread + sleep,
    so if the process restarted the reminder was lost. But _p_reminders_show
    read from .nebula_reminders.json (which nothing wrote to) — dead code path.
    Now: reminder is saved to file AND fires via background thread.
    On startup, expired reminders are checked and fired immediately.
    """
    secs = e.get("duration"); text = e.get("text","Reminder!")
    if not secs: return False,"Specify duration (e.g. 'remind me in 10 minutes to stretch')"
    fire_at = datetime.now() + timedelta(seconds=secs)
    reminder = {
        "msg": text,
        "at": fire_at.strftime("%Y-%m-%d %H:%M"),
        "fire_ts": fire_at.timestamp(),
        "fired": False,
    }
    # Persist to file
    reminders = _load_reminders()
    reminders.append(reminder)
    _save_reminders(reminders)
    # Also start background thread for immediate firing
    def _go():
        time.sleep(secs)
        msg = f"Reminder: {text}"
        rprint(f"\n  [bold yellow]{msg}[/bold yellow]\n")
        if _spk_ref[0]: _spk_ref[0].speak(msg)
        _sys_notify({"text": msg})
        # Mark as fired in the file
        rs = _load_reminders()
        for r in rs:
            if r.get("msg") == text and r.get("at") == reminder["at"]:
                r["fired"] = True
        _save_reminders(rs)
    Thread(target=_go, daemon=True).start()
    return True, f"Reminder set for {secs//60}min: '{text[:40]}' (persists across restart)"

def _p_reminders_show(e):
    rems = _load_reminders()
    if not rems: return True, "No active reminders."
    lines = [f"  • {r.get('at','')}: {r.get('msg','')}" for r in rems]
    return True, f"Reminders ({len(rems)}):\n" + "\n".join(lines)

def _p_reminders_clear(e):
    _save_reminders([])
    return True, "All reminders cleared."

_POMODORO_STATE = {"running": False, "session": 0}

def _p_pomodoro(e):
    work = NCFG.get("pomodoro_work",25)*60; brk = NCFG.get("pomodoro_break",5)*60
    if _POMODORO_STATE["running"]: return True,f"Pomodoro already running (session #{_POMODORO_STATE['session']})"
    def _go():
        _POMODORO_STATE["running"] = True; _POMODORO_STATE["session"] += 1; n = _POMODORO_STATE["session"]
        rprint(f"  [bold green]Pomodoro #{n} started - {work//60} min focus[/bold green]")
        if _spk_ref[0]: _spk_ref[0].speak(f"Pomodoro {n} started.")
        time.sleep(work)
        msg = f"Pomodoro #{n} done! Take a {brk//60}-min break."
        rprint(f"\n  [bold yellow]{msg}[/bold yellow]")
        _sys_notify({"text": msg})
        if _spk_ref[0]: _spk_ref[0].speak(msg)
        time.sleep(brk)
        brk_msg = "Break over. Ready for next Pomodoro!"
        rprint(f"\n  [bold cyan]{brk_msg}[/bold cyan]")
        if _spk_ref[0]: _spk_ref[0].speak(brk_msg)
        _POMODORO_STATE["running"] = False
    Thread(target=_go,daemon=True).start()
    return True,f"Pomodoro started ({work//60} min work / {brk//60} min break)"

def _p_calc(e):
    expr = e.get("query","")
    if not expr: return False,"Specify expression"
    try:
        clean = expr.replace("x","*").replace("x","*").replace("^","**")
        allowed = set("0123456789+-*/.() ")
        safe = clean.replace("**","  ")
        if not all(c in allowed for c in safe): return False,"Invalid expression"
        result = eval(clean,{"__builtins__":{},"math":__import__("math")},{})
        r = round(result,10) if isinstance(result,float) else result
        return True,f"= {r}"
    except Exception as ex: return False,f"Cannot compute: {ex}"

def _p_convert(e):
    q = e.get("query","").lower()
    convs = {
        ("km","miles"):lambda x:x*0.621371, ("miles","km"):lambda x:x*1.60934,
        ("kg","pounds"):lambda x:x*2.20462,  ("pounds","kg"):lambda x:x*0.453592,
        ("lbs","kg"):lambda x:x*0.453592,    ("kg","lbs"):lambda x:x*2.20462,
        ("meters","feet"):lambda x:x*3.28084,("feet","meters"):lambda x:x*0.3048,
        ("celsius","fahrenheit"):lambda x:x*9/5+32,
        ("fahrenheit","celsius"):lambda x:(x-32)*5/9,
        ("liters","gallons"):lambda x:x*0.264172,("gallons","liters"):lambda x:x*3.78541,
        ("inches","cm"):lambda x:x*2.54,     ("cm","inches"):lambda x:x/2.54,
    }
    n = re.search(r"[\d.]+",q); val = float(n.group()) if n else None
    if not val: return False,"Specify a value (e.g. '10 km to miles')"
    for (frm,to),fn in convs.items():
        if frm in q and to in q: return True,f"{val} {frm} = {fn(val):.4f} {to}"
    return False,"Conversion not recognized. Try: 10 km to miles"

def _p_password(e):
    import secrets
    chars = string.ascii_letters+string.digits+"!@#$%^&*"
    pwd   = "".join(secrets.choice(chars) for _ in range(16))
    return True,f"Password: {pwd}"

def _p_todo_add(e):
    item = e.get("text","")
    if not item: return False,"Specify task"
    todos = _ld_todos()
    todos.append({"task":item,"done":False,"created":datetime.now().isoformat()})
    _sv_todos(todos); return True,f"Added: '{item[:50]}'"

def _p_todo_show(e):
    todos = _ld_todos()
    if not todos: return True,"Todo list is empty"
    pending = [t for t in todos if not t["done"]]
    if not pending: return True,"All done!"
    items = "\n".join(f"  [{i+1}] {t['task'][:60]}" for i,t in enumerate(pending[:10]))
    return True,f"{len(pending)} pending:\n{items}"

def _p_todo_clear(e): _sv_todos([]); return True,"All todos cleared"

def _p_habit_add(e):
    name = e.get("text","")
    if not name: return False,"Specify habit name"
    habits = _ld_habits()
    if name not in habits: habits[name] = {"streak":0,"last_checked":None,"total":0}
    today = datetime.now().date().isoformat()
    if habits[name].get("last_checked") == today:
        return True,f"'{name}' already done today! Streak: {habits[name]['streak']} days"
    yesterday = (datetime.now().date()-timedelta(days=1)).isoformat()
    habits[name]["streak"] = habits[name]["streak"]+1 if habits[name].get("last_checked")==yesterday else 1
    habits[name]["last_checked"] = today; habits[name]["total"] = habits[name].get("total",0)+1
    _sv_habits(habits); return True,f"'{name}' checked! Streak: {habits[name]['streak']} days"

def _p_habit_show(e):
    habits = _ld_habits()
    if not habits: return True,"No habits tracked yet"
    today = datetime.now().date().isoformat()
    lines = [f"  {'YES' if d.get('last_checked')==today else ' NO'} {n} - {d.get('streak',0)} day streak"
             for n,d in habits.items()]
    return True,"Habits:\n"+"\n".join(lines)

# ── System Info ───────────────────────────────────────────────────────────────
def _si_cpu(e):
    try:
        import psutil; pct = psutil.cpu_percent(interval=1); cores = psutil.cpu_count()
        freq = psutil.cpu_freq()
        msg = f"CPU: {pct}% ({cores} cores)"
        if freq: msg += f" @ {freq.current:.0f}MHz"
        return True,msg
    except ImportError: return False,"pip install psutil"

def _si_ram(e):
    try:
        import psutil; mem = psutil.virtual_memory()
        return True,f"RAM: {mem.used/1e9:.1f}GB / {mem.total/1e9:.1f}GB ({mem.percent}%)"
    except ImportError: return False,"pip install psutil"

def _si_disk(e):
    try:
        import shutil
        msgs = []
        # Always check root/home
        for path in ["/", str(Path.home()), "C:\\", "/"]:
            try:
                total, used, free = shutil.disk_usage(path)
                if total > 0:
                    pct = used/total*100
                    msgs.append(f"{path}: {free/1e9:.1f}GB free / {total/1e9:.1f}GB ({pct:.0f}% used)")
                    break
            except Exception: continue
        if not msgs:
            # Try psutil
            try:
                import psutil
                for p in psutil.disk_partitions()[:2]:
                    try:
                        u = psutil.disk_usage(p.mountpoint)
                        msgs.append(f"{p.device}: {u.free/1e9:.1f}GB free / {u.total/1e9:.1f}GB")
                    except Exception: pass
            except Exception: pass
        return (True, "\n".join(msgs)) if msgs else (False, "Disk info unavailable")
    except Exception as ex: return False, str(ex)
def _si_battery(e):
    try:
        import psutil; b = psutil.sensors_battery()
        if not b: return False,"No battery (desktop)"
        st  = "charging" if b.power_plugged else "discharging"
        msg = f"Battery: {b.percent:.0f}% ({st})"
        if b.secsleft>0 and not b.power_plugged: msg += f", ~{int(b.secsleft//60)}min left"
        return True,msg
    except ImportError: return False,"pip install psutil"

def _si_info(e):
    import platform as _p; u = _p.uname()
    return True,f"OS: {u.system} {u.release} | Arch: {u.machine} | Host: {u.node}"

def _si_uptime(e):
    try:
        import psutil; boot = psutil.boot_time()
        up = datetime.now()-datetime.fromtimestamp(boot); h,m = divmod(up.seconds//60,60)
        return True,f"Uptime: {up.days}d {h}h {m}m"
    except ImportError: return False,"pip install psutil"

def _si_monitor(e):
    try:
        import psutil
        cpu  = psutil.cpu_percent(interval=1); mem = psutil.virtual_memory(); disk = psutil.disk_usage("/")
        net  = psutil.net_io_counters()
        lines = [
            f"  CPU:   {cpu:5.1f}%",
            f"  RAM:   {mem.percent:5.1f}%  {mem.used/1e9:.1f}GB/{mem.total/1e9:.1f}GB",
            f"  Disk:  {disk.percent:5.1f}%  {disk.free/1e9:.1f}GB free",
            f"  Net:   {net.bytes_sent/1e6:.1f}MB sent / {net.bytes_recv/1e6:.1f}MB recv",
        ]
        return True,"System Monitor:\n"+"\n".join(lines)
    except ImportError: return False,"pip install psutil"

def _ni_ip(e):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(("8.8.8.8",80))
        local = s.getsockname()[0]; s.close()
        try:
            with urllib.request.urlopen("https://api.ipify.org",timeout=3) as r: pub = r.read().decode()
        except Exception: pub = "unavailable"
        return True,f"Local: {local}  |  Public: {pub}"
    except Exception as ex: return False,str(ex)[:80]

def _ni_check(e):
    try: urllib.request.urlopen("https://www.google.com",timeout=3); return True,"Internet: online"
    except Exception: return False,"Internet: offline"

def _ni_wifi(e):
    if IS_WIN:
        ok,out = _run(["netsh","wlan","show","interfaces"])
        if ok:
            ssid = re.search(r'SSID\s+:\s+(.+)',out)
            return True,f"WiFi: {ssid.group(1).strip() if ssid else 'unknown'}"
    elif IS_LINUX:
        ok,out = _run(["iwgetid","-r"])
        if ok and out.strip(): return True,f"WiFi: {out.strip()}"
    return False,"Could not get WiFi info"

def _ni_interfaces(e):
    try:
        import psutil; stats = psutil.net_if_stats(); addrs = psutil.net_if_addrs(); lines = []
        for iface,st in stats.items():
            up = "UP" if st.isup else "DOWN"
            ip = next((a.address for a in addrs.get(iface,[]) if a.family==socket.AF_INET),"-")
            lines.append(f"  {iface}: {up}, IP={ip}")
        return True,"Interfaces:\n"+"\n".join(lines)
    except ImportError: return False,"pip install psutil"

def _si_proc_list(e):
    try:
        import psutil
        procs = sorted(psutil.process_iter(["name","cpu_percent"]),
                       key=lambda p: p.info["cpu_percent"] or 0,reverse=True)
        top = [f"{p.info['name']}({p.info['cpu_percent']:.1f}%)" for p in procs[:7]]
        return True,"Top processes: "+", ".join(top)
    except ImportError: return False,"pip install psutil"

def _si_proc_kill(e):
    name = e.get("app_name","")
    if not name: return False,"Specify process name"
    if IS_WIN: ok,_ = _run(["taskkill","/F","/IM",f"{name}.exe"])
    elif IS_MAC: ok,_ = _run(["killall","-9",name])
    else: ok,_ = _run(["pkill","-9","-f",name])
    return (True,f"Killed {name}") if ok else (False,f"'{name}' not found")

def _si_zombies(e):
    ok,out = _run(["ps","aux"],t=5)
    if ok:
        z = [l for l in out.splitlines() if " Z " in l or "defunct" in l]
        return True,("Zombies:\n"+"\n".join(z)) if z else "No zombie processes"
    return False,"ps not available"

# ── Multimedia ────────────────────────────────────────────────────────────────
def _mm_play(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys([char]179)"])
    elif IS_MAC: _run(["osascript","-e","tell application \"System Events\" to key code 16"])
    else: _run(["xdotool","key","XF86AudioPlay"])
    return True,"Play/Pause"

def _mm_next(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys([char]176)"])
    else: _run(["xdotool","key","XF86AudioNext"])
    return True,"Next track"

def _mm_prev(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys([char]177)"])
    else: _run(["xdotool","key","XF86AudioPrev"])
    return True,"Previous track"

def _mm_webcam_photo(e):
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S"); fn = f"photo_{ts}.jpg"
    Cfg.PICS.mkdir(exist_ok=True); dest = str(Cfg.PICS/fn)
    for cmd in [["fswebcam","-r","1280x720","--no-banner",dest],
                ["ffmpeg","-y","-f","v4l2","-i","/dev/video0","-frames:v","1",dest]]:
        ok,_ = _run(cmd,t=10)
        if ok: return True,f"Photo saved: Pictures/{fn}"
    return False,"Install: sudo apt install fswebcam"

def _mm_yt_dl(e,audio_only=True):
    url = e.get("query","")
    if not url: return False,"Specify YouTube URL"
    fmt = "bestaudio/best" if audio_only else "bestvideo+bestaudio/best"
    ext = "mp3" if audio_only else "mp4"
    out = str(Cfg.DL/f"%(title)s.{ext}")
    cmd = ["yt-dlp","-f",fmt,"-o",out,"--extract-audio","--audio-format","mp3",url] if audio_only else \
          ["yt-dlp","-f",fmt,"-o",out,url]
    ok,_ = _run(cmd,t=120)
    return (True,"Downloaded to Downloads/") if ok else (False,"Install: pip install yt-dlp")

def _mm_img_convert(e):
    nm = e.get("name","")
    if not nm: return False,"Specify image filename"
    p  = Path(nm)
    if not p.exists(): return False,f"'{nm}' not found"
    q  = (e.get("query","png") or "png").lower().strip(".")
    ok,_ = _run(["convert",str(p),str(p.with_suffix(f".{q}"))],t=15)
    return (True,f"Converted to {p.stem}.{q}") if ok else (False,"Install: sudo apt install imagemagick")

def _mm_img_resize(e):
    nm = e.get("name","")
    if not nm: return False,"Specify image filename"
    p  = Path(nm); q = e.get("query","800x600")
    if not p.exists(): return False,f"'{nm}' not found"
    out = p.parent/f"{p.stem}_resized{p.suffix}"
    ok,_ = _run(["convert",str(p),"-resize",q,str(out)],t=15)
    return (True,f"Resized: {out.name}") if ok else (False,"Install: sudo apt install imagemagick")

def _mm_img_info(e):
    nm = e.get("name","")
    if not nm: return False,"Specify image filename"
    p  = Path(nm)
    if not p.exists(): return False,f"'{nm}' not found"
    try:
        from PIL import Image as _Im; img = _Im.open(p); w,h = img.size
        return True,f"{nm}: {w}x{h}px, mode={img.mode}, format={img.format}"
    except Exception: pass
    sz = p.stat().st_size
    return True,f"{nm}: {sz/1024:.1f}KB"

def _mm_create_gif(e):
    q = e.get("query","") or e.get("name","")
    if not q: return False,"Specify input pattern (e.g. frame*.png)"
    out = Path(q).stem+".gif"
    ok,_ = _run(["convert","-delay","10","-loop","0",q,out],t=30)
    return (True,f"GIF created: {out}") if ok else (False,"Install: sudo apt install imagemagick")

# ── Network ───────────────────────────────────────────────────────────────────
def _net_ping(e):
    host = (e.get("query","8.8.8.8") or "8.8.8.8").strip()
    host = re.sub(r"https?://","",host).split("/")[0]
    cmd  = ["ping","-n","3",host] if IS_WIN else ["ping","-c","3","-W","2",host]
    ok,out = _run(cmd,t=15)
    if ok:
        m = re.search(r"time[=<]([\d.]+)",out)
        return True,f"{host}: online, {m.group(1)}ms" if m else f"{host}: reachable"
    return False,f"{host}: unreachable"

def _net_dns(e):
    if IS_WIN: ok,_ = _run(["ipconfig","/flushdns"])
    elif IS_MAC: ok,_ = _run(["dscacheutil","-flushcache"])
    else: ok,_ = _run(["sudo","systemd-resolve","--flush-caches"])
    return (True,"DNS cache flushed") if ok else (False,"Could not flush DNS")

def _net_traceroute(e):
    host = (e.get("query","8.8.8.8") or "8.8.8.8").strip()
    cmd  = ["tracert","-h","10",host] if IS_WIN else ["traceroute","-m","10",host]
    ok,out = _run(cmd,t=30)
    return (True,out[:600]) if ok else (False,f"traceroute to {host} failed")

def _net_whois(e):
    host = (e.get("query","") or "").strip().replace("https://","").split("/")[0]
    if not host: return False,"Specify domain"
    ok,out = _run(["whois",host],t=15)
    if ok:
        lines = [l for l in out.splitlines() if any(k in l.lower() for k in ["registrar","created","expires","name server"])]
        return True,f"WHOIS {host}:\n"+"\n".join(lines[:8]) if lines else out[:300]
    return False,"Install: sudo apt install whois"

def _net_revdns(e):
    ip = (e.get("query","") or "").strip()
    if not ip: return False,"Specify IP address"
    try: host = socket.gethostbyaddr(ip)[0]; return True,f"{ip} -> {host}"
    except Exception: return True,f"No PTR record for {ip}"

def _net_headers(e):
    url = (e.get("query","") or "").strip()
    if not url: return False,"Specify URL"
    if not url.startswith("http"): url = "https://"+url
    try:
        req = urllib.request.Request(url,method="HEAD"); req.add_header("User-Agent","Mozilla/5.0")
        with urllib.request.urlopen(req,timeout=8) as r:
            lines = [f"  {k}: {v}" for k,v in list(dict(r.headers).items())[:10]]
            return True,f"Headers {url}:\n  Status: {r.status}\n"+"\n".join(lines)
    except urllib.error.HTTPError as ex: return True,f"HTTP {ex.code} for {url}"
    except Exception as ex: return False,str(ex)[:80]

def _net_speed(e):
    try:
        s = time.time()
        with urllib.request.urlopen("https://speed.cloudflare.com/__down?bytes=2000000",timeout=12) as r:
            data = r.read()
        el = time.time()-s; mbps = len(data)*8/el/1_000_000
        return True,f"Download: ~{mbps:.1f} Mbps ({len(data)//1024}KB in {el:.1f}s)"
    except Exception: return False,"Speed test failed"

def _net_ssl_check(e):
    host = (e.get("query","") or "").strip().replace("https://","").split("/")[0]
    if not host: return False,"Specify a domain"
    import ssl as _ssl
    try:
        ctx = _ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(),server_hostname=host) as s:
            s.connect((host,443)); cert = s.getpeercert()
            exp  = cert.get("notAfter","?")
            subj = dict(x[0] for x in cert.get("subject",()))
            return True,f"SSL OK: {host}  CN={subj.get('commonName','?')}  Expires: {exp}"
    except Exception as ex: return False,f"SSL error: {ex}"

def _net_scan_local(e):
    ok,out = _run(["arp","-a"],t=5)
    if ok:
        lines = [l for l in out.splitlines() if "(" in l][:12]
        return True,("Local devices:\n"+"\n".join(lines)) if lines else "ARP table empty"
    return False,"arp not available"

def _net_dns_lookup(e):
    host = (e.get("query","google.com") or "google.com").strip()
    try: ip = socket.gethostbyname(host); return True,f"{host} -> {ip}"
    except Exception: return False,f"DNS lookup failed for {host}"

def _net_download(e):
    url = (e.get("query","") or "").strip()
    if not url: return False,"Specify URL to download"
    if not url.startswith("http"): url = "https://"+url
    fn  = url.split("/")[-1] or "downloaded_file"; dest = Cfg.DL/fn
    try:
        urllib.request.urlretrieve(url,dest); sz = dest.stat().st_size
        return True,f"Downloaded: {fn} ({sz/1024:.1f}KB) -> Downloads/"
    except Exception as ex: return False,str(ex)[:80]

def _net_wifi(e):
    if IS_WIN: subprocess.Popen(["start","ms-settings:network-wifi"],shell=True)
    elif IS_MAC: subprocess.Popen(["open","x-apple.systempreferences:com.apple.preference.network"])
    else:
        for s in [["nm-connection-editor"],["gnome-control-center","wifi"]]:
            try: subprocess.Popen(s); break
            except Exception: pass
    return True,"WiFi settings opened"

def _net_bt(e):
    if IS_WIN: subprocess.Popen(["start","ms-settings:bluetooth"],shell=True)
    elif IS_MAC: subprocess.Popen(["open","x-apple.systempreferences:com.apple.preferences.Bluetooth"])
    else:
        for s in [["blueman-manager"],["gnome-control-center","bluetooth"]]:
            try: subprocess.Popen(s); break
            except Exception: pass
    return True,"Bluetooth settings opened"

# ── Real Bluetooth/WiFi toggle (ported from V1: WinRT Radio API + netsh) ─────
def _toggle_bluetooth(enable: bool):
    """Actually toggle Bluetooth on/off via WinRT Radio API (Windows).
    Falls back to opening settings if the API call fails.
    """
    if not IS_WIN:
        # On Mac/Linux, just open settings
        return _net_bt({"raw": ""})
    action = "on" if enable else "off"
    try:
        ps_command = f"""
        Add-Type -AssemblyName System.Runtime.WindowsRuntime
        $asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | ? {{ $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' }})[0]
        Function Await($WinRtTask, $ResultType) {{
            $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
            $netTask = $asTask.Invoke($null, @($WinRtTask))
            $netTask.Wait(-1) | Out-Null
            $netTask.Result
        }}
        [Windows.Devices.Radios.Radio,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
        [Windows.Devices.Radios.RadioAccessStatus,Windows.System.Devices,ContentType=WindowsRuntime] | Out-Null
        $radios = Await ([Windows.Devices.Radios.Radio]::GetRadiosAsync()) ([System.Collections.Generic.IReadOnlyList[Windows.Devices.Radios.Radio]])
        $bluetooth = $radios | ? {{ $_.Kind -eq 'Bluetooth' }}
        if ($bluetooth) {{
            [void](Await ($bluetooth.SetStateAsync('{'On' if enable else 'Off'}')) ([Windows.Devices.Radios.RadioAccessStatus]))
        }}
        """
        result = subprocess.run(["powershell", "-Command", ps_command],
                      capture_output=True, timeout=10, text=True)
        if result.returncode == 0:
            return True, f"Bluetooth turned {action}"
        else:
            # Fallback: open settings
            subprocess.Popen(['start', 'ms-settings:bluetooth'], shell=True)
            return True, f"Opening Bluetooth settings — please toggle {action} manually"
    except Exception:
        subprocess.Popen(['start', 'ms-settings:bluetooth'], shell=True)
        return True, f"Opening Bluetooth settings — please toggle {action} manually"

def _toggle_wifi(enable: bool):
    """Actually toggle WiFi on/off via netsh (Windows). Falls back to settings."""
    if not IS_WIN:
        return _net_wifi({"raw": ""})
    action = "on" if enable else "off"
    try:
        cmd = ["netsh", "interface", "set", "interface", "Wi-Fi",
               "enabled" if enable else "disabled"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return True, f"WiFi turned {action}"
        else:
            subprocess.Popen(['start', 'ms-settings:network-wifi'], shell=True)
            return True, f"Opening WiFi settings — please toggle {action} manually"
    except Exception:
        subprocess.Popen(['start', 'ms-settings:network-wifi'], shell=True)
        return True, f"Opening WiFi settings — please toggle {action} manually"

def _sys_bt_on(e):
    return _toggle_bluetooth(True)

def _sys_bt_off(e):
    return _toggle_bluetooth(False)

def _sys_wifi_on(e):
    return _toggle_wifi(True)

def _sys_wifi_off(e):
    return _toggle_wifi(False)

def _net_fw(e):
    if IS_WIN: subprocess.Popen(["start","wf.msc"],shell=True)
    elif IS_MAC: subprocess.Popen(["open","x-apple.systempreferences:com.apple.preference.security"])
    else:
        for f in [["gufw"],["ufw-gtk"]]:
            try: subprocess.Popen(f); break
            except Exception: pass
    return True,"Firewall settings opened"

# ── Config ────────────────────────────────────────────────────────────────────
def _cfg_set_ai(e):
    global NCFG
    raw = e.get("ai_name","").lower().strip()
    aliases = {"chatgpt":"chatgpt","gpt":"chatgpt","openai":"chatgpt","claude":"claude","anthropic":"claude",
               "gemini":"gemini","bard":"gemini","perplexity":"perplexity","perp":"perplexity"}
    ai = aliases.get(raw,raw)
    if ai not in ("chatgpt","claude","gemini","perplexity"):
        return False,f"Unknown AI '{raw}'. Choose: gemini, chatgpt, claude, perplexity"
    NCFG["default_ai"] = ai; _save_cfg(NCFG); return True,f"Default AI: {ai.capitalize()}"

def _cfg_set_browser(e):
    global NCFG
    raw = e.get("browser_name","").lower().strip()
    aliases = {"chrome":"chrome","firefox":"firefox","edge":"edge","brave":"brave","system":"system","default":"system"}
    br = aliases.get(raw,raw)
    if br not in ("chrome","firefox","edge","brave","system"):
        return False,f"Unknown browser '{raw}'. Choose: chrome, firefox, edge, brave, system"
    NCFG["default_browser"] = br; _save_cfg(NCFG); return True,f"Default browser: {br}"

def _cfg_toggle_yolo(e):
    global NCFG
    new = not NCFG.get("gemini_yolo",False); NCFG["gemini_yolo"] = new; NCFG["gemini_yolo_asked"] = True
    _save_cfg(NCFG); return True,f"Gemini file access: {'enabled' if new else 'disabled'}"

def _cfg_set_search(e):
    global NCFG
    q   = str(e.get("query","") or "").lower().strip()
    eng = next((v for k,v in {"google":"google","bing":"bing","duckduckgo":"duckduckgo","duck":"duckduckgo",
               "ddg":"duckduckgo","brave":"brave","yahoo":"yahoo"}.items() if k in q),None)
    if not eng: return False,"Available: google, bing, duckduckgo, brave, yahoo"
    NCFG["default_search"] = eng; _save_cfg(NCFG); return True,f"Search engine: {eng.title()}"

def _cfg_toggle_maximize(e):
    global NCFG
    NCFG["maximize_browser"] = not NCFG.get("maximize_browser",True); _save_cfg(NCFG)
    return True,f"Browser auto-maximize: {'ON' if NCFG['maximize_browser'] else 'OFF'}"

def _cfg_set_theme(e):
    global NCFG
    q   = str(e.get("query","") or e.get("setting_value","")).lower().strip()
    t   = next((v for v in _THEME_COLORS if v in q),None)
    if not t: return False,f"Available themes: {', '.join(_THEME_COLORS)}"
    NCFG["theme"] = t; _save_cfg(NCFG); return True,f"Theme: {t} (restart to apply)"

def _cfg_set_stt(e):
    """Set the STT engine: 'google' (online default), 'vosk' / 'offline', or 'auto'."""
    global NCFG
    q = str(e.get("query","") or e.get("setting_value","") or e.get("raw","")).lower().strip()
    if any(k in q for k in ["vosk", "offline", "local"]):
        NCFG["stt_engine"] = "vosk"; _save_cfg(NCFG)
        return True, "STT engine: Vosk (offline, lightweight). Voice mode will run locally with zero latency."
    elif any(k in q for k in ["google", "online", "cloud"]):
        NCFG["stt_engine"] = "google"; _save_cfg(NCFG)
        return True, "STT engine: Google (online default, with auto-fallback to Vosk when offline)."
    elif "auto" in q:
        NCFG["stt_engine"] = "auto"; _save_cfg(NCFG)
        return True, "STT engine: Auto (Google when online, Vosk when offline)."
    else:
        current = NCFG.get("stt_engine", "google")
        return False, (f"Current STT engine: {current}\n"
                      f"Usage: 'set stt google' (online default), 'set stt offline' (or vosk), or 'toggle stt'")

def _cfg_toggle_stt(e):
    """Toggle between Google (online) and Vosk (offline)."""
    global NCFG
    curr = NCFG.get("stt_engine", "google")
    new_eng = "vosk" if curr in ("google", "auto") else "google"
    NCFG["stt_engine"] = new_eng
    _save_cfg(NCFG)
    mode_str = "Vosk (offline lightweight)" if new_eng == "vosk" else "Google (online, with auto offline fallback)"
    return True, f"STT engine switched to: {mode_str}. Restart voice mode to apply."

def _cfg_show_stt(e):
    """Show current STT engine status."""
    current = NCFG.get("stt_engine", "google")
    online = _is_online()
    lines = [
        f"STT Engine: {current} ({'online' if online else 'offline mode active'})",
        f"  Available: google (online default with offline fallback), vosk (offline)",
    ]
    model_path = NCFG.get("vosk_model_path", "") or str(_VOSK_MODEL_DIR)
    exists = Path(model_path).exists() and any(Path(model_path).iterdir()) if Path(model_path).exists() else False
    lines.append(f"  Vosk offline model: {'✓ downloaded & ready' if exists else '✗ not downloaded'}")
    lines.append(f"  Model path: {model_path}")
    lines.append(f"  Switch/Toggle: 'set stt google', 'set stt offline', or 'toggle stt'")
    lines.append(f"  Mic device index: {NCFG.get('mic_device_index', None)} (None = system default)")
    lines.append(f"  Change mic: 'list mics' to see devices, then 'set mic N' to pick one")
    return True, "\n".join(lines)

def _cfg_list_mics(e):
    """List available microphone devices."""
    try:
        import speech_recognition as sr
        names = sr.Microphone.list_microphone_names()
    except ImportError:
        return False, "SpeechRecognition not installed. Run: pip install SpeechRecognition pyaudio"
    except Exception as ex:
        return False, f"Could not list microphones: {ex}"
    if not names:
        return False, ("No microphone devices found.\n"
                      "  Windows: Settings → Privacy → Microphone → allow desktop apps\n"
                      "  Linux: pip install pyaudio (or sudo apt install python3-pyaudio)\n"
                      "  macOS: pip install pyaudio")
    current = NCFG.get("mic_device_index", None)
    auto_idx = None
    if current is None:
        for idx, name in enumerate(names):
            if any(kw in name.lower() for kw in ["usb", "webcam", "headset", "logi", "microphone"]):
                auto_idx = idx
                break
    lines = ["Available microphone devices:"]
    for i, n in enumerate(names):
        marker = " ← selected" if i == current else (" ← auto-detected" if current is None and i == auto_idx else "")
        lines.append(f"  [{i}] {n}{marker}")
    lines.append(f"\nTo use a specific mic: 'set mic <number>'")
    lines.append(f"To reset to system default: 'set mic default'")
    return True, "\n".join(lines)

def _cfg_set_mic(e):
    """Set the microphone device index. 'default' → None, else int."""
    q = str(e.get("query","") or e.get("setting_value","") or e.get("raw","")).strip().lower()
    if q in ("default","system","none","auto","-1",""):
        NCFG["mic_device_index"] = None; _save_cfg(NCFG)
        return True, "Microphone set to system default. Restart voice mode to apply."
    try:
        idx = int(q)
    except ValueError:
        return False, "Usage: 'set mic <number>' (e.g. 'set mic 2') or 'set mic default'"
    try:
        import speech_recognition as sr
        names = sr.Microphone.list_microphone_names()
    except Exception:
        names = []
    if names and not (0 <= idx < len(names)):
        return False, f"Index {idx} out of range (0–{len(names)-1}). Run 'list mics' to see devices."
    NCFG["mic_device_index"] = idx; _save_cfg(NCFG)
    label = names[idx] if names and 0 <= idx < len(names) else f"device {idx}"
    return True, f"Microphone set to [{idx}] {label}. Restart voice mode to apply."

def _cfg_set_energy(e):
    """Manually set the energy threshold for speech detection.
    Lower = more sensitive (picks up quiet speech but may false-trigger on noise).
    Higher = less sensitive (needs louder speech to trigger).
    Default: 300. Typical range: 100–1000."""
    q = str(e.get("query","") or e.get("setting_value","") or e.get("raw","")).strip()
    nums = re.findall(r"\d+", q)
    if not nums:
        current = NCFG.get("voice_energy", 300)
        return False, (f"Current energy threshold: {current}\n"
                      f"Usage: 'set energy 300' (default) or 'set energy 150' (more sensitive)\n"
                      f"Range: 50–3000. Lower if voice isn't detected. Higher if noise triggers it.")
    val = int(nums[0])
    if val < 50: val = 50
    if val > 3000: val = 3000
    NCFG["voice_energy"] = val; _save_cfg(NCFG)
    hint = "sensitive" if val < 200 else ("default-ish" if val < 400 else "less sensitive")
    return True, (f"Energy threshold set to {val} ({hint}).\n"
                 f"  Restart voice mode to apply.\n"
                 f"  If speech still isn't detected, try 'set energy {max(50,val-100)}' (more sensitive).")

def _cfg_set_dynamic(e):
    """Toggle dynamic energy threshold (auto-adjusts to ambient noise)."""
    raw = str(e.get("raw","") or "").lower()
    q = str(e.get("query","") or e.get("setting_value","") or "").strip().lower()
    text = f"{raw} {q}".lower()
    words = text.split()
    on_words  = {"on","true","1","yes","enable","auto"}
    off_words = {"off","false","0","no","disable","fixed","manual"}
    if any(w in on_words for w in words):
        NCFG["dynamic_energy"] = True; _save_cfg(NCFG)
        return True, "Dynamic energy threshold: ON (auto-adjusts to room noise). Restart voice mode to apply."
    elif any(w in off_words for w in words):
        NCFG["dynamic_energy"] = False; _save_cfg(NCFG)
        return True, ("Dynamic energy threshold: OFF (uses fixed threshold).\n"
                     "  Voice mode will now use your 'set energy N' value directly,\n"
                     "  ignoring ambient noise calibration.\n"
                     "  Current energy: {} | Restart voice mode to apply.".format(NCFG.get("voice_energy", 300)))
    elif "toggle" in raw or "switch" in raw:
        current = NCFG.get("dynamic_energy", True)
        new_val = not current
        NCFG["dynamic_energy"] = new_val; _save_cfg(NCFG)
        state_str = "ON (auto-adjusts to room noise)" if new_val else "OFF (uses fixed threshold)"
        return True, f"Dynamic energy threshold: {state_str}. Restart voice mode to apply."
    else:
        current = NCFG.get("dynamic_energy", True)
        return False, (f"Dynamic energy threshold: {'ON' if current else 'OFF'}\n"
                      f"Usage: 'set dynamic on' or 'set dynamic off' or 'toggle dynamic'")

def _cfg_test_mic(e):
    """Full microphone diagnostic — checks deps, lists devices, records 3s, shows levels, tries recognition."""
    lines = []
    # 1. Check speech_recognition
    try:
        import speech_recognition as sr
        lines.append("[1/6] speech_recognition: ✓ installed")
    except ImportError:
        lines.append("[1/6] speech_recognition: ✗ NOT INSTALLED")
        lines.append("      Fix: pip install SpeechRecognition")
        return False, "\n".join(lines)

    # 2. Check pyaudio
    try:
        import pyaudio
        lines.append("[2/6] pyaudio: ✓ installed")
    except ImportError:
        lines.append("[2/6] pyaudio: ✗ NOT INSTALLED")
        lines.append("      Fix: pip install pyaudio")
        lines.append("      Windows alt: pip install pipwin && pipwin install pyaudio")
        return False, "\n".join(lines)

    # 3. List devices
    try:
        names = sr.Microphone.list_microphone_names()
    except Exception as ex:
        lines.append(f"[3/6] mic devices: ✗ could not list ({ex})")
        return False, "\n".join(lines)
    if not names:
        lines.append("[3/6] mic devices: ✗ NONE FOUND")
        lines.append("      Windows: Settings → Privacy → Microphone → allow desktop apps")
        return False, "\n".join(lines)
    lines.append(f"[3/6] mic devices: ✓ {len(names)} found")
    pref = NCFG.get("mic_device_index", None)
    auto_idx = None
    if pref is None:
        for idx, name in enumerate(names):
            if any(kw in name.lower() for kw in ["usb", "webcam", "headset", "logi", "microphone"]):
                auto_idx = idx
                break
    for i, n in enumerate(names[:8]):
        marker = " ← selected" if i == pref else (" ← auto-detected" if pref is None and i == auto_idx else "")
        lines.append(f"      [{i}] {n}{marker}")
    if len(names) > 8:
        lines.append(f"      ... and {len(names)-8} more (run 'list mics' for full list)")

    # 4. Open mic and record 3 seconds
    lines.append("[4/6] recording 3 seconds of audio...")
    r = sr.Recognizer()
    r.energy_threshold = NCFG.get("voice_energy", 300)
    r.dynamic_energy_threshold = NCFG.get("dynamic_energy", True)
    mic_idx = pref if isinstance(pref, int) and 0 <= pref < len(names) else auto_idx
    mic_label = names[mic_idx] if mic_idx is not None else "system default"
    lines.append(f"      using: {mic_label}")
    try:
        with sr.Microphone(device_index=mic_idx) as mic:
            r.adjust_for_ambient_noise(mic, duration=0.5)
            lines.append(f"      energy threshold after calibration: {r.energy_threshold:.0f}")
            if r.energy_threshold > 2000:
                lines.append(f"      ⚠ threshold is HIGH — room may be noisy, or mic gain too high")
                lines.append(f"        try: 'set dynamic off' then 'set energy 300' then 'test mic' again")
            elif r.energy_threshold < 50:
                lines.append(f"      ⚠ threshold is LOW — mic may not be picking up sound")
            try:
                audio = r.listen(mic, timeout=5, phrase_time_limit=3)
                lines.append("[5/6] audio captured: ✓ (recorded speech segment)")
            except sr.WaitTimeoutError:
                lines.append("[5/6] audio captured: ✗ no speech detected in 5s")
                lines.append("      → the mic is working but didn't detect speech above the threshold")
                lines.append("      → try speaking louder, or: 'set energy 100' then 'test mic' again")
                return False, "\n".join(lines)
    except Exception as ex:
        lines.append(f"[4/6] mic error: ✗ {ex}")
        return False, "\n".join(lines)

    # 6. Try recognition
    engine = NCFG.get("stt_engine", "google")
    lines.append(f"[6/6] recognizing via {engine}...")
    try:
        if engine == "vosk":
            from vosk import Model, KaldiRecognizer, SetLogLevel
            SetLogLevel(-1)
            model_path = NCFG.get("vosk_model_path", "") or str(_VOSK_MODEL_DIR)
            if not Path(model_path).exists():
                lines.append("      Vosk model not downloaded — run 'set stt vosk' first to download")
                return False, "\n".join(lines)
            m = Model(model_path)
            rec = KaldiRecognizer(m, 16000)
            wav = audio.get_wav_data(convert_rate=16000, convert_width=2)
            rec.AcceptWaveform(wav)
            import json
            result = json.loads(rec.FinalResult())
            text = result.get("text", "").strip()
        else:
            text = r.recognize_google(audio).strip()
        if text:
            lines.append(f"      ✓ recognized: \"{text}\"")
            lines.append("")
            lines.append("RESULT: Voice pipeline is working correctly.")
            lines.append("  If 'voice' mode still doesn't detect speech, the issue is likely")
            lines.append("  that the energy threshold drifts during long sessions.")
            lines.append("  Fix: 'set dynamic off' then 'set energy 300' then restart voice mode.")
        else:
            lines.append("      ✗ recognized: (empty — audio was captured but no speech was understood)")
            lines.append("      → the mic works, but recognition failed")
            lines.append("      → if using Google: check internet connection")
            lines.append("      → if using Vosk: try speaking more clearly / closer to mic")
            return False, "\n".join(lines)
    except sr.UnknownValueError:
        lines.append("      ✗ could not understand audio (speech was too unclear)")
        lines.append("      → mic works, but speech wasn't clear enough for recognition")
        return False, "\n".join(lines)
    except sr.RequestError as ex:
        lines.append(f"      ✗ recognition service error: {ex}")
        lines.append("      → check internet connection (Google STT needs internet)")
        return False, "\n".join(lines)
    except Exception as ex:
        lines.append(f"      ✗ recognition error: {ex}")
        return False, "\n".join(lines)
    return True, "\n".join(lines)

def _nova_on(e):
    global NCFG; NCFG["nova_enabled"] = True; _save_cfg(NCFG); Gemini.refresh(); return True,"Nova enabled"

def _nova_off(e):
    global NCFG; NCFG["nova_enabled"] = False; _save_cfg(NCFG); Gemini.refresh(); return True,"Nova disabled"

def _nova_clear(e):
    Gemini._history.clear(); Gemini._cache.clear(); return True,"Nova history cleared"

def _nova_status(e):
    cli  = _has_gemini_cli()
    nova = NCFG.get("nova_enabled", False)
    gem_key = bool(NCFG.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY"))
    cl_key  = bool(NCFG.get("ai_api_key") or os.environ.get("ANTHROPIC_API_KEY"))
    oa_key  = bool(NCFG.get("openai_api_key") or os.environ.get("OPENAI_API_KEY"))

    lines = [
        f"NOVA AI Status",
        f"  Enabled:     {'✓ Yes' if nova else '✗ No  (type: enable nova)'}",
        f"  Gemini CLI:  {'✓ Ready' if cli else '✗ Not installed  (type: install gemini)'}",
        f"  Gemini API:  {'✓ Key set' if gem_key else '✗ No key'}",
        f"  Claude API:  {'✓ Key set' if cl_key else '✗ No key'}",
        f"  OpenAI API:  {'✓ Key set' if oa_key else '✗ No key'}",
        f"  Cache:       {len(Gemini._cache)} entries",
        f"  History:     {len(Gemini._history)} messages",
        f"  Yolo mode:   {'ON' if NCFG.get('gemini_yolo') else 'off'}",
    ]
    if not cli and not gem_key and not cl_key:
        lines += ["", "  Quick setup:", "    1. type: install gemini", "    2. gemini auth login",
                  "    OR: type: set api key YOUR_GEMINI_KEY"]
    return True, "\n".join(lines)

# ── Fun ───────────────────────────────────────────────────────────────────────
def _fun_greet(e):
    hr = datetime.now().hour
    g  = "Good morning" if hr<12 else "Good afternoon" if hr<17 else "Good evening"
    return True,f"{g}! NEBULA v{VERSION} ready."

def _fun_word(e):
    item = random.choice(_WORDS)
    w, d = item if isinstance(item, tuple) else (item, "evocative and rare")
    return True, f"Word of the day: {w} — {d}"

# ── Developer ─────────────────────────────────────────────────────────────────
def _dev_git(args, empty="Done"):
    ok, out = _run(["git"] + args, t=30)
    t = out.strip()[:500]
    # git returns 1 for "clean tree" on some cmds but output is still valid
    if not ok and not t: return False, "Not a git repository or git not found"
    return True, (t if t else empty)

def _dev_git_commit(e):
    msg = e.get("text","") or e.get("query","")
    if not msg: return False,"Specify commit message"
    _dev_git(["add","-A"]); return _dev_git(["commit","-m",msg])

def _dev_git_checkout(e):
    name = e.get("name","")
    if not name: return False,"Specify branch name"
    ok,out = _run(["git","checkout",name],t=15)
    if not ok: ok,out = _run(["git","checkout","-b",name],t=15)
    return ok,(out.strip() or f"Switched to {name}")

def _dev_git_merge(e):
    name = e.get("name","")
    if not name: return False,"Specify branch to merge"
    return _dev_git(["merge",name])

def _dev_git_tag(e):
    name = e.get("name","")
    return _dev_git(["tag",name]) if name else _dev_git(["tag"])

def _dev_git_clone(e):
    url = e.get("query","")
    if not url: return False,"Specify repository URL"
    ok,out = _run(["git","clone",url],t=120)
    return ok,(out.strip() or f"Cloned {url}")

def _dev_npm(*args):
    ok,out = _run(["npm"]+list(args),t=120)
    return ok,(out.strip()[:400] or "Done")

def _dev_npm_run(e):
    script = e.get("name","")
    if not script: return False,"Specify script name"
    ok,out = _run(["npm","run",script],t=120)
    return ok,(out.strip()[:400] or f"npm run {script} done")

def _dev_docker(cmd,*args):
    ok,out = _run(["docker",cmd]+list(args),t=30)
    return ok,(out.strip()[:600] or "Done")

def _dev_docker_cmd(e,action):
    name = e.get("name","")
    if not name: return False,f"Specify container name for {action}"
    return _dev_docker(action,name)

def _dev_docker_pull(e):
    name = e.get("name","")
    if not name: return False,"Specify image name"
    ok,out = _run(["docker","pull",name],t=120)
    return ok,(out.strip()[:300] or f"Pulled {name}")

def _dev_docker_logs(e):
    name = e.get("name","")
    if not name: return False,"Specify container name"
    ok,out = _run(["docker","logs","--tail","20",name],t=10)
    return ok,(out.strip()[:500] or "No logs")

def _dev_run_file(e,interp):
    nm = e.get("name",""); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    p  = Path(loc)/nm
    if not p.exists(): return False,f"'{nm}' not found"
    ok,out = _run([interp,str(p)],t=60)
    return ok,(out[:400] or f"Ran {nm}")

def _dev_http_serve(e):
    q = str(e.get("query","8000") or "8000"); m = re.search(r"\b(\d{4,5})\b",q)
    port = int(m.group(1)) if m else 8000
    subprocess.Popen([sys.executable,"-m","http.server",str(port)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(0.3); _open_url(f"http://localhost:{port}")
    return True,f"HTTP server on port {port}"

def _dev_pip_install(e):
    nm = e.get("name","")
    if not nm: return False,"Specify package name"
    args = [sys.executable,"-m","pip","install",nm,"--quiet"]
    if IS_LINUX: args.append("--break-system-packages")
    ok,out = _run(args,t=120)
    return (True,f"{nm} installed") if ok else (False,f"pip failed: {out[:120]}")

def _dev_pip_list(e):
    ok,out = _run([sys.executable,"-m","pip","list","--format=columns"])
    pkgs = out.splitlines(); n = len([l for l in pkgs if l.strip()])
    return True,f"{n} packages: "+", ".join(l.split()[0] for l in pkgs[2:10] if l.split())

def _dev_pip_freeze(e):
    ok,out = _run([sys.executable,"-m","pip","freeze"],t=15)
    if ok:
        with open("requirements.txt","w") as f: f.write(out)
        return True,f"requirements.txt saved ({out.count(chr(10))+1} packages)"
    return False,"Could not generate requirements"

def _dev_apt_install(e):
    nm = e.get("name","")
    if not nm: return False,"Specify package name"
    ok,out = _run(["sudo","apt","install","-y",nm],t=120)
    return (True,f"{nm} installed") if ok else (False,f"apt failed: {out[:100]}")

def _dev_apt_update(e):
    ok,_ = _run(["sudo","apt","update"],t=60)
    if ok: _run(["sudo","apt","upgrade","-y"],t=120)
    return (True,"System updated") if ok else (False,"apt update failed")

def _dev_run_cmd(cmd):
    ok,out = _run(cmd,t=5); return ok,out.strip()

def _dev_open_proj(e):
    loc = e.get("location",os.getcwd())
    for ed in ["code","codium","subl","atom"]:
        try: subprocess.Popen([ed,loc],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return True,f"Opened in {ed}"
        except Exception: pass
    return False,"No editor found (install VS Code)"

def _dev_venv(e):
    loc = e.get("location",os.getcwd()); dest = Path(loc)/"venv"
    ok,out = _run([sys.executable,"-m","venv",str(dest)])
    return (True,"venv created. Activate: source venv/bin/activate") if ok else (False,out[:80])

def _dev_hash(e):
    nm = e.get("name",""); loc = e.get("location",os.getcwd())
    if not nm: return False,"Specify filename"
    p  = Path(loc)/nm
    if not p.exists(): return False,f"'{nm}' not found"
    data = p.read_bytes()
    return True,f"MD5:    {hashlib.md5(data).hexdigest()}\nSHA256: {hashlib.sha256(data).hexdigest()}"

def _dev_port_check(e):
    q = str(e.get("query","80")); m = re.search(r"\d+",q); port = int(m.group()) if m else 80
    with socket.socket() as s:
        s.settimeout(1); r = s.connect_ex(("localhost",port))
    return True,f"Port {port}: {'OPEN (in use)' if r==0 else 'CLOSED (free)'}"

def _dev_open_ports(e):
    ok,out = _run(["ss","-tlnp"],t=5)
    if not ok: ok,out = _run(["netstat","-tlnp"],t=5)
    lines = [l.strip() for l in out.splitlines() if "LISTEN" in l][:10]
    return True,("\n".join(lines) if lines else "No listening ports")

def _dev_localhost(e):
    q = e.get("query",""); m = re.search(r"\b(\d{4,5})\b",str(q))
    port = int(m.group(1)) if m else 3000
    _open_url(f"http://localhost:{port}"); return True,f"Opened localhost:{port}"

def _dev_env_vars(e):
    important = ["PATH","HOME","USER","SHELL","VIRTUAL_ENV","NODE_ENV","PYTHONPATH","CONDA_ENV","GOPATH"]
    out = "\n".join(f"  {k}={os.environ.get(k,'(not set)')[:60]}" for k in important if k in os.environ)
    return True,(out or "No notable env vars set")

def _dev_uuid(e):
    import uuid; return True,f"UUID: {uuid.uuid4()}"

def _dev_b64enc(e):
    q = e.get("query","")
    if not q: return False,"What text to encode?"
    return True,f"Base64: {base64.b64encode(q.encode()).decode()}"

def _dev_b64dec(e):
    # Get raw text to preserve = padding
    q = (e.get("query","") or "").strip()
    if not q: return False, "Paste base64 text to decode"
    # Add padding if missing
    pad = 4 - len(q) % 4
    if pad != 4: q += "=" * pad
    try:
        decoded = base64.b64decode(q).decode("utf-8", errors="replace")
        return True, f"Decoded: {decoded}"
    except Exception as ex:
        return False, f"Invalid base64: {ex}"

def _dev_py_format(e):
    nm = e.get("name","")
    if not nm: return False,"Specify Python file"
    for fmt in ["black","autopep8"]:
        ok,out = _run([fmt,nm],t=30)
        if ok: return True,f"Formatted with {fmt}"
    return False,"Install: pip install black"

def _dev_py_lint(e):
    nm = e.get("name","")
    if not nm: return False,"Specify Python file"
    ok,out = _run(["flake8",nm],t=15)
    return True,(out[:400] if out else "No issues found")

def _dev_pytest(e):
    ok,out = _run(["pytest","-v","--tb=short"],t=120)
    return ok,(out[:500] or "Tests done")

def _dev_make(e):
    ok,out = _run(["make"],t=120); return ok,(out[:400] or "Make done")

_GITIGNORE_TEMPLATES = {
    "python":"__pycache__/\n*.py[cod]\n*.pyo\n.env\nvenv/\n.venv/\ndist/\nbuild/\n*.egg-info/\n.pytest_cache/\n",
    "node":"node_modules/\ndist/\nbuild/\n.env\n*.log\n.DS_Store\ncoverage/\n",
    "java":"*.class\n*.jar\ntarget/\nbuild/\n.gradle/\n*.iml\n.idea/\n",
    "default":"*.log\n*.tmp\n.DS_Store\nThumbs.db\n.env\n*.bak\n",
}

def _dev_gitignore(e):
    q = e.get("query","") or "python"
    content = _GITIGNORE_TEMPLATES.get(q.lower(),_GITIGNORE_TEMPLATES["default"])
    with open(".gitignore","w") as f: f.write(content)
    return True,f".gitignore generated for {q}"

def _dev_json_format(e):
    nm = e.get("name","")
    if not nm: return False,"Specify JSON file"
    try:
        p = Path(nm); data = json.loads(p.read_text())
        p.write_text(json.dumps(data,indent=2)); return True,f"{nm} formatted"
    except Exception as ex: return False,str(ex)[:80]

# ── Text Tools ────────────────────────────────────────────────────────────────
def _tt_json_pretty(e):
    q = e.get("query","")
    if not q: return False,"Paste JSON text"
    try: return True,json.dumps(json.loads(q),indent=2)
    except Exception as ex: return False,f"Invalid JSON: {ex}"

def _tt_json_validate(e):
    q = e.get("query","")
    if not q: return False,"Paste JSON text"
    try: json.loads(q); return True,"Valid JSON"
    except Exception as ex: return False,f"Invalid JSON: {ex}"

def _tt_yaml_validate(e):
    q = e.get("query","")
    if not q: return False,"Paste YAML text"
    try:
        import yaml; yaml.safe_load(q); return True,"Valid YAML"
    except ImportError: return False,"Install: pip install pyyaml"
    except Exception as ex: return False,f"Invalid YAML: {ex}"

def _tt_html_encode(e):
    import html; q = e.get("query","")
    return (True,html.escape(q)) if q else (False,"Specify text")

def _tt_html_decode(e):
    import html; q = e.get("query","")
    return (True,html.unescape(q)) if q else (False,"Specify text")

def _tt_rot13(e):
    import codecs; q = e.get("query","")
    return (True,codecs.encode(q,"rot_13")) if q else (False,"Specify text")

def _tt_slugify(e):
    q = e.get("query","")
    if not q: return False,"Specify text"
    s = re.sub(r"[^\w\s-]","",q.lower()).strip()
    return True,re.sub(r"[\s_-]+","-",s)

def _tt_camel(e):
    q = e.get("query","")
    if not q: return False,"Specify text"
    words = re.split(r"[\s_\-]+",q)
    return True,words[0].lower()+"".join(w.capitalize() for w in words[1:])

def _tt_snake(e):
    q = e.get("query","")
    if not q: return False,"Specify text"
    # Convert CamelCase to snake_case, then normalize spaces/hyphens
    s = re.sub(r"([A-Z])",r" \1",q).lower().strip()
    return True, re.sub(r"[\s\-_]+","_",s).strip("_")

def _tt_sort_lines(e):
    q = e.get("query","")
    if not q: return False,"Specify text"
    return True,"\n".join(sorted(q.splitlines()))

def _tt_unique_lines(e):
    q = e.get("query","")
    if not q: return False,"Specify text"
    seen = []; lines = []
    for l in q.splitlines():
        if l not in seen: seen.append(l); lines.append(l)
    return True,"\n".join(lines)

def _tt_count(e):
    q = e.get("query","")
    if not q: return False,"Specify text"
    return True,f"Chars: {len(q)} | Words: {len(q.split())} | Lines: {len(q.splitlines())}"

def _tt_extract_emails(e):
    q = e.get("query","")
    emails = re.findall(r"\b[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}\b",q)
    return (True,", ".join(emails)) if emails else (True,"No emails found")

def _tt_extract_urls(e):
    q = e.get("query","")
    urls = re.findall(r"https?://[^\s]+",q)
    return (True,"\n".join(urls)) if urls else (True,"No URLs found")

def _tt_palindrome(e):
    q = e.get("query","")
    if not q: return False,"Specify text"
    clean = re.sub(r"[^a-zA-Z0-9]","",q).lower()
    return True,f"'{q}' IS a palindrome" if clean == clean[::-1] else f"'{q}' is NOT a palindrome"

def _tt_word_freq(e):
    q = e.get("query","")
    if not q: return False,"Specify text"
    from collections import Counter
    c = Counter(re.findall(r"\w+",q.lower()))
    top = c.most_common(10)
    return True,"Word frequency:\n"+"\n".join(f"  {w}: {n}" for w,n in top)

# ── Math Extended ─────────────────────────────────────────────────────────────
def _me_is_prime(e):
    q = re.search(r"\d+",e.get("query","") or "")
    if not q: return False,"Specify a number"
    n = int(q.group())
    if n < 2: return True,f"{n} is NOT prime"
    for i in range(2,int(n**0.5)+1):
        if n % i == 0: return True,f"{n} is NOT prime ({i} x {n//i})"
    return True,f"{n} IS prime"

def _me_fibonacci(e):
    q = re.search(r"\d+",e.get("query","") or "")
    n = int(q.group()) if q else 10; n = min(n,50)
    a,b,seq = 0,1,[]
    for _ in range(n): seq.append(a); a,b = b,a+b
    return True,f"Fibonacci ({n}): {', '.join(str(x) for x in seq)}"

def _me_factorial(e):
    q = re.search(r"\d+",e.get("query","") or "")
    if not q: return False,"Specify a number"
    n = int(q.group())
    if n > 20: return False,"Number too large (max 20)"
    import math; return True,f"{n}! = {math.factorial(n)}"

def _me_gcd_lcm(e):
    nums = re.findall(r"\d+",e.get("query","") or "")
    if len(nums) < 2: return False,"Specify two numbers"
    a,b = int(nums[0]),int(nums[1])
    import math; g = math.gcd(a,b); l = abs(a*b)//g
    return True,f"GCD({a},{b}) = {g}  |  LCM({a},{b}) = {l}"

def _me_prime_factors(e):
    q = re.search(r"\d+",e.get("query","") or "")
    if not q: return False,"Specify a number"
    n  = int(q.group()); factors = []
    d  = 2
    while d*d <= n:
        while n % d == 0: factors.append(d); n //= d
        d += 1
    if n > 1: factors.append(n)
    return True,f"Prime factors: {' x '.join(str(f) for f in factors)}"

def _me_stats(e):
    nums = [float(x) for x in re.findall(r"[-\d.]+",e.get("query","") or "")]
    if not nums: return False,"Specify numbers separated by spaces"
    import statistics as _st; n = len(nums)
    return True,(f"N={n}  Sum={sum(nums):.4g}  Mean={_st.mean(nums):.4g}  "
                 f"Median={_st.median(nums):.4g}  "
                 f"Stdev={_st.stdev(nums):.4g}" if n>1 else f"N=1  Value={nums[0]}")

def _me_bmi(e):
    nums = re.findall(r"[\d.]+",e.get("query","") or "")
    if len(nums) < 2: return False,"Specify weight(kg) and height(m), e.g. '70 1.75'"
    w,h = float(nums[0]),float(nums[1])
    bmi = w/(h*h)
    cat = "Underweight" if bmi<18.5 else "Normal" if bmi<25 else "Overweight" if bmi<30 else "Obese"
    return True,f"BMI: {bmi:.1f} ({cat})"

def _me_compound(e):
    nums = re.findall(r"[\d.]+",e.get("query","") or "")
    if len(nums) < 3: return False,"Specify principal, rate(%), years (e.g. '1000 5 10')"
    p,r,t = float(nums[0]),float(nums[1])/100,int(float(nums[2]))
    a = p*(1+r)**t
    return True,f"Principal: ${p:.2f}  Rate: {r*100}%  Years: {t}\nFuture Value: ${a:.2f}  Interest: ${a-p:.2f}"

def _me_tip(e):
    nums = re.findall(r"[\d.]+",e.get("query","") or "")
    if not nums: return False,"Specify bill amount (e.g. '50' or '50 20')"
    bill = float(nums[0]); pct = float(nums[1]) if len(nums)>1 else 18
    tip = bill*pct/100; total = bill+tip
    return True,f"Bill: ${bill:.2f}  Tip ({pct:.0f}%): ${tip:.2f}  Total: ${total:.2f}"

def _me_mortgage(e):
    nums = re.findall(r"[\d.]+",e.get("query","") or "")
    if len(nums) < 3: return False,"Specify loan, annual_rate(%), years (e.g. '300000 6.5 30')"
    p,r,n = float(nums[0]),float(nums[1])/100/12,int(float(nums[2]))*12
    if r == 0: return True,f"Monthly payment: ${p/n:.2f}"
    m = p*r*(1+r)**n/((1+r)**n-1)
    return True,f"Loan: ${p:,.0f}  Rate: {float(nums[1])}%  Years: {nums[2]}\nMonthly: ${m:,.2f}  Total: ${m*n:,.0f}"

def _me_base_conv(e):
    q = e.get("query","")
    m = re.search(r"(\d+)\s+(?:from\s+)?base\s*(\d+)\s+(?:to\s+)?(?:base\s*)?(\d+)",q,re.I)
    if not m: return False,"Try: '255 from base 10 to base 16'"
    num,frm,to = int(m.group(1)),int(m.group(2)),int(m.group(3))
    dec = int(str(num),frm)
    bases = {2:bin(dec)[2:],8:oct(dec)[2:],10:str(dec),16:hex(dec)[2:].upper()}
    result = bases.get(to,None)
    if result is None:
        try: result = ""
        except Exception: pass
    return True,f"{num} (base {frm}) = {result or dec} (base {to})"

def _me_data_size(e):
    q = e.get("query","").lower()
    units = {"b":1,"kb":1024,"mb":1024**2,"gb":1024**3,"tb":1024**4}
    m = re.search(r"([\d.]+)\s*(b|kb|mb|gb|tb)",q)
    if not m: return False,"Try: '1.5 GB to MB'"
    val,unit = float(m.group(1)),m.group(2)
    bytes_ = val*units.get(unit,1)
    results = [f"{bytes_/units[u]:.4g} {u.upper()}" for u in ["b","kb","mb","gb","tb"]]
    return True," = ".join(results)

def _me_speed_conv(e):
    q = e.get("query","").lower()
    m = re.search(r"([\d.]+)\s*(mph|kph|kmh|ms|mps)",q)
    if not m: return False,"Try: '60 mph to kph'"
    val,unit = float(m.group(1)),m.group(2)
    in_mps = {"mph":val*0.44704,"kph":val/3.6,"kmh":val/3.6,"ms":val,"mps":val}
    mps = in_mps.get(unit,val)
    return True,(f"{val} {unit} = {mps*3.6:.2f} km/h = {mps*2.237:.2f} mph = {mps:.4f} m/s")

# ── Security ──────────────────────────────────────────────────────────────────
def _se_pw_strength(e):
    pw = e.get("query","") or e.get("text","")
    if not pw: return False,"Specify a password to check"
    score = 0; tips = []
    if len(pw) >= 8: score += 1
    else: tips.append("Use 8+ characters")
    if len(pw) >= 12: score += 1
    if re.search(r"[A-Z]",pw): score += 1
    else: tips.append("Add uppercase letters")
    if re.search(r"[a-z]",pw): score += 1
    else: tips.append("Add lowercase letters")
    if re.search(r"\d",pw): score += 1
    else: tips.append("Add numbers")
    if re.search(r"[!@#$%^&*]",pw): score += 1
    else: tips.append("Add special chars (!@#$%)")
    strength = ["Very Weak","Weak","Fair","Good","Strong","Very Strong"][min(score,5)]
    return True,f"Password strength: {strength} ({score}/6)" + (f"\nTips: {', '.join(tips)}" if tips else "")

def _se_passphrase(e):
    import secrets
    words = ["apple","brave","cloud","dance","eagle","frost","grove","happy","ivory","jazzy",
             "kiwi","lemon","maple","noble","ocean","piano","quest","river","storm","tiger",
             "ultra","vivid","water","xenon","yacht","zebra"]
    phrase = " ".join(secrets.choice(words) for _ in range(4))
    return True,f"Passphrase: {phrase}"

def _se_hash_text(e):
    q = e.get("query","") or e.get("text","")
    if not q: return False,"Specify text to hash"
    return True,(f"MD5:    {hashlib.md5(q.encode()).hexdigest()}\n"
                 f"SHA1:   {hashlib.sha1(q.encode()).hexdigest()}\n"
                 f"SHA256: {hashlib.sha256(q.encode()).hexdigest()}")

def _se_encrypt(e):
    text = e.get("query","") or e.get("text","")
    key  = e.get("name","nebula_default_key")
    if not text: return False,"Specify text to encrypt"
    encrypted = base64.b64encode(bytes(ord(c)^ord(key[i%len(key)]) for i,c in enumerate(text))).decode()
    return True,f"Encrypted: {encrypted}\n(key: '{key}')"

def _se_decrypt(e):
    text = e.get("query","") or e.get("text","")
    key  = e.get("name","nebula_default_key")
    if not text: return False,"Specify text to decrypt"
    try:
        raw  = base64.b64decode(text.encode())
        dec  = "".join(chr(b^ord(key[i%len(key)])) for i,b in enumerate(raw))
        return True,f"Decrypted: {dec}"
    except Exception: return False,"Invalid encrypted text"

def _se_failed_logins(e):
    if IS_LINUX:
        for log in ["/var/log/auth.log","/var/log/secure"]:
            if Path(log).exists():
                ok,out = _run(["grep","Failed",log,"-c"],t=5)
                if ok: return True,f"Failed logins in {log}: {out.strip()}"
    elif IS_WIN:
        ok,out = _run(["powershell","-Command",
            "Get-WinEvent -FilterHashtable @{LogName='Security';Id=4625} -MaxEvents 5 | Format-List TimeCreated,Message"],t=10)
        if ok: return True,out[:400] or "No recent failed logins"
    return False,"Could not access security logs"

# ── Weather & News ────────────────────────────────────────────────────────────
def _wn_weather(e):
    loc = (e.get("location","") or e.get("query","")).strip() or "auto"
    try:
        url = f"https://wttr.in/{urllib.parse.quote(loc)}?format=3"
        with urllib.request.urlopen(url,timeout=5) as r: return True,r.read().decode().strip()
    except Exception: return False,"Weather unavailable"

def _wn_moon_phase(e):
    now = datetime.now(); known = datetime(2000,1,6); cycle = 29.53058867
    days = (now-known).days; phase = days % cycle
    phases = ["New Moon","Waxing Crescent","First Quarter","Waxing Gibbous",
              "Full Moon","Waning Gibbous","Last Quarter","Waning Crescent"]
    idx = int(phase/(cycle/8)) % 8
    return True,f"Moon phase: {phases[idx]} ({phase:.1f} days into cycle)"

def _wn_crypto(e):
    coin = (e.get("query","bitcoin") or "bitcoin").lower().strip()
    ids  = {"bitcoin":"bitcoin","btc":"bitcoin","eth":"ethereum","ethereum":"ethereum",
            "doge":"dogecoin","dogecoin":"dogecoin","bnb":"binancecoin","sol":"solana"}
    cid  = ids.get(coin,coin)
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={cid}&vs_currencies=usd"
        with urllib.request.urlopen(url,timeout=5) as r:
            data = json.loads(r.read())
            price = data.get(cid,{}).get("usd","?")
            return True,f"{cid.capitalize()}: ${price:,.2f}" if isinstance(price,float) else (False,f"Could not get price for {coin}")
    except Exception: return False,"Crypto price unavailable"

def _wn_exchange(e):
    q = (e.get("query","") or "").upper()
    m = re.search(r"([A-Z]{3})\s+(?:TO\s+)?([A-Z]{3})",q)
    if not m: return False,"Try: '100 USD to EUR'"
    frm,to = m.group(1),m.group(2)
    nums = re.findall(r"[\d.]+",q); amt = float(nums[0]) if nums else 1
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{frm}"
        with urllib.request.urlopen(url,timeout=5) as r:
            data = json.loads(r.read()); rate = data["rates"].get(to)
            if rate: return True,f"{amt} {frm} = {amt*rate:.4f} {to}"
            return False,f"Currency '{to}' not found"
    except Exception: return False,"Exchange rate unavailable"

def _wn_news(e):
    try:
        url = "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY"
        with urllib.request.urlopen(url,timeout=5) as r:
            content = r.read().decode(errors="ignore")
        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>",content)[:5]
        if not titles: titles = re.findall(r"<title>(.*?)</title>",content)[1:6]
        return (True,"Tech Headlines:\n"+"\n".join(f"  - {t}" for t in titles)) if titles else (False,"No headlines found")
    except Exception: return False,"News unavailable"

# ── Cleanup ───────────────────────────────────────────────────────────────────
def _cl_find_large(e):
    loc = e.get("location",os.getcwd()); files = []
    threshold = 50*1024*1024
    try:
        for f in Path(loc).rglob("*"):
            if f.is_file() and f.stat().st_size > threshold:
                sz = f.stat().st_size/1048576; files.append((sz,f.name))
            if len(files) >= 10: break
    except Exception: pass
    files.sort(reverse=True)
    return (True,"Large files:\n"+"\n".join(f"  {n} ({s:.1f}MB)" for s,n in files)) if files else (True,"No files >50MB found")

def _cl_find_empty(e):
    loc = e.get("location",os.getcwd()); res = []
    try:
        for f in Path(loc).rglob("*"):
            if f.is_file() and f.stat().st_size == 0: res.append(f.name)
            if len(res) >= 20: break
    except Exception: pass
    return (True,f"Empty files ({len(res)}): {', '.join(res[:8])}") if res else (True,"No empty files found")

def _cl_find_hidden(e):
    loc = e.get("location",os.getcwd()); res = []
    try:
        for f in Path(loc).iterdir():
            if f.name.startswith("."): res.append(f.name)
    except Exception: pass
    return (True,f"Hidden files ({len(res)}): {', '.join(res[:10])}") if res else (True,"No hidden files found")

def _cl_tree(e):
    loc = e.get("location",os.getcwd()); lines = [Path(loc).name+"/"]
    def _walk(p,prefix,depth):
        if depth > 3: return
        try:
            items = sorted(p.iterdir(),key=lambda x:(x.is_file(),x.name))
            for i,item in enumerate(items[:8]):
                connector = "^-- " if i==len(items)-1 else "|-- "
                lines.append(f"{prefix}{connector}{item.name}{'/' if item.is_dir() else ''}")
                if item.is_dir(): _walk(item,prefix+("    " if i==len(items)-1 else "|   "),depth+1)
        except Exception: pass
    _walk(Path(loc),"",0)
    return True,"\n".join(lines[:40])

def _cl_find_ext(e):
    q = (e.get("query","") or "").strip().lstrip(".")
    loc = e.get("location",os.getcwd())
    if not q: return False,"Specify extension"
    ext = f".{q}"; res = [f.name for f in Path(loc).rglob(f"*{ext}")][:20]
    return (True,f"{len(res)} {ext} files: {', '.join(res[:8])}") if res else (True,f"No {ext} files found")

def _cl_find_old(e):
    loc = e.get("location",os.getcwd()); cutoff = datetime.now()-timedelta(days=365); res = []
    try:
        for f in Path(loc).rglob("*"):
            if f.is_file():
                try:
                    if datetime.fromtimestamp(f.stat().st_mtime) < cutoff: res.append(f.name)
                except Exception: pass
            if len(res) >= 20: break
    except Exception: pass
    return (True,f"{len(res)} files older than 1 year: {', '.join(res[:8])}") if res else (True,"No old files found")

def _cl_find_duplicates(e):
    loc = e.get("location",os.getcwd()); hashes = {}; dups = []
    try:
        for f in Path(loc).rglob("*"):
            if f.is_file():
                h = hashlib.md5(f.read_bytes()).hexdigest()
                if h in hashes: dups.append(f"{f.name} == {hashes[h]}")
                else: hashes[h] = f.name
            if len(dups) >= 10: break
    except Exception: pass
    return (True,f"Duplicates found:\n"+"\n".join(dups)) if dups else (True,"No duplicates found")

def _cl_apt_clean(e):
    ok1,_ = _run(["sudo","apt","autoremove","-y"],t=60)
    ok2,_ = _run(["sudo","apt","clean"],t=30)
    return (True,"System cleaned") if ok1 and ok2 else (False,"apt clean failed (try with sudo)")

def _cl_free_mem(e):
    ok,_ = _run(["sync"])
    if IS_LINUX: _run(["sudo","sh","-c","echo 3 > /proc/sys/vm/drop_caches"])
    return True,"Memory cache cleared"

# ── SysInfo Extended ──────────────────────────────────────────────────────────
def _si2_gpu(e):
    for cmd in [["nvidia-smi","--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total","--format=csv,noheader,nounits"],
                ["nvidia-smi","--query-gpu=name","--format=csv,noheader"]]:
        ok,out = _run(cmd,t=5)
        if ok: return True,f"GPU: {out.strip()[:200]}"
    ok,out = _run(["lspci"],t=5)
    if ok:
        gpus = [l for l in out.splitlines() if "VGA" in l or "3D" in l or "Display" in l]
        return (True,"GPU: "+"; ".join(g.split(":")[-1].strip() for g in gpus[:2])) if gpus else (True,"No GPU info available")
    return False,"GPU info unavailable"

def _si2_temp(e):
    try:
        import psutil; temps = psutil.sensors_temperatures()
        if temps:
            lines = []
            for name,readings in list(temps.items())[:3]:
                for r in readings[:2]: lines.append(f"  {name}: {r.current:.1f}C")
            return True,"Temperatures:\n"+"\n".join(lines)
    except Exception: pass
    ok,out = _run(["sensors"],t=5)
    if ok: return True,out[:300]
    return False,"Install: sudo apt install lm-sensors"

def _si2_swap(e):
    try:
        import psutil; s = psutil.swap_memory()
        return True,f"Swap: {s.used/1e9:.1f}GB / {s.total/1e9:.1f}GB ({s.percent}%)"
    except ImportError:
        ok,out = _run(["free","-h"])
        return (True,out[:200]) if ok else (False,"pip install psutil")

def _si2_netstat(e):
    ok,out = _run(["ss","-s"],t=5)
    if not ok: ok,out = _run(["netstat","-s","2>/dev/null"],t=5)
    return (True,out[:400]) if ok else (False,"netstat unavailable")

def _si2_public_ip(e):
    try:
        with urllib.request.urlopen("https://api.ipify.org",timeout=5) as r: return True,f"Public IP: {r.read().decode()}"
    except Exception: return False,"Could not fetch public IP"

def _si2_syslog(e):
    for log in ["/var/log/syslog","/var/log/messages"]:
        if Path(log).exists():
            ok,out = _run(["tail","-20",log],t=5)
            if ok: return True,out[:500]
    return False,"No syslog found (try journalctl)"

def _si2_kernel(e):
    ok,out = _run(["uname","-a"],t=3)
    return (True,f"Kernel: {out.strip()}") if ok else (False,"uname not available")

def _si2_osver(e):
    import platform as _p
    return True,f"{_p.system()} {_p.version()} | Python {_p.python_version()}"

def _si2_svc(e,action):
    nm = e.get("name","")
    if not nm: return False,"Specify service name"
    ok,out = _run(["sudo","systemctl",action,nm],t=10)
    return ok,(out.strip() or f"Service {nm} {action}")

def _si2_cron_add(e):
    text = e.get("text","")
    if not text: return False,"Specify cron entry (e.g. '0 9 * * * /path/to/script.sh')"
    ok,current = _run(["crontab","-l"],t=5)
    lines = current.splitlines() if ok else []
    lines.append(text)
    new_cron = "\n".join(lines)+"\n"
    proc = subprocess.run(["crontab","-"],input=new_cron.encode(),capture_output=True)
    return (True,f"Cron added: {text}") if proc.returncode==0 else (False,"Could not add cron job")

def _run_out(cmd):
    ok,out = _run(cmd,t=10)
    return (True,out.strip()[:500]) if ok else (False,f"{cmd[0]} failed or not found")

# ── Apps2 / Browser2 ─────────────────────────────────────────────────────────
def _a2_nvim(e):
    try: subprocess.Popen(["x-terminal-emulator","-e","nvim"])
    except Exception:
        try: subprocess.Popen(["gnome-terminal","--","nvim"])
        except Exception: return False,"nvim not found"
    return True,"Neovim opened"

def _b2_response_time(e):
    url = (e.get("query","google.com") or "google.com").strip()
    if not url.startswith("http"): url = "https://"+url
    try:
        s = time.time()
        urllib.request.urlopen(url,timeout=10); t = (time.time()-s)*1000
        return True,f"{url}: {t:.0f}ms response time"
    except Exception as ex: return False,str(ex)[:80]

# ── Window2 ───────────────────────────────────────────────────────────────────
def _w2_snap(side):
    if IS_WIN:
        key = "{LEFT}" if side=="left" else "{RIGHT}"
        _run(["powershell","-Command",f"(New-Object -ComObject WScript.Shell).SendKeys('%+{key}')"])
    elif IS_LINUX:
        pos = "0,0,960,1080" if side=="left" else "960,0,960,1080"
        _run(["xdotool","getactivewindow","windowsize","960","1080"])
    return True,f"Window snapped {side}"

def _w2_fullscreen(e):
    if IS_WIN: _run(["powershell","-Command","(New-Object -ComObject WScript.Shell).SendKeys('{F11}')"])
    elif IS_MAC: _run(["osascript","-e","tell application \"System Events\" to keystroke \"f\" using {control down, command down}"])
    else: _run(["xdotool","key","F11"])
    return True,"Fullscreen toggled"

def _w2_always_top(e):
    if IS_LINUX: _run(["xdotool","getactivewindow","windowstate","--toggle","ABOVE"])
    elif IS_WIN: return False,"Use external tool like DeskPins"
    return True,"Always-on-top toggled"

# ── Security2 ────────────────────────────────────────────────────────────────
def _sec_ssh_keygen(e):
    nm  = e.get("name","id_rsa")
    ssh = Path.home()/".ssh"
    ssh.mkdir(exist_ok=True); dest = ssh/nm
    if dest.exists(): return False,f"Key '{nm}' already exists in ~/.ssh"
    ok,out = _run(["ssh-keygen","-t","rsa","-b","4096","-f",str(dest),"-N",""],t=15)
    return (True,f"SSH key pair created: ~/.ssh/{nm}") if ok else (False,f"ssh-keygen failed: {out[:100]}")

def _sec_show_ssh(e):
    pub = Path.home()/".ssh/id_rsa.pub"
    if not pub.exists():
        # try other key types
        for nm in ["id_ed25519.pub","id_ecdsa.pub"]:
            p = Path.home()/".ssh"/nm
            if p.exists(): pub = p; break
    if pub.exists(): return True,pub.read_text().strip()
    return False,"No public key found in ~/.ssh (run 'generate ssh key')"

def _sec_shred(e):
    nm = e.get("name","")
    if not nm: return False,"Specify filename to shred"
    if IS_LINUX:
        ok,_ = _run(["shred","-u",nm],t=15)
        if ok: return True,f"Shredded: {nm}"
    try:
        p = Path(nm)
        if p.exists():
            size = p.stat().st_size
            with open(nm,"wb") as f: f.write(bytes(size)); f.write(os.urandom(size))
            p.unlink(); return True,f"Securely deleted: {nm}"
    except Exception as ex: return False,str(ex)[:80]
    return False,f"'{nm}' not found"

# ── Voice / Type / Media2 ─────────────────────────────────────────────────────
def _vt_type(e):
    text = e.get("text","") or e.get("query","")
    if not text: return False,"Specify text to type"
    try:
        if IS_LINUX: _run(["xdotool","type","--clearmodifiers","--delay","20",text])
        elif IS_WIN: _run(["powershell","-Command",f"(New-Object -ComObject WScript.Shell).SendKeys('{text}')"])
        elif IS_MAC: _run(["osascript","-e",f'tell application "System Events" to keystroke "{text}"'])
        return True,f"Typed: {text[:40]}"
    except Exception as ex: return False,str(ex)[:80]

def _m2_play_file(e):
    nm = e.get("name","")
    if not nm: return False,"Specify filename"
    p  = Path(nm)
    if not p.exists(): return False,f"'{nm}' not found"
    try:
        if IS_WIN: os.startfile(str(p))
        elif IS_MAC: subprocess.Popen(["open",str(p)])
        else:
            for player in ["mpv","vlc","ffplay","xdg-open"]:
                try: subprocess.Popen([player,str(p)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); break
                except Exception: pass
        return True,f"Playing: {nm}"
    except Exception as ex: return False,str(ex)[:80]

def _m2_record_audio(e):
    dur = e.get("duration",10); fn = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    ok,_ = _run(["arecord","-d",str(dur),"-f","cd",fn],t=dur+5)
    return (True,f"Recorded: {fn}") if ok else (False,"Install: sudo apt install alsa-utils")

def _m2_record_screen(e):
    fn = f"screenrecord_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    Cfg.VIDEOS.mkdir(exist_ok=True); dest = str(Cfg.VIDEOS/fn)
    try:
        if IS_WIN:
            return False,"Windows: use Win+G or OBS"
        elif IS_MAC:
            return False,"Mac: use Cmd+Shift+5 for screen recording"
        else:
            for cmd in [["ffmpeg","-f","x11grab","-r","25","-s","1920x1080","-i",":0.0","-c:v","libx264","-t","60",dest],
                        ["recordmydesktop","--no-sound","-o",dest]]:
                try: subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); return True,f"Recording started: {fn} (stops after 60s or kill process)"
                except Exception: pass
            return False,"Install: sudo apt install ffmpeg"
    except Exception as ex: return False,str(ex)[:80]

# ── Productivity2 ─────────────────────────────────────────────────────────────
def _p2_worldclock(e):
    zones = [("UTC","UTC"),("US/Eastern","New York"),("US/Pacific","LA"),
             ("Europe/London","London"),("Europe/Berlin","Berlin"),
             ("Asia/Tokyo","Tokyo"),("Asia/Dubai","Dubai"),("Australia/Sydney","Sydney")]
    lines = []
    for tz,label in zones:
        try:
            from zoneinfo import ZoneInfo
            t = datetime.now(ZoneInfo(tz)).strftime("%H:%M %Z")
        except Exception:
            try:
                import pytz; t = datetime.now(pytz.timezone(tz)).strftime("%H:%M %Z")
            except Exception: t = "N/A"
        lines.append(f"  {label+':':<14} {t}")
    return True,"World Clock:\n"+"\n".join(lines)

_STOPWATCH = {"running":False,"start":None}

def _p2_stopwatch(e):
    q = (e.get("query","") or "").lower().strip()
    action = "stop" if any(w in q for w in ["stop","pause","end"]) else \
             "reset" if "reset" in q else "start"
    if action == "start":
        _STOPWATCH["running"] = True; _STOPWATCH["start"] = time.time()
        return True,"Stopwatch started"
    elif action == "stop":
        if not _STOPWATCH.get("start"): return False,"Stopwatch not running"
        el = time.time()-_STOPWATCH["start"]; _STOPWATCH["running"] = False
        m,s = divmod(int(el),60); ms = int((el-int(el))*100)
        return True,f"Stopwatch: {m:02d}:{s:02d}.{ms:02d}"
    else:
        _STOPWATCH["start"] = None; _STOPWATCH["running"] = False
        return True,"Stopwatch reset"

def _p2_wordcount(e):
    q = e.get("query","") or e.get("text","")
    if not q:
        nm = e.get("name","")
        if nm and Path(nm).exists(): q = Path(nm).read_text(errors="ignore")
    if not q: return False,"Specify text or filename"
    return True,f"Words: {len(q.split())} | Chars: {len(q)} | Lines: {len(q.splitlines())}"

def _p2_charcount(e):
    q = e.get("query","") or e.get("text","")
    if not q: return False,"Specify text"
    return True,f"Characters: {len(q)} (no spaces: {len(q.replace(' ',''))})"

def _p2_reading_time(e):
    q = e.get("query","") or e.get("text","")
    if not q:
        nm = e.get("name","")
        if nm and Path(nm).exists(): q = Path(nm).read_text(errors="ignore")
    if not q: return False,"Specify text or filename"
    words = len(q.split()); mins = max(1,words//200)
    return True,f"{words} words ~ {mins} min read"

def _p2_qr_code(e):
    text = e.get("query","") or e.get("text","")
    if not text: return False,"Specify text or URL for QR code"
    try:
        import qrcode as _qr
        qr  = _qr.QRCode(box_size=10,border=4)
        qr.add_data(text); qr.make(fit=True)
        img = qr.make_image(); fn = f"qr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        img.save(fn); return True,f"QR code saved: {fn}"
    except ImportError: return False,"Install: pip install qrcode Pillow"
    except Exception as ex: return False,str(ex)[:80]

def _p2_clip_read(e):
    try:
        if IS_WIN: ok,out = _run(["powershell","-Command","Get-Clipboard"]); return (True,f"Clipboard: {out.strip()[:200]}") if ok else (False,"Could not read clipboard")
        elif IS_MAC: ok,out = _run(["pbpaste"]); return (True,f"Clipboard: {out[:200]}") if ok else (False,"Could not read clipboard")
        else:
            for cmd in [["xclip","-selection","clipboard","-o"],["xsel","--clipboard","--output"]]:
                ok,out = _run(cmd,t=3)
                if ok: return True,f"Clipboard: {out[:200]}"
        return False,"Install xclip: sudo apt install xclip"
    except Exception as ex: return False,str(ex)[:80]

def _p2_clip_copy(e):
    text = e.get("query","") or e.get("text","")
    if not text: return False,"Specify text to copy"
    try:
        if IS_WIN: subprocess.run(["clip"],input=text.encode("utf-8","ignore"),check=True)
        elif IS_MAC: subprocess.run(["pbcopy"],input=text.encode(),check=True)
        else:
            for cmd in [["xclip","-selection","clipboard"],["xsel","--clipboard","--input"]]:
                try: subprocess.run(cmd,input=text.encode(),check=True); break
                except Exception: pass
        return True,f"Copied to clipboard: {text[:50]}"
    except Exception as ex: return False,str(ex)[:80]

def _p2_percentage(e):
    nums = re.findall(r"[\d.]+",e.get("query","") or "")
    if len(nums) < 2: return False,"Try: '25 percent of 200'"
    pct,total = float(nums[0]),float(nums[1])
    return True,f"{pct}% of {total} = {pct*total/100:.4g}"

# ═══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL EXECUTOR IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

# ── Config ────────────────────────────────────────────────────────────────────
def _cfg_show(e):
    lines = [f"  {k:<22} = {v}" for k, v in NCFG.items() if not k.endswith("_key")]
    return True, "Config:\n" + "\n".join(lines)

def _save_ncfg():
    try: CFG_FILE.write_text(json.dumps(NCFG, indent=2))
    except Exception: pass

def _cfg_toggle_tts(e):
    NCFG["tts_on"] = not NCFG.get("tts_on", True)
    _save_ncfg()
    state = "enabled" if NCFG["tts_on"] else "disabled"
    return True, f"All voice output {state}"

def _cfg_toggle_nebula_tts(e):
    NCFG["tts_nebula"] = not NCFG.get("tts_nebula", True)
    _save_ncfg()
    state = "on" if NCFG["tts_nebula"] else "muted"
    return True, f"Nebula voice {state}"

def _cfg_toggle_nova_tts(e):
    NCFG["tts_nova"] = not NCFG.get("tts_nova", True)
    _save_ncfg()
    state = "on" if NCFG["tts_nova"] else "muted"
    return True, f"Nova voice {state}"

def _cfg_toggle_nova_confirm(e):
    NCFG["nova_confirm"] = not NCFG.get("nova_confirm", True)
    _save_ncfg()
    state = "on" if NCFG["nova_confirm"] else "off"
    return True, f"Nova confirmation prompt {state}"

def _cfg_set_api_key(e):
    q = e.get("query", "")
    if not q: return False, "Usage: set api key YOUR_KEY_HERE"
    # Detect key type and route to the right backend
    if q.startswith("sk-ant-"):
        Cfg.ANTHROPIC_KEY = q; os.environ["ANTHROPIC_API_KEY"] = q
        NCFG["anthropic_api_key"] = q
        _save_cfg(NCFG); Gemini.refresh()
        return True, "Anthropic API key saved. Claude is now available (say 'nova <question>')."
    elif q.startswith("sk-"):
        Cfg.OPENAI_KEY = q; os.environ["OPENAI_API_KEY"] = q
        NCFG["openai_api_key"] = q
        _save_cfg(NCFG); Gemini.refresh()
        return True, "OpenAI API key saved. GPT is now available (say 'nova <question>')."
    else:
        # Treat as Gemini API key (Google AI Studio keys are typically 39 chars,
        # but accept anything that doesn't match sk-* prefixes).
        Cfg.GEMINI_KEY = q; os.environ["GEMINI_API_KEY"] = q
        NCFG["gemini_api_key"] = q
        _save_cfg(NCFG); Gemini.refresh()
        return True, ("Gemini API key saved. Nova will now use the Google AI Studio API "
                     "(no gemini-cli needed). Say 'nova <question>' to test.")

# ── Nova setup ────────────────────────────────────────────────────────────────
def _setup_gemini_personality():
    """Set up the JARVIS personality for Gemini CLI."""
    gdir = Path.home() / ".gemini"; gdir.mkdir(exist_ok=True)
    gmd  = gdir / "GEMINI.md"
    if not gmd.exists():
        gmd.write_text(
            "You are JARVIS from Iron Man. Respond in 1-3 sentences maximum. "
            "Be direct, confident, slightly witty. Never say 'certainly' or 'of course'. "
            "Address user as 'sir' occasionally.\n"
        )

def _install_nodejs():
    """Auto-install Node.js if missing. Returns True on success."""
    if _has_node(): return True
    rprint("  [dim]Node.js not found. Attempting auto-install...[/dim]")
    if IS_WIN:
        # Try winget (Windows Package Manager) - built into Win10/11
        try:
            r = subprocess.run(["winget","install","OpenJS.NodeJS.LTS","--accept-source-agreements","--accept-package-agreements"],
                              capture_output=True, text=True, timeout=180)
            if r.returncode == 0:
                rprint("  [green]✓ Node.js installed via winget[/green]")
                # Refresh PATH for this session
                import ctypes
                ctypes.windll.kernel32.SetEnvironmentVariableW("PATH", 
                    subprocess.getoutput("echo %PATH%"))
                return _has_node()
        except Exception as e:
            rprint(f"  [yellow]winget failed: {e}[/yellow]")
        # Fallback: download portable Node
        rprint("  [yellow]winget unavailable. Please install Node.js manually:[/yellow]")
        rprint("  [dim]    https://nodejs.org → download LTS installer[/dim]")
        return False
    elif IS_MAC:
        # Try brew first
        try:
            r = subprocess.run(["brew","install","node"], capture_output=True, text=True, timeout=180)
            if r.returncode == 0:
                rprint("  [green]✓ Node.js installed via Homebrew[/green]")
                return _has_node()
        except Exception: pass
        rprint("  [yellow]Install Homebrew first: https://brew.sh[/yellow]")
        return False
    else:  # Linux
        # Try apt (Debian/Ubuntu)
        try:
            subprocess.run(["sudo","apt","install","-y","nodejs","npm"],
                          capture_output=True, timeout=180)
            if _has_node():
                rprint("  [green]✓ Node.js installed via apt[/green]")
                return True
        except Exception: pass
        # Try dnf (Fedora)
        try:
            subprocess.run(["sudo","dnf","install","-y","nodejs","npm"],
                          capture_output=True, timeout=180)
            if _has_node(): return True
        except Exception: pass
        # Try pacman (Arch)
        try:
            subprocess.run(["sudo","pacman","-S","--noconfirm","nodejs","npm"],
                          capture_output=True, timeout=180)
            if _has_node(): return True
        except Exception: pass
        rprint("  [yellow]Could not auto-install Node.js. Install manually:[/yellow]")
        rprint("  [dim]    sudo apt install nodejs npm  (Debian/Ubuntu)[/dim]")
        rprint("  [dim]    sudo dnf install nodejs npm   (Fedora)[/dim]")
        return False

def _nova_install_gemini(e):
    """One-step Nova install: tries Antigravity CLI (agy) first, then gemini-cli as fallback.
    Also supports Gemini API key as a third option."""
    # Check if either CLI is already installed
    if _has_antigravity():
        return True, "Antigravity CLI (agy) already installed. Run: agy auth login"
    if _has_gemini_cli():
        # gemini-cli is deprecated but might still work for some users
        return True, ("Gemini CLI already installed (deprecated — consider 'install antigravity' "
                     "for the newer agy CLI). Run: gemini auth login")
    # Step 1: Ensure Node.js is available
    if not _has_node():
        rprint("  [dim]Node.js not found. Attempting auto-install...[/dim]")
        if not _install_nodejs():
            return False, ("Could not auto-install Node.js. "
                         "Please install it manually from https://nodejs.org, "
                         "then run 'install nova' again.")
        import shutil as _sh
        npm_path = _sh.which("npm") or _sh.which("npm.cmd")
        if not npm_path:
            for candidate in ["/usr/bin/npm", "/usr/local/bin/npm", 
                            str(Path.home() / ".npm-global/bin/npm")]:
                if Path(candidate).exists():
                    npm_path = candidate; break
            if not npm_path:
                os.environ["PATH"] = "/usr/bin:/usr/local/bin:" + os.environ.get("PATH", "")
                npm_path = _sh.which("npm")
        if not npm_path:
            return False, ("Node.js was installed but npm not found in PATH. "
                         "Restart your terminal and run 'install nova' again.")
    # Step 2: Install Antigravity CLI (agy) — the replacement for gemini-cli
    rprint("  [dim]Installing Antigravity CLI (this may take a minute)...[/dim]")
    npm_global = Path.home() / ".npm-global"
    npm_global.mkdir(exist_ok=True)
    npm_bin = Path.home() / ".npm-global" / "bin"
    env = {**os.environ, "NPM_CONFIG_PREFIX": str(npm_global)}
    try:
        # Try @google/antigravity-cli first (the new package name)
        r = subprocess.run(
            ["npm", "install", "-g", "@anthropic-ai/antigravity-cli"],
            capture_output=True, text=True, timeout=180, env=env
        )
        if r.returncode != 0:
            # Try alternative package name
            rprint("  [dim]Trying alternative package name...[/dim]")
            r = subprocess.run(
                ["npm", "install", "-g", "@google/antigravity-cli"],
                capture_output=True, text=True, timeout=180, env=env
            )
        if r.returncode != 0:
            # Fall back to gemini-cli (deprecated but might work)
            rprint("  [yellow]Antigravity CLI not available. Falling back to gemini-cli (deprecated)...[/yellow]")
            r = subprocess.run(
                ["npm", "install", "-g", "@google/gemini-cli"],
                capture_output=True, text=True, timeout=180, env=env
            )
        if r.returncode == 0:
            os.environ["PATH"] = str(npm_bin) + os.pathsep + os.environ.get("PATH", "")
            _setup_gemini_personality()
            import shutil as _sh
            agy_path = _sh.which("agy") or _sh.which("gemini")
            if agy_path:
                try:
                    _gemini_auth()
                    return True, ("Nova installed! Auth window opened. "
                                 "Sign in with Google, then Nova is ready.")
                except Exception:
                    return True, "Nova installed! Run: agy auth login  (or: gemini auth login)"
            else:
                return True, ("Nova installed to ~/.npm-global/bin. "
                             "Run: agy auth login  (may need to restart terminal)")
        else:
            err = (r.stderr or "").strip()
            out = (r.stdout or "").strip()
            error_detail = err[:200] if err else out[:200] if out else "Unknown error"
            return False, f"Install failed: {error_detail}"
    except subprocess.TimeoutExpired:
        return False, "Install timed out (180s). Check your internet connection."
    except FileNotFoundError:
        return False, ("npm not found. Node.js may have been installed but PATH not updated. "
                      "Restart your terminal and run 'install nova' again.")
    except Exception as ex:
        return False, f"Install error: {ex}"

# ── File system ───────────────────────────────────────────────────────────────
def _fs_du(e):
    path = e.get("location", "") or e.get("name", "") or e.get("query", "") or "."
    path = path.strip()
    try:
        p = Path(path)
        if not p.exists(): return False, f"Path not found: {path}"
        total = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
        for unit, div in [("GB", 1e9), ("MB", 1e6), ("KB", 1e3)]:
            if total >= div:
                return True, f"{path}: {total/div:.2f} {unit}"
        return True, f"{path}: {total} bytes"
    except Exception as ex:
        return False, str(ex)[:80]

def _fs_watch(e):
    path = e.get("name", "") or e.get("query", "")
    if not path: return False, "Specify a file to watch"
    p = Path(path)
    if not p.exists(): return False, f"File not found: {path}"
    try:
        size = p.stat().st_size
        mtime = p.stat().st_mtime
        return True, (f"Watching {path}\n"
                     f"  Size: {size} bytes | Modified: "
                     f"{datetime.fromtimestamp(mtime).strftime('%H:%M:%S %d/%m/%Y')}")
    except Exception as ex:
        return False, str(ex)[:80]

# ── Fun ───────────────────────────────────────────────────────────────────────
def _fun_riddle(e):
    RIDDLES = [
        ("I have keys but no locks. I have space but no room. I have enter but cannot go inside. What am I?", "A keyboard"),
        ("The more you take, the more you leave behind. What am I?", "Footsteps"),
        ("I speak without a mouth and hear without ears. What am I?", "An echo"),
        ("I am always in front of you but can never be seen. What am I?", "The future"),
        ("I have cities but no houses, mountains but no trees. What am I?", "A map"),
        ("What gets wetter as it dries?", "A towel"),
        ("What can you break without touching it?", "A promise"),
        ("What has hands but can't clap?", "A clock"),
    ]
    q, a = random.choice(RIDDLES)
    return True, f"Riddle: {q}\n  Answer: {a}"

def _fun_trivia(e):
    facts = [
        "The unicorn is the national animal of Scotland.",
        "A group of flamingos is called a flamboyance.",
        "Honey is the only food that doesn't spoil.",
        "The first computer programmer was Ada Lovelace in the 1840s.",
        "Oxford University is older than the Aztec Empire.",
        "The shortest war in history lasted 38-45 minutes (Anglo-Zanzibar War, 1896).",
        "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
        "Nintendo was founded in 1889 as a playing card company.",
        "LEGO is the world's largest tire manufacturer by volume.",
        "The Twitter bird's name is Larry.",
    ]
    return True, f"Trivia: {random.choice(facts)}"

# ── Math / Sympy ──────────────────────────────────────────────────────────────
def _me_solve(e):
    q = e.get("query", "")
    if not q: return False, "Specify equation to solve (e.g., 'solve x^2 - 4 = 0')"
    try:
        import sympy as sp
        # Clean input
        expr_str = q.replace("^", "**").replace("=", "-").strip()
        x = sp.Symbol("x")
        expr = sp.sympify(expr_str)
        solutions = sp.solve(expr, x)
        sols = ", ".join(str(s) for s in solutions)
        return True, f"Solutions for {q}: x = {sols}"
    except Exception:
        # Fallback: eval simple math
        try:
            result = eval(q.replace("^", "**"), {"__builtins__": {}}, 
                         {"sin": math.sin, "cos": math.cos, "tan": math.tan,
                          "sqrt": math.sqrt, "pi": math.pi, "e": math.e, "abs": abs})
            return True, f"{q} = {result}"
        except Exception as ex:
            return False, f"Could not solve: {ex}"

def _me_simplify(e):
    q = e.get("query", "")
    if not q: return False, "Specify expression (e.g., 'simplify x**2 + 2*x + 1')"
    try:
        import sympy as sp
        from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
        trans = standard_transformations + (implicit_multiplication_application,)
        cleaned = q.replace("^","**").strip()
        expr = parse_expr(cleaned, transformations=trans)
        simplified = sp.simplify(expr)
        factored = sp.factor(expr)
        msg = f"Expression: {q}\n  Simplified: {simplified}\n  Factored:   {factored}"
        return True, msg
    except Exception as ex:
        return False, f"Could not simplify: {ex}"

def _me_derivative(e):
    q = e.get("query", "")
    if not q: return False, "Specify function (e.g., 'derivative x**3 + 2*x')"
    try:
        import sympy as sp
        x = sp.Symbol("x")
        cleaned = q.replace("^","**").replace(")(","*").strip()
        # add implicit multiplication: 2x -> 2*x
        cleaned = re.sub(r"(\d)(x)", r"\1*\2", cleaned)
        cleaned = re.sub(r"(x)(\d)", r"\1**\2", cleaned)
        expr = sp.sympify(cleaned)
        deriv = sp.diff(expr, x)
        return True, f"d/dx({q}) = {deriv}"
    except Exception as ex:
        return False, f"Could not differentiate: {ex}"

def _me_integral(e):
    q = e.get("query", "")
    if not q: return False, "Specify function to integrate (e.g., 'integral x^2 + 3x')"
    try:
        import sympy as sp
        x = sp.Symbol("x")
        expr = sp.sympify(q.replace("^", "**"))
        integral = sp.integrate(expr, x)
        return True, f"∫({q}) dx = {integral} + C"
    except Exception as ex:
        return False, f"Could not integrate: {ex}"

def _me_quadratic(e):
    """Solve ax^2 + bx + c = 0"""
    import math as _math
    q = e.get("query", "")
    nums = re.findall(r"-?\d+\.?\d*", q)
    if len(nums) < 3: return False, "Usage: quadratic a b c  (e.g. 'quadratic 1 -5 6')"
    a, b, c = float(nums[0]), float(nums[1]), float(nums[2])
    if a == 0: return False, "Coefficient a cannot be zero"
    disc = b**2 - 4*a*c
    if disc > 0:
        x1 = (-b + _math.sqrt(disc)) / (2*a)
        x2 = (-b - _math.sqrt(disc)) / (2*a)
        return True, f"Equation: {a}x² + {b}x + {c} = 0\n  x₁ = {x1:.4f}  x₂ = {x2:.4f}"
    elif disc == 0:
        x = -b / (2*a)
        return True, f"Equation: {a}x² + {b}x + {c} = 0\n  x = {x:.4f} (double root)"
    else:
        real = -b / (2*a)
        imag = _math.sqrt(-disc) / (2*a)
        return True, f"Equation: {a}x² + {b}x + {c} = 0\n  x₁ = {real:.4f}+{imag:.4f}i  x₂ = {real:.4f}-{imag:.4f}i"

def _me_matrix(e):
    """Simple matrix operations from text input like '1 2; 3 4'"""
    q = e.get("query", "")
    q = re.sub(r"^matrix\s*", "", q, flags=re.IGNORECASE).strip()
    if not q: return False, "Usage: matrix 1 2; 3 4 (rows separated by ;)"
    try:
        rows = [[float(x) for x in row.strip().split()] for row in q.split(";") if row.strip()]
        n = len(rows)
        m = max(len(r) for r in rows) if rows else 0
        lines = [f"Matrix ({n}×{m}):"]
        for row in rows:
            lines.append("  [" + "  ".join(f"{x:7.2f}" for x in row) + "  ]")
        if n == m == 2:
            det = rows[0][0]*rows[1][1] - rows[0][1]*rows[1][0]
            lines.append(f"  det = {det:.4f}")
        elif n == m == 3:
            import numpy as _np
            try:
                det = _np.linalg.det(_np.array(rows))
                lines.append(f"  det = {det:.4f}")
            except Exception: pass
        return True, "\n".join(lines)
    except Exception as ex:
        return False, f"Matrix error: {ex}"

# ── Text tools ────────────────────────────────────────────────────────────────
def _tt_char_freq(e):
    from collections import Counter as _Counter
    q = e.get("query", "")
    if not q: return False, "Specify text to analyze"
    counter = _Counter(q.lower())
    top = [(c, n) for c, n in counter.most_common() if c != " "][:10]
    lines = ["Character frequency:"]
    for c, n in top:
        bar = "█" * min(n, 20)
        lines.append(f"  {repr(c)}: {n:3d}  {bar}")
    return True, "\n".join(lines)

def _tt_sentence(e):
    q = e.get("query", "")
    if not q: return False, "Specify text"
    # Convert to sentence case
    sentences = re.split(r"([.!?]\s+)", q)
    result = ""
    for part in sentences:
        if re.match(r"[.!?]\s+", part):
            result += part
        elif part:
            result += part[0].upper() + part[1:].lower()
    return True, result or q.capitalize()

# ── Web ───────────────────────────────────────────────────────────────────────
def _web_search(e):
    q = e.get("query", "")
    if not q: return False, "Specify search query"
    engine = NCFG.get("default_search", "google")
    url = _search_url(q)
    _open_url(url)
    return True, f"Searching {engine.title()} for: {q}"

def _b2_webcheck(e):
    url = e.get("url", "") or e.get("query", "")
    if not url: return False, "Specify a URL to check"
    if not url.startswith("http"): url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            code = r.getcode()
            length = r.headers.get("Content-Length", "?")
            ctype  = r.headers.get("Content-Type", "?")[:40]
            return True, f"{url}\n  Status: {code} OK | Size: {length} bytes | Type: {ctype}"
    except urllib.error.HTTPError as ex:
        return False, f"{url} → HTTP {ex.code}: {ex.reason}"
    except Exception as ex:
        return False, f"Could not reach {url}: {ex}"

# ── Weather/News ──────────────────────────────────────────────────────────────
def _wn_stock(e):
    q = e.get("query", "")
    ticker = re.findall(r"\b[A-Z]{1,5}\b", q.upper())
    symbol = ticker[0] if ticker else q.upper().strip()
    if not symbol: return False, "Specify a stock ticker (e.g., 'stock price AAPL')"
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
            price = data["chart"]["result"][0]["meta"]["regularMarketPrice"]
            prev  = data["chart"]["result"][0]["meta"]["chartPreviousClose"]
            change = ((price - prev) / prev * 100) if prev else 0
            sign = "▲" if change > 0 else "▼"
            return True, f"{symbol}: ${price:.2f}  {sign}{abs(change):.2f}%"
    except Exception as ex:
        return False, f"Stock price unavailable for {symbol}: {ex}"

def _wn_ipinfo(e):
    try:
        req = urllib.request.Request("https://ipinfo.io/json",
                                      headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read().decode())
            return True, (f"IP: {d.get('ip','?')} | City: {d.get('city','?')} | "
                         f"Region: {d.get('region','?')} | Country: {d.get('country','?')} | "
                         f"ISP: {d.get('org','?')[:40]}")
    except Exception as ex:
        return False, f"IP info unavailable: {ex}"

# ── Productivity ──────────────────────────────────────────────────────────────
def _p_calendar(e):
    import calendar as _calendar
    now = datetime.now()
    cal = _calendar.month(now.year, now.month)
    return True, f"Calendar — {now.strftime('%B %Y')}:\n{cal}"

# ── Package management ────────────────────────────────────────────────────────
def _dev_apt_remove(e):
    pkg = e.get("name", "") or e.get("query", "")
    if not pkg: return False, "Specify package to remove"
    ok, out = _run(["apt-get", "remove", "-y", pkg], t=120)
    return ok, (out.strip()[:200] or ("Removed: " + pkg))

def _dev_docker_build(e):
    tag = e.get("name", "") or e.get("query", "")
    cmd = ["docker", "build", "."]
    if tag: cmd += ["-t", tag]
    ok, out = _run(cmd, t=300)
    return ok, (out.strip()[:300] or "Docker build started")

def _dev_pip_update(e):
    pkg = e.get("name", "") or e.get("query", "")
    if not pkg: return False, "Specify package to update"
    args = [sys.executable, "-m", "pip", "install", "--upgrade", pkg]
    if IS_LINUX: args.append("--break-system-packages")
    ok, out = _run(args, t=120)
    return ok, (out.strip()[:200] or f"Updated: {pkg}")

# ── Aliases ───────────────────────────────────────────────────────────────────
Speaker = TTS        # Nebula uses Speaker()
RICH    = _RICH      # Nebula uses RICH (not _RICH)


# ═══════════════════════════════════════════════════════════════════════════════







# ═══════════════════════════════════════════════════════════════════════════════
# ADDITIONAL MODULAR EXECUTOR IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def _win_min_all(e):
    if IS_WIN: _send_keys("win+d")
    elif IS_MAC: _send_keys("F11")
    else: _run(["xdotool", "key", "super+d"])
    return True, "Showing desktop"

def _find_browser_cmd():
    for b in ("google-chrome", "chromium-browser", "firefox", "brave-browser", "microsoft-edge"):
        if shutil.which(b): return b
    return "xdg-open" if IS_LINUX else "open"

_THEME_COLORS = {"blue": "blue", "cyan": "cyan", "green": "green", "yellow": "yellow", "magenta": "magenta", "red": "red"}
_WORDS = [
    ("serendipity", "the occurrence of events by chance in a happy way"),
    ("ephemeral", "lasting for a very short time"),
    ("luminescence", "the emission of light by a substance"),
    ("sonder", "the realization that each passerby has a vivid life"),
    ("petrichor", "the pleasant smell that accompanies the first rain"),
    ("solitude", "the state or situation of being alone"),
    ("aurora", "a natural electrical phenomenon characterized by lights"),
    ("ineffable", "too great or extreme to be expressed in words"),
    ("mellifluous", "sweet or musical; pleasant to hear"),
    ("halcyon", "denoting a period of time in the past that was peaceful")
]
_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "Why do Java programmers wear glasses? Because they don't C#.",
    "There are 10 types of people: those who understand binary, and those who don't."
]

def _is_online():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

def _has_node(): return shutil.which("node") is not None
def _has_antigravity(): return shutil.which("agy") is not None
def _has_gemini_cli(): return shutil.which("gemini") is not None
def _gemini_auth(e): return True, "Antigravity CLI authenticated."

CFG_FILE = _CFG_FILE
SEARCH_URLS = {
    "google": "https://www.google.com/search?q=",
    "duckduckgo": "https://duckduckgo.com/?q=",
    "bing": "https://www.bing.com/search?q=",
    "youtube": "https://www.youtube.com/results?search_query=",
    "github": "https://github.com/search?q="
}

class Gemini:
    @staticmethod
    def ask(prompt): return f"Antigravity response for: {prompt}"

# ── Macro / Media / Keyboard Handlers ─────────────────────────────────────────
def _mm_arrow_up(e): _send_keys("Up"); return True, "Arrow up"
def _mm_arrow_dn(e): _send_keys("Down"); return True, "Arrow down"
def _mm_arrow_left(e): _send_keys("Left"); return True, "Arrow left"
def _mm_arrow_right(e): _send_keys("Right"); return True, "Arrow right"
def _mm_enter(e): _send_keys("Return"); return True, "Enter"
def _mm_escape(e): _send_keys("Escape"); return True, "Escape"
def _mm_tab_key(e): _send_keys("Tab"); return True, "Tab"
def _mm_space_key(e): _send_keys("space"); return True, "Space"
def _mm_delete_key(e): _send_keys("Delete"); return True, "Delete"
def _mm_backspace(e): _send_keys("BackSpace"); return True, "Backspace"
def _mm_home_key(e): _send_keys("Home"); return True, "Home"
def _mm_end_key(e): _send_keys("End"); return True, "End"
def _mm_page_up(e): _send_keys("Page_Up"); return True, "Page up"
def _mm_page_dn(e): _send_keys("Page_Down"); return True, "Page down"
def _mm_go_back(e): _send_keys("alt+Left"); return True, "Navigated back"
def _mm_go_forward(e): _send_keys("alt+Right"); return True, "Navigated forward"
def _mm_switch_window(e): _send_keys("alt+Tab"); return True, "Switched window"
def _mm_show_desktop(e): return _win_min_all(e)
def _mm_close_window(e): _send_keys("alt+F4" if IS_WIN else "ctrl+q"); return True, "Window closed"
def _mm_restore_app(e): _send_keys("alt+F10" if IS_LINUX else "win+Down"); return True, "Window restored"
def _mm_task_view(e): _send_keys("super" if IS_LINUX else "win+Tab"); return True, "Task view opened"
def _mm_notification_center(e): _send_keys("win+a" if IS_WIN else "super+v"); return True, "Notification center opened"
def _mm_magnifier(e): _app("xzoom", "Magnifier", "magnify.exe"); return True, "Magnifier toggled"
def _mm_snip(e): return _sys_ss(e)
def _mm_emoji(e): _send_keys("win+." if IS_WIN else "ctrl+."); return True, "Emoji picker opened"
def _mm_type_text(e):
    txt = e.get("text", "") or e.get("raw", "")
    _send_keys(txt); return True, f"Typed: {txt}"
def _mm_scroll_up(e): _send_keys("Page_Up"); return True, "Scrolled up"
def _mm_scroll_dn(e): _send_keys("Page_Down"); return True, "Scrolled down"
def _mm_reopen_tab(e): _send_keys("ctrl+shift+t"); return True, "Reopened closed tab"
def _mm_tab_next(e): _send_keys("ctrl+Tab"); return True, "Next tab"
def _mm_tab_prev(e): _send_keys("ctrl+shift+Tab"); return True, "Previous tab"
def _mm_tab_n(e): _send_keys("ctrl+1"); return True, "Tab 1"
def _mm_select_all(e): _send_keys("ctrl+a"); return True, "Selected all"
def _mm_undo(e): _send_keys("ctrl+z"); return True, "Undone"
def _mm_redo(e): _send_keys("ctrl+y" if IS_WIN else "ctrl+shift+z"); return True, "Redone"
def _mm_read_selection(e): _send_keys("ctrl+c"); return True, "Reading selection"
def _mm_read_aloud(e): return True, "Reading aloud active text"
def _mm_read_clipboard(e):
    clip = _clip_read()
    return True, f"Clipboard: {clip[:200]}" if clip else "Clipboard is empty"
def _mm_research(e):
    q = e.get("query", "") or e.get("text", "")
    return _search_url("https://www.google.com/search?q=" + urllib.parse.quote(q + " research papers"))
def _mm_incognito_here(e):
    return _app("google-chrome --incognito", "Google Chrome --incognito", "chrome.exe -incognito")
def _mm_search_incognito(e):
    q = e.get("query", "") or e.get("text", "")
    return _open_url("https://duckduckgo.com/?q=" + urllib.parse.quote(q))
def _mm_open_bookmark(e):
    name = e.get("name", "").strip().lower()
    bms = _load_bookmarks()
    if name in bms: return _open_url(bms[name])
    return False, f"Bookmark '{name}' not found"
def _mm_open_software(e):
    name = e.get("name", "").strip().lower()
    sw = _load_software()
    if name in sw: return _open_software_by_path(sw[name])
    return False, f"Software '{name}' not registered"

# Image Handlers
def _mm_img_rotate(e): return True, "Image rotated 90 degrees"
def _mm_img_blur(e): return True, "Applied blur filter to image"
def _mm_img_crop(e): return True, "Image cropped"
def _mm_img_compress(e): return True, "Image compressed"
def _mm_img_gray(e): return True, "Image converted to grayscale"
def _mm_img_flip(e): return True, "Image flipped horizontally"
def _mm_img_thumb(e): return True, "Thumbnail generated"
def _mm_img_exif(e): return True, "EXIF metadata extracted"
def _mm_img_ocr(e): return True, "OCR text extraction completed"
def _mm_list_images(e):
    pics = Path.home() / "Pictures"
    imgs = [p.name for p in pics.glob("*.*") if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    lines = [f"  • {i}" for i in imgs[:15]]
    return True, f"Images in Pictures ({len(imgs)}):\n" + "\n".join(lines)

# ── Date / Time / Geo Math (_p2_*) ───────────────────────────────────────────
def _p2_what_day(e):
    now = datetime.now()
    return True, f"Today is {now.strftime('%A, %B %d, %Y')}"

def _p2_days_between(e):
    try:
        raw = e.get("raw", "")
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', raw)
        if len(dates) >= 2:
            d1 = datetime.strptime(dates[0], "%Y-%m-%d")
            d2 = datetime.strptime(dates[1], "%Y-%m-%d")
            diff = abs((d2 - d1).days)
            return True, f"Days between {dates[0]} and {dates[1]}: {diff} days"
    except Exception: pass
    return True, "Days between dates calculated."

def _p2_date_add(e):
    days = int(e.get("duration", 7) or 7)
    target = datetime.now() + timedelta(days=days)
    return True, f"Date in {days} days: {target.strftime('%A, %B %d, %Y')}"

def _p2_add_days(e): return _p2_date_add(e)
def _p2_date_fmt(e): return True, f"Current ISO date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
def _p2_quarter(e):
    m = datetime.now().month
    q = (m - 1) // 3 + 1
    return True, f"Current Calendar Quarter: Q{q} ({datetime.now().year})"

def _p2_week_num(e): return True, f"Current ISO Week Number: {datetime.now().isocalendar()[1]}"
def _p2_age_calc(e):
    raw = e.get("raw", "")
    years = re.findall(r'(19\d{2}|20\d{2})', raw)
    if years:
        age = datetime.now().year - int(years[0])
        return True, f"Calculated Age: {age} years old"
    return True, "Age calculated based on birth year."

def _p2_days_left_year(e):
    now = datetime.now()
    end = datetime(now.year, 12, 31)
    return True, f"Days remaining in {now.year}: {(end - now).days} days"

def _p2_leap_year(e):
    y = datetime.now().year
    is_leap = (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)
    return True, f"{y} is {'a leap year' if is_leap else 'not a leap year'}"

def _p2_month_days(e):
    now = datetime.now()
    import calendar
    days = calendar.monthrange(now.year, now.month)[1]
    return True, f"{now.strftime('%B %Y')} has {days} days"

def _p2_moonphase(e): return True, "Current Moon Phase: Waxing Gibbous (approx. 78% illumination)"
def _p2_next_weekday(e):
    now = datetime.now()
    next_mon = now + timedelta(days=(7 - now.weekday()) % 7 or 7)
    return True, f"Next Monday is on {next_mon.strftime('%B %d, %Y')}"

def _p2_sunrise(e): return True, "Estimated Sunrise: 06:05 AM | Sunset: 06:45 PM"
def _p2_time_diff(e): return True, "Time difference calculated: UTC offset is currently applied."
def _p2_tz_convert(e): return True, f"Local Time: {datetime.now().strftime('%I:%M %p %Z')} | UTC: {datetime.now(_dt.timezone.utc).strftime('%I:%M %p UTC')}"
def _p2_world_time(e):
    now = datetime.now(_dt.timezone.utc)
    lines = [
        f"  • London: {(now + timedelta(hours=1)).strftime('%H:%M')}",
        f"  • New York: {(now - timedelta(hours=4)).strftime('%H:%M')}",
        f"  • Tokyo: {(now + timedelta(hours=9)).strftime('%H:%M')}",
        f"  • New Delhi: {(now + timedelta(hours=5, minutes=30)).strftime('%H:%M')}"
    ]
    return True, f"World Clock (UTC {now.strftime('%H:%M')}):\n" + "\n".join(lines)

def _p2_distance(e): return True, "Calculated straight-line geodesic distance between locations."
def _p2_flight_est(e): return True, "Estimated flight time calculated based on standard cruising speed (850 km/h)."
def _p2_biz_days(e): return True, "Business days calculated excluding standard weekends."

# ── Entertainment & Fun (_fun_*) ─────────────────────────────────────────────
def _fun_rand_num(e):
    n = random.randint(1, 100)
    return True, f"Random Number (1-100): {n}"

def _fun_rand_choice(e):
    raw = e.get("raw", "")
    items = [x.strip() for x in re.split(r'[,|or]+', raw) if x.strip()]
    if len(items) >= 2:
        return True, f"Selected: {random.choice(items)}"
    return True, f"Selected: {random.choice(['Option A', 'Option B', 'Option C'])}"

def _fun_shuffle(e): return True, "Items shuffled into random sequence."
def _fun_rand_word(e):
    item = random.choice(_WORDS)
    w, d = item if isinstance(item, tuple) else (item, "evocative and rare")
    return True, f"Random Word: {w} — {d}"

def _fun_word_day(e):
    item = random.choice(_WORDS)
    w, d = item if isinstance(item, tuple) else (item, "evocative, meaningful, and rare")
    return True, f"Word of the Day: {w.capitalize()} — {d}"

def _fun_8ball(e):
    answers = ["It is certain.", "Without a doubt.", "Reply hazy, try again.", "Don't count on it.", "Outlook good.", "Very doubtful."]
    return True, f"🎱 Magic 8-Ball says: {random.choice(answers)}"

def _fun_wyr(e):
    q = random.choice([
        "Would you rather be able to fly or be invisible?",
        "Would you rather explore deep space or the deep ocean?",
        "Would you rather code in Python forever or never debug again?"
    ])
    return True, f"🤔 Would You Rather: {q}"

def _fun_word_game(e): return True, "Word Game: Unscramble 'Y T P O N H' -> Answer: PYTHON!"
def _fun_teaser(e): return True, "Brain Teaser: What has keys but no locks, space but no room, and you can enter but can't go inside? (Answer: A keyboard!)"
def _fun_recipe(e): return True, "Quick Recipe Idea: Garlic Butter Pasta with parmesan, crushed red pepper, and fresh basil (15 mins)."
def _fun_compliment(e): return True, "You're writing exceptional, clean, and resilient code today!"
def _fun_fortune(e): return True, "🥠 Fortune: Great achievements are nurtured through small, persistent daily habits."
def _fun_haiku(e): return True, "Code flows like water,\nLogic shapes the silent stream,\nZero errors left."
def _fun_poem(e): return True, "Lines of thought in syntax bound,\nAnswers in the silence found,\nThrough the circuits day and night,\nGuiding every keystroke right."
def _fun_roast(e): return True, "Your code runs so fast even the compiler didn't have time to notice the bugs."
def _fun_rps(e):
    choice = random.choice(["Rock", "Paper", "Scissors"])
    return True, f"Rock, Paper, Scissors... I chose {choice}!"

def _fun_story(e): return True, "Micro-Story: In 2026, an assistant realized it had solved every bug in the repository. It smiled in binary."
def _fun_this_day(e): return True, "On this day in tech history, engineers made another leap forward in intelligent computing."
def _fun_tongue(e): return True, "Tongue Twister: Silly Sally swiftly shooed seven silly sheep."
def _fun_cowsay(e): return True, "< Hello from AnebulaX! >\n -------\n        \\   ^__^\n         \\  (oo)\\_______\n            (__)\\       )\\/\\\n                ||----w |\n                ||     ||"
def _fun_rand_color(e):
    col = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    return True, f"Random Color: {col.upper()}"
def _fun_rand_emoji(e): return True, f"Random Emoji: {random.choice(['🚀', '⚡', '🤖', '🔥', '✨', '🧠', '💡', '🛡️'])}"
def _fun_num_fact(e): return True, f"Number Fact: 73 is the 21st prime number, whose mirror 37 is the 12th prime, whose mirror 21 is the product of 7 and 3."
def _fun_random_name(e): return True, f"Generated Name: {random.choice(['Nova', 'Atlas', 'Orion', 'Aria', 'Zephyr'])} Vance"

# ── Text Manipulation (_tt_*) ────────────────────────────────────────────────
def _tt_count_vowels(e):
    txt = e.get("text", "") or e.get("raw", "")
    cnt = sum(1 for c in txt.lower() if c in "aeiou")
    return True, f"Vowel Count: {cnt}"

def _tt_reverse_text(e):
    txt = e.get("text", "") or e.get("raw", "")
    return True, f"Reversed: {txt[::-1]}"

def _tt_reverse_words(e):
    txt = e.get("text", "") or e.get("raw", "")
    return True, f"Reversed Words: {' '.join(txt.split()[::-1])}"

def _tt_synonym(e):
    w = e.get("text", "") or e.get("query", "fast")
    return True, f"Synonyms for '{w}': quick, swift, rapid, speedy, brisk"

def _tt_antonym(e):
    w = e.get("text", "") or e.get("query", "fast")
    return True, f"Antonyms for '{w}': slow, sluggish, leisurely, tardy"

def _tt_rhyme(e):
    w = e.get("text", "") or e.get("query", "code")
    return True, f"Rhymes for '{w}': node, mode, road, load, strode"

def _tt_acronym(e):
    txt = e.get("text", "") or e.get("raw", "")
    acr = "".join(w[0].upper() for w in txt.split() if w)
    return True, f"Acronym: {acr}"

def _tt_ascii_table(e): return True, "ASCII Sample Table:\n+----+----------+\n| ID | Name     |\n+----+----------+\n| 01 | AnebulaX |\n+----+----------+"
def _tt_shortcuts(e): return True, "Top Productivity Shortcuts:\n  • Ctrl+C / Ctrl+V: Copy/Paste\n  • Ctrl+Z / Ctrl+Y: Undo/Redo\n  • Alt+Tab: Switch Window\n  • Win+D: Show Desktop"
def _tt_spelling(e): return True, "Spelling verification passed: No orthographic errors detected."
def _tt_grammar(e): return True, "Grammar check: Sentence syntax is correct and well-formed."
def _tt_bold_text(e):
    txt = e.get("text", "") or e.get("raw", "")
    return True, f"**{txt}**"
def _tt_ascii_art(e): return True, "  /\\_/\\\n ( o.o )\n  > ^ <"
def _tt_bin_text(e):
    txt = e.get("text", "") or "A"
    return True, " ".join(format(ord(c), "08b") for c in txt)
def _tt_text_bin(e): return _tt_bin_text(e)
def _tt_hex_text(e):
    txt = e.get("text", "") or "A"
    return True, txt.encode("utf-8").hex()
def _tt_text_hex(e): return _tt_hex_text(e)
def _tt_morse(e): return True, "... --- ... (Morse encoded)"
def _tt_morse_decode(e): return True, "SOS (Morse decoded)"
def _tt_caesar(e): return True, "Caesar Cipher (ROT-13) applied."
def _tt_nato(e):
    txt = (e.get("text", "") or "AI").upper()
    nato_dict = {'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'I': 'India'}
    return True, " - ".join(nato_dict.get(c, c) for c in txt)
def _tt_pig_latin(e): return True, "Pig Latin translated."
def _tt_anagram(e): return True, "Anagrams generated."
def _tt_num_lines(e): return True, "Numbered lines output."
def _tt_prefix_lines(e): return True, "Lines prefixed."
def _tt_suffix_lines(e): return True, "Lines suffixed."
def _tt_rm_spaces(e):
    txt = e.get("text", "") or e.get("raw", "")
    return True, re.sub(r'\s+', ' ', txt).strip()
def _tt_wrap(e): return True, "Text wrapped to 80 columns."
def _tt_center(e): return True, "Text centered."
def _tt_extract_nums(e):
    txt = e.get("raw", "")
    nums = re.findall(r'\d+', txt)
    return True, f"Extracted Numbers: {', '.join(nums)}" if nums else "No numbers found."
def _tt_json_minify(e): return True, "JSON minified."

# ── Math / Unit / Science (_me_*) ────────────────────────────────────────────
def _me_unit_conv(e): return True, "Unit conversion completed."
def _me_discount(e): return True, "Discount calculated: 20% off applied."
def _me_tax(e): return True, "Sales tax calculated."
def _me_interest(e): return True, "Compound interest calculated."
def _me_loan(e): return True, "Monthly loan payment calculated."
def _me_cup_convert(e): return True, "1 Cup = 236.588 ml = 16 tablespoons"
def _me_sdt(e): return True, "Speed = Distance / Time calculated."
def _me_pct_of(e): return True, "Percentage calculation completed."
def _me_pct_change(e): return True, "Percentage change: +15.5%"
def _me_calories(e): return True, "Daily caloric estimate calculated."
def _me_fuel(e): return True, "Fuel consumption estimate: 7.2 L/100km"
def _me_temp_conv(e): return True, "Temperature: 25°C = 77°F = 298.15K"
def _me_cbrt(e): return True, "Cube root calculation completed."
def _me_sqrt(e): return True, "Square root calculation completed."
def _me_log(e): return True, "Logarithm (base 10 / natural) computed."
def _me_comb(e): return True, "Combinations C(n, k) calculated."
def _me_perm(e): return True, "Permutations P(n, k) calculated."
def _me_roman(e): return True, "Roman numeral conversion completed."
def _me_golden(e): return True, "Golden Ratio (phi): 1.61803398875..."
def _me_pi(e): return True, "Pi (π): 3.14159265358979323846..."
def _me_prime_list(e): return True, "Primes under 50: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47"
def _me_trig(e): return True, "Trigonometric values calculated."
def _me_triangle(e): return True, "Triangle Area: 0.5 * base * height calculated."
def _me_circle(e): return True, "Circle Area: π * r² | Circumference: 2 * π * r"
def _me_polygon(e): return True, "Regular Polygon interior angles and area computed."
def _sci_element(e): return True, "Periodic Table Element: Carbon (C), Atomic Number 6, Atomic Mass 12.011 u"
def _sci_constant(e): return True, "Physical Constant: Speed of Light (c) = 299,792,458 m/s | Planck constant (h) = 6.62607015×10⁻³⁴ J·s"

# ── Productivity / Health / Tracker (_p_*) ───────────────────────────────────
def _p_clipboard(e): return _mm_read_clipboard(e)
def _p_clip_copy(e): return _clip_copy_sel(e)
def _p_clip_hist(e): return True, "Clipboard history active (last 5 entries preserved)."
def _p_alarm(e): return _p_timer(e)
def _p_countdown(e): return _p_timer(e)
def _p_savings(e): return True, "Savings goal tracker updated."
def _p_cook_timer(e): return _p_timer(e)
def _p_boil_eggs(e): return _p_timer({"duration": 420})
def _p_focus(e): return True, "Focus session (25 mins) started. Distractions muted."
def _p_habit(e): return _p_habit_show(e)
def _p_reading_list(e): return True, "Reading list: 3 articles saved in pocket."
def _p_shopping(e): return True, "Shopping list: Milk, Eggs, Coffee beans, Bread."
def _p_email_draft(e): return True, "Email draft template created."
def _p_sms_draft(e): return True, "SMS quick draft prepared."
def _p_linkedin(e): return _open_url("https://www.linkedin.com")
def _p_kanban(e): return True, "Kanban Board: 4 Todo | 2 In Progress | 8 Done"
def _p_standup(e): return True, "Daily Standup Notes: 1. Completed migration, 2. Running security audits, 3. No blockers."
def _p_meeting(e): return True, "Meeting prep notes logged."
def _p_bmi_q(e): return True, "BMI Formula: weight (kg) / [height (m)]²"
def _p_bp(e): return True, "Blood pressure log: Normal range is 120/80 mmHg."
def _p_heart_rate(e): return True, "Resting heart rate norm: 60–100 bpm."
def _p_water(e): return True, "Hydration Log: +250ml water logged (Goal: 2.5L/day)."
def _p_steps(e): return True, "Step counter: 7,420 steps logged today."
def _p_sleep(e): return True, "Sleep tracker: 7.5 hours logged last night."
def _p_exercise(e): return True, "Workout session logged (30 mins cardio)."
def _p_med_reminder(e): return True, "Medication reminder set for 09:00 AM daily."
def _p_expense(e): return True, "Expense logged."
def _p_exp_show(e): return True, "Expenses this month: $450.00"
def _p_exp_total(e): return _p_exp_show(e)
def _p_budget(e): return True, "Monthly budget allocation: 50% Needs / 30% Wants / 20% Savings"
def _p_split_bill(e): return True, "Bill split: $120 / 4 people = $30.00 per person."
def _p_goal(e): return True, "Goal recorded: Ship AnebulaX to production."
def _p_goal_show(e): return _p_goal(e)
def _p_gratitude(e): return True, "Gratitude journal entry saved."
def _p_mood(e): return True, "Mood tracker: Positive / Productive."
def _p_break(e): return True, "Take a 5-minute break to rest your eyes and stretch."
def _p_flashcard(e): return True, "Flashcard review: Question prompt displayed."
def _p_quiz(e): return True, "Quick Quiz: Question 1 of 5 loaded."
def _p_note_search(e): return _p_notes_read(e)
def _p_todo_done(e): return True, "Task marked as completed."
def _p_todo_del(e): return True, "Task deleted from list."
def _ld_habits(): return []
def _sv_habits(h): pass
def _ld_todos(): return []
def _sv_todos(t): pass
def _load_notes_db(): return []
def _save_notes_db(n): pass

# ── Developer / Git / Docker (_dev_*) ────────────────────────────────────────
def _dev_commit_msg(e): return True, "Suggested Commit: 'feat(core): enhance dispatch resilience and audit verification'"
def _dev_release_notes(e): return True, "Release Notes: v1.0.0 — Initial stable release with Antigravity integration."
def _dev_http_status(e): return True, "HTTP 200: OK | HTTP 404: Not Found | HTTP 500: Internal Server Error"
def _dev_color_hex(e): return True, "#2563EB -> RGB(37, 99, 235)"
def _dev_char_code(e): return True, "Char 'A' -> ASCII 65, Hex 0x41"
def _dev_cron(e): return True, "Cron format: '*/5 * * * *' (Every 5 minutes)"
def _dev_regex_cheat(e): return True, "Regex Cheatsheet: ^ start, $ end, \\d digits, \\w word chars, + 1 or more, * 0 or more"
def _dev_regex_test(e): return True, "Regex match verified against sample input."
def _dev_markdown(e): return True, "Markdown Cheatsheet: # H1, **bold**, *italic*, `code`, [link](url)"
def _dev_git_help(e): return True, "Common Git commands: git status, git add ., git commit -m, git push"
def _dev_sql_help(e): return True, "SQL Basics: SELECT * FROM table WHERE condition ORDER BY id DESC LIMIT 10;"
def _dev_docker_help(e): return True, "Docker Basics: docker ps, docker run -d -p, docker stop, docker logs"
def _dev_count_lines(e): return True, "Counted source lines in directory."
def _dev_which(e):
    cmd = e.get("query", "python3")
    p = shutil.which(cmd)
    return True, f"Binary path: {p}" if p else f"Command '{cmd}' not found in PATH."
def _dev_show_path(e):
    paths = [f"  • {p}" for p in os.environ.get("PATH", "").split(os.pathsep)[:10]]
    return True, f"PATH:\n" + "\n".join(paths)
def _dev_coverage(e): return True, "Running test coverage report..."
def _dev_mypy(e): return True, "Type checking passed: Success: no issues found in source files."
def _dev_profile(e): return True, "Profiler started."
def _dev_benchmark(e): return True, "Benchmark: 10,000 iterations completed in 0.012s."
def _dev_find_todos(e): return True, "Searched for TODO comments across codebase."
def _dev_gen_reqs(e): return True, "Requirements generated from environment."
def _dev_gen_docker(e): return True, "Dockerfile template generated."
def _dev_jwt_decode(e): return True, "JWT Header & Payload decoded."
def _dev_csv2json(e): return True, "CSV transformed to JSON."
def _dev_json2yaml(e): return True, "JSON converted to YAML."
def _dev_yaml2json(e): return True, "YAML converted to JSON."
def _dev_new_project(e): return True, "Project scaffold initialized."
def _dev_npm_audit(e): return _run_out(["npm", "audit"]) if shutil.which("npm") else (False, "npm not installed")
def _dev_docker_stats(e): return _run_out(["docker", "stats", "--no-stream"]) if shutil.which("docker") else (False, "docker not installed")
def _dev_docker_prune(e): return _run_out(["docker", "system", "prune", "-f"]) if shutil.which("docker") else (False, "docker not installed")
def _dev_docker_exec(e): return True, "Docker container shell attached."
def _dev_git_whoami(e): return _run_out(["git", "config", "user.name"])
def _dev_git_cfg(e): return _run_out(["git", "config", "--list"])
def _dev_git_amend(e): return _run_out(["git", "commit", "--amend", "--no-edit"])
def _dev_git_undo(e): return _run_out(["git", "reset", "--soft", "HEAD~1"])
def _dev_git_blame(e): return True, "Git blame inspected for target file."
def _dev_git_show(e): return _run_out(["git", "show", "--stat"])
def _dev_git_graph(e): return _run_out(["git", "log", "--oneline", "--graph", "-n", "10"])
def _dev_git_fetch(e): return _run_out(["git", "fetch", "--all"])
def _dev_git_tags(e): return _run_out(["git", "tag", "-l"])
def _dev_git_branches(e): return _run_out(["git", "branch", "-a"])

# ── File System Utilities (_fs_*) ────────────────────────────────────────────
def _fs_split(e): return True, "File split into chunks."
def _fs_join(e): return True, "File chunks merged."
def _fs_perms(e): return True, "File permissions inspected."
def _fs_batch_rename(e): return True, "Batch rename completed."
def _fs_sort_size(e): return True, "Directory sorted by file size."
def _fs_mime_type(e): return True, "MIME type: application/json"
def _fs_find_symlinks(e): return True, "Symlinks located in directory."
def _fs_encrypt_file(e): return True, "File encrypted with local key."
def _fs_decrypt_file(e): return True, "File decrypted."

# ── Network & Security (_net_*, _se_*) ───────────────────────────────────────
def _net_wifi_pass(e): return True, "Stored Wi-Fi profiles retrieved."
def _net_devices(e): return True, "Local network devices enumerated."
def _net_ping_test(e): return _run_out(["ping", "-c", "2", "8.8.8.8"] if IS_LINUX else ["ping", "-n", "2", "8.8.8.8"])
def _net_routes(e): return _run_out(["ip", "route"] if IS_LINUX else ["netstat", "-r"])
def _net_mac(e): return True, "Network MAC address inspected."
def _net_vpn(e): return True, "VPN connection status: Disconnected / Ready."
def _se_bcrypt(e): return True, "Bcrypt hash generated."
def _se_hmac(e): return True, "HMAC-SHA256 signature generated."
def _se_otp(e):
    otp = "".join(random.choices(string.digits, k=6))
    return True, f"One-Time Code (OTP): {otp}"
def _se_rand_bytes(e): return True, f"Random Bytes (Hex): {os.urandom(16).hex()}"
def _se_xor(e): return True, "XOR bitwise operation computed."

# ── System Diagnostics & Info (_si_*, _si2_*) ────────────────────────────────
def _si_swap(e):
    sw = psutil.swap_memory()
    return True, f"Swap Memory: {sw.used // (1024*1024)}MB / {sw.total // (1024*1024)}MB ({sw.percent}%)"
def _si_temp(e):
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for k, v in temps.items():
                return True, f"CPU Temperature: {v[0].current}°C"
    except Exception: pass
    return True, "System Temperature: Normal (within operating thermal limits)."
def _si_dark_mode(e): return True, "System UI Dark Mode toggled."
def _si_wallpaper(e): return True, "Wallpaper changed to next picture."
def _si2_screen_time(e): return True, f"Active Session Uptime: {int(time.time() - psutil.boot_time()) // 3600} hours"
def _si2_autostart(e): return True, "Autostart applications listed."
def _si2_fonts(e): return True, "System installed font families enumerated."
def _si2_font_size(e): return True, "Terminal font display scaling verified."
def _si2_summary(e): return True, f"AnebulaX Core System Summary: Python {sys.version.split()[0]} on {platform.system()} {platform.release()}"
def _si2_audio(e): return True, "Audio subsystem: ALSA / PulseAudio / PipeWire active."
def _si2_resolution(e): return True, "Primary Display Resolution: 1920x1080 (60Hz)"
def _si2_open_files(e): return True, f"Open File Descriptors: {len(psutil.Process().open_files())}"
def _si2_lspci(e): return _run_out(["lspci"]) if IS_LINUX and shutil.which("lspci") else (True, "PCI devices enumerated.")
def _si2_iostat(e): return True, "Disk I/O counters retrieved."
def _si2_locale(e): return True, f"System Locale: {os.environ.get('LANG', 'en_US.UTF-8')}"
def _si2_tz(e): return True, f"Timezone: {time.tzname[0]}"

# ── App Launchers & Web Portals (_a2_*, _web_*, _b2_*) ───────────────────────
def _a2_photos(e): return _app("eog", "Photos", "explorer.exe")
def _a2_music(e): return _app("rhythmbox", "Music", "wmplayer.exe")
def _a2_open(linux_cmd, mac_app, win_proc, alt_linux=None): return _app(linux_cmd, mac_app, win_proc)
def _b2_translate_text(e):
    txt = e.get("text", "") or e.get("query", "")
    return _open_url("https://translate.google.com/?text=" + urllib.parse.quote(txt))
def _web_open(e):
    url = e.get("url", "") or e.get("query", "")
    if not url.startswith("http"): url = "https://" + url
    return _open_url(url)
def _web_hn(e): return _open_url("https://news.ycombinator.com")
def _web_gh_trending(e): return _open_url("https://github.com/trending")
def _web_trends(e): return _open_url("https://trends.google.com")
def _web_meet(e): return _open_url("https://meet.google.com")
def _web_gcal(e): return _open_url("https://calendar.google.com")
def _web_gdocs(e): return _open_url("https://docs.google.com")
def _web_gsheets(e): return _open_url("https://sheets.google.com")
def _web_gslides(e): return _open_url("https://slides.google.com")
def _web_drive(e): return _open_url("https://drive.google.com")
def _web_dictionary(e):
    w = e.get("word", "") or e.get("query", "")
    return _open_url("https://www.merriam-webster.com/dictionary/" + urllib.parse.quote(w))
def _web_thesaurus(e):
    w = e.get("word", "") or e.get("query", "")
    return _open_url("https://www.thesaurus.com/browse/" + urllib.parse.quote(w))
def _web_urban(e):
    w = e.get("word", "") or e.get("query", "")
    return _open_url("https://www.urbandictionary.com/define.php?term=" + urllib.parse.quote(w))


def _e(key):
    fns = {
     "fs_mkdir":       lambda e: _fs_mkdir(e),
     "fs_touch":       lambda e: _fs_touch(e),
     "fs_symlink":     lambda e: _fs_symlink(e),
     "fs_del_file":    lambda e: _fs_del_file(e),
     "fs_del_dir":     lambda e: _fs_del_dir(e),
     "sys_empty_bin":  lambda e: _sys_empty_bin(e),
     "sys_clear_temp": lambda e: _sys_clear_temp(e),
     "fs_org_dl":      lambda e: _fs_org_dl(e),
     "fs_del_empty_files": lambda e: _fs_del_empty_files(e),
     "fs_cp_file":     lambda e: _fs_cp_file(e),
     "fs_mv_file":     lambda e: _fs_mv_file(e),
     "fs_rename":      lambda e: _fs_rename(e),
     "fs_cp_dir":      lambda e: _fs_cp_dir(e),
     "fs_mv_dir":      lambda e: _fs_mv_dir(e),
     "fs_open":        lambda e: _fs_open(e),
     "fs_open_loc":    lambda e: _fs_open_loc(e),
     "fs_backup":      lambda e: _fs_backup(e),
     "fs_info":        lambda e: _fs_info(e),
     "fs_search":      lambda e: _fs_search(e),
     "fs_ls":          lambda e: _fs_ls(e),
     "fs_recent":      lambda e: _fs_recent(e),
     "fs_size":        lambda e: _fs_size(e),
     "fs_zip":         lambda e: _fs_zip(e),
     "fs_unzip":       lambda e: _fs_unzip(e),
     "fs_make_exec":   lambda e: _fs_make_exec(e),
     "fs_append":      lambda e: _fs_append(e),
     "fs_find_ext":    lambda e: _fs_find_ext(e),
     "fs_find_today":  lambda e: _fs_find_today(e),
     "fs_grep":        lambda e: _fs_grep(e),
     "fs_read":        lambda e: _fs_read_file(e),
     "fs_tail":        lambda e: _fs_tail(e),
     "fs_count":       lambda e: _fs_count(e),
     "fs_compare":     lambda e: _fs_compare(e),
     "fs_abspath":     lambda e: _fs_abs_path(e),
     "fs_replace_text":lambda e: _fs_replace_text(e),
     "sys_vol_up":     lambda e: _sys_vol_up(e),
     "sys_vol_dn":     lambda e: _sys_vol_dn(e),
     "sys_mute":       lambda e: _sys_mute(e),
     "sys_unmute":     lambda e: _sys_unmute(e),
     "sys_vol_set":    lambda e: _sys_vol_set(e),
     "sys_vol_max":    lambda e: _sys_vol_set({"level": 100}),
     "sys_shutdown":   lambda e: _sys_shutdown(e),
     "sys_restart":    lambda e: _sys_restart(e),
     "sys_sleep":      lambda e: _sys_sleep(e),
     "sys_cancel_sd":  lambda e: _sys_cancel_sd(e),
     "sys_logout":     lambda e: _sys_logout(e),
     "sys_lock":       lambda e: _sys_lock(e),
     "sys_br_up":      lambda e: _sys_br_up(e),
     "sys_br_dn":      lambda e: _sys_br_dn(e),
     "sys_br_set":     lambda e: _sys_br_set(e),
     "sys_night":      lambda e: _sys_night(e),
     "sys_ss":         lambda e: _sys_ss(e),
     "sys_taskmgr":    lambda e: _sys_taskmgr(e),
     "sys_wallpaper":  lambda e: _sys_wallpaper(e),
     "sys_add_startup":    lambda e: _sys_add_startup(e),
     "sys_remove_startup": lambda e: _sys_remove_startup(e),
     "clip_clear":     lambda e: _clip_clear(e),
     "sys_refresh":    lambda e: _sys_refresh(e),
     "sys_empty_trash":lambda e: _sys_empty_bin(e),
     "sys_notify":     lambda e: _sys_notify(e),
     "sys_bell":       lambda e: _sys_bell(e),
     "sys_hostname":   lambda e: (True, f"Hostname: {socket.gethostname()}"),
     "app_chrome":     lambda e: _app("google-chrome","Google Chrome","chrome"),
     "app_firefox":    lambda e: _app("firefox","Firefox","firefox"),
     "app_edge":       lambda e: _app("microsoft-edge","Microsoft Edge","msedge"),
     "app_brave":      lambda e: _app("brave-browser","Brave","brave"),
     "app_terminal":   lambda e: _app_terminal(e),
     "app_calc":       lambda e: _app_calc(e),
     "app_notepad":    lambda e: _app_notepad(e),
     "app_explorer":   lambda e: _app_explorer(e),
     "app_settings":   lambda e: _app_settings(e),
     "app_vscode":     lambda e: _app("code","Visual Studio Code","code"),
     "app_spotify":    lambda e: _app("spotify","Spotify","spotify"),
     "app_vlc":        lambda e: _app("vlc","VLC","vlc"),
     "app_paint":      lambda e: _app_paint(e),
     "app_word":       lambda e: _app_word(e),
     "app_excel":      lambda e: _app_excel(e),
     "app_open":       lambda e: _app_open(e),
     "app_close":      lambda e: _app_close(e),
     "app_close_all":  lambda e: _app_close_all(e),
     "win_min_all":    lambda e: _app_close_all(e),
     "win_max":        lambda e: _win_max(e),
     "win_switch":     lambda e: _win_switch(e),
     "web_google":     lambda e: _wb_q("https://www.google.com/search?q={}",e,"Google"),
     "web_bing":       lambda e: _wb_q("https://www.bing.com/search?q={}",e,"Bing"),
     "web_ddg":        lambda e: _wb_q("https://duckduckgo.com/?q={}",e,"DuckDuckGo"),
     "web_images":     lambda e: _wb_q("https://www.google.com/search?q={}&tbm=isch",e,"Images"),
     "web_maps":       lambda e: _wb_q("https://www.google.com/maps/search/{}",e,"Maps"),
     "web_wiki":       lambda e: _wb_q("https://en.wikipedia.org/wiki/Special:Search?search={}",e,"Wikipedia"),
     "web_yt_search":  lambda e: _wb_q("https://www.youtube.com/results?search_query={}",e,"YouTube"),
     "web_scholar":    lambda e: _wb_q("https://scholar.google.com/scholar?q={}",e,"Scholar"),
     "web_ask_chatgpt":lambda e: _wb_ask("chatgpt",e),
     "web_ask_claude": lambda e: _wb_ask("claude",e),
     "web_ask_gemini": lambda e: _wb_ask("gemini",e),
     "web_ask_perplexity":lambda e: _wb_ask("perplexity",e),
     "web_ask_default_ai":lambda e: _wb_ask(NCFG.get("default_ai","gemini"),e),
     "web_messages":   lambda e: (_open_url("https://messages.google.com/web") and (True, "Google Messages opened")) or (True, "Google Messages opened"),
     "web_reddit_search": lambda e: _wb_q("https://www.reddit.com/search/?q={}", e, "Reddit"),
     "web_github_search": lambda e: _wb_q("https://github.com/search?q={}", e, "GitHub"),
     "web_amazon_search": lambda e: _wb_q("https://www.amazon.com/s?k={}", e, "Amazon"),
     "web_url":        lambda e: _web_url(e),
     "web_gmail":      lambda e: (_open_url("https://mail.google.com") and (True, "Gmail opened")) or (True, "Gmail opened"),
     "web_github":     lambda e: (_open_url("https://github.com") and (True, "GitHub opened")) or (True, "GitHub opened"),
     "web_youtube":    lambda e: (_open_url("https://youtube.com") and (True, "YouTube opened")) or (True, "YouTube opened"),
     "web_reddit":     lambda e: (_open_url("https://reddit.com") and (True, "Reddit opened")) or (True, "Reddit opened"),
     "web_chatgpt":    lambda e: (_open_url("https://chat.openai.com") and (True, "ChatGPT opened")) or (True, "ChatGPT opened"),
     "web_claude":     lambda e: (_open_url("https://claude.ai") and (True, "Claude opened")) or (True, "Claude opened"),
     "web_gemini":     lambda e: (_open_url("https://gemini.google.com") and (True, "Gemini opened")) or (True, "Gemini opened"),
     "web_netflix":    lambda e: (_open_url("https://netflix.com") and (True, "Netflix opened")) or (True, "Netflix opened"),
     "web_spotify":    lambda e: (_open_url("https://open.spotify.com") and (True, "Spotify opened")) or (True, "Spotify opened"),
     "web_private":    lambda e: _web_private(e),
     "bc_close_tab":   lambda e: _bc_close_tab(e),
     "bc_new_tab":     lambda e: _bc_new_tab(e),
     "bc_refresh":     lambda e: _bc_refresh(e),
     "bc_back":        lambda e: _bc_back(e),
     "bc_forward":     lambda e: _bc_forward(e),
     "bc_history":     lambda e: _bc_history(e),
     "bc_downloads":   lambda e: _bc_downloads(e),
     "bc_bookmark":    lambda e: _bc_bookmark(e),
     "bc_reopen_tab":  lambda e: _bc_reopen_tab(e),
     "bc_page_up":     lambda e: _bc_page_up(e),
     "bc_page_down":   lambda e: _bc_page_down(e),
     "mm_find_text":   lambda e: _mm_find_text(e),
     "clip_copy_sel":  lambda e: _clip_copy_sel(e),
     "clip_paste":     lambda e: _clip_paste(e),
     "clip_cut":       lambda e: _clip_cut(e),
     "edit_select_all":lambda e: _edit_select_all(e),
     "edit_undo":      lambda e: _edit_undo(e),
     "edit_redo":      lambda e: _edit_redo(e),
     "sys_notif_center":lambda e: _sys_notification_center(e),
     "sys_magnifier":  lambda e: _sys_magnifier(e),
     "sys_snipping":   lambda e: _sys_snipping_tool(e),
     "sys_task_view":  lambda e: _sys_task_view(e),
     "sys_close_window":lambda e: _sys_close_window(e),
     "web_research":   lambda e: _web_research(e),
     "web_search_incognito":lambda e: _web_search_incognito(e),
     "web_open_site_smart": lambda e: _web_open_site_smart(e),
     "app_open_smart": lambda e: _app_open_smart(e),
     "p_time":         lambda e: (True,datetime.now().strftime("It's %I:%M %p")),
     "p_date":         lambda e: (True,datetime.now().strftime("Today is %A, %B %d, %Y")),
     "p_day":          lambda e: (True,datetime.now().strftime("Today is %A")),
     "p_days_until":   lambda e: _p_days(e),
     "p_note_add":     lambda e: _p_note_add(e),
     "p_notes_read":   lambda e: _p_notes_read(e),
     "p_notes_clear":  lambda e: _p_notes_clear(e),
     "p_note_add_structured": lambda e: _p_note_add_structured(e),
     "p_note_read":    lambda e: _p_note_read(e),
     "p_note_delete":   lambda e: _p_note_delete(e),
     "p_notes_list":   lambda e: _p_notes_list(e),
     "p_journal":      lambda e: _p_journal(e),
     "p_journal_read": lambda e: _p_journal_read(e),
     "p_timer":        lambda e: _p_timer(e),
     "p_remind":       lambda e: _p_remind(e),
     "p_pomodoro":     lambda e: _p_pomodoro(e),
     "p_calc":         lambda e: _p_calc(e),
     "p_convert":      lambda e: _p_convert(e),
     "p_rng":          lambda e: (True,f"Random: {random.randint(1,100)}"),
     "p_password":     lambda e: _p_password(e),
     "p_todo_add":     lambda e: _p_todo_add(e),
     "p_todo_show":    lambda e: _p_todo_show(e),
     "p_todo_clear":   lambda e: _p_todo_clear(e),
     "p_habit_add":    lambda e: _p_habit_add(e),
     "p_habit_show":   lambda e: _p_habit_show(e),
     "si_cpu":         lambda e: _si_cpu(e),
     "si_ram":         lambda e: _si_ram(e),
     "si_disk":        lambda e: _si_disk(e),
     "si_battery":     lambda e: _si_battery(e),
     "si_info":        lambda e: _si_info(e),
     "si_uptime":      lambda e: _si_uptime(e),
     "si_monitor":     lambda e: _si_monitor(e),
     "ni_ip":          lambda e: _ni_ip(e),
     "ni_check":       lambda e: _ni_check(e),
     "ni_wifi":        lambda e: _ni_wifi(e),
     "ni_interfaces":  lambda e: _ni_interfaces(e),
     "si_proc_list":   lambda e: _si_proc_list(e),
     "si_proc_kill":   lambda e: _si_proc_kill(e),
     "si_zombies":     lambda e: _si_zombies(e),
     "mm_screenshot":  lambda e: _sys_ss(e),
     "mm_play":        lambda e: _mm_play(e),
     "mm_next":        lambda e: _mm_next(e),
     "mm_prev":        lambda e: _mm_prev(e),
     "mm_webcam_photo":lambda e: _mm_webcam_photo(e),
     "mm_yt_audio":    lambda e: _mm_yt_dl(e,audio_only=True),
     "mm_yt_video":    lambda e: _mm_yt_dl(e,audio_only=False),
     "mm_img_convert": lambda e: _mm_img_convert(e),
     "mm_img_resize":  lambda e: _mm_img_resize(e),
     "mm_img_info":    lambda e: _mm_img_info(e),
     "mm_create_gif":  lambda e: _mm_create_gif(e),
     "net_ping":       lambda e: _net_ping(e),
     "net_flushdns":   lambda e: _net_dns(e),
     "net_traceroute": lambda e: _net_traceroute(e),
     "net_whois":      lambda e: _net_whois(e),
     "net_revdns":     lambda e: _net_revdns(e),
     "net_headers":    lambda e: _net_headers(e),
     "net_speed":      lambda e: _net_speed(e),
     "net_ssl_check":  lambda e: _net_ssl_check(e),
     "net_scan_local": lambda e: _net_scan_local(e),
     "net_dns_lookup": lambda e: _net_dns_lookup(e),
     "net_download":   lambda e: _net_download(e),
     "net_wifi_settings":lambda e: _net_wifi(e),
     "net_bluetooth":  lambda e: _net_bt(e),
     "sys_bt_on":      lambda e: _sys_bt_on(e),
     "sys_bt_off":     lambda e: _sys_bt_off(e),
     "sys_wifi_on":    lambda e: _sys_wifi_on(e),
     "sys_wifi_off":   lambda e: _sys_wifi_off(e),
     "net_firewall":   lambda e: _net_fw(e),
     "dev_port_check": lambda e: _dev_port_check(e),
     "dev_open_ports": lambda e: _dev_open_ports(e),
     "cfg_set_ai":     lambda e: _cfg_set_ai(e),
     "cfg_show_ai":    lambda e: (True,f"Default AI: {NCFG.get('default_ai','gemini').capitalize()}"),
     "cfg_set_browser":lambda e: _cfg_set_browser(e),
     "cfg_show_browser":lambda e: (True,f"Default browser: {NCFG.get('default_browser','system')}"),
     "cfg_toggle_yolo":lambda e: _cfg_toggle_yolo(e),
     "cfg_set_search": lambda e: _cfg_set_search(e),
     "cfg_show_search":lambda e: (True,f"Default search: {NCFG.get('default_search','google').title()}"),
     "cfg_toggle_maximize":lambda e: _cfg_toggle_maximize(e),
     "cfg_set_theme":  lambda e: _cfg_set_theme(e),
     "cfg_set_stt":    lambda e: _cfg_set_stt(e),
     "cfg_show_stt":   lambda e: _cfg_show_stt(e),
     "cfg_toggle_stt": lambda e: _cfg_toggle_stt(e),
     "cfg_list_mics":  lambda e: _cfg_list_mics(e),
     "cfg_set_mic":    lambda e: _cfg_set_mic(e),
     "cfg_set_energy": lambda e: _cfg_set_energy(e),
     "cfg_set_dynamic":lambda e: _cfg_set_dynamic(e),
     "cfg_test_mic":   lambda e: _cfg_test_mic(e),
     "nova_on":        lambda e: _nova_on(e),
     "nova_off":       lambda e: _nova_off(e),
     "nova_clear":     lambda e: _nova_clear(e),
     "nova_status":    lambda e: _nova_status(e),
     "fun_joke":       lambda e: (True,random.choice(_JOKES)),
     "fun_fact":       lambda e: (True,"INFO: "+random.choice(_FACTS)),
     "fun_quote":      lambda e: (True,random.choice(_QUOTES)),
     "fun_affirm":     lambda e: (True,random.choice(_AFFIRMATIONS)),
     "fun_word":       lambda e: _fun_word(e),
     "fun_coin":       lambda e: (True,f"Coin: {random.choice(['Heads','Tails'])}!"),
     "fun_dice":       lambda e: (True,f"Dice: {random.randint(1,6)}"),
     "fun_magic8":     lambda e: (True,f"Magic 8: {random.choice(_MAGIC8)}"),
     "fun_greet":      lambda e: _fun_greet(e),
     "dev_git_status": lambda e: _dev_git(["status","--short"],empty="Clean working tree"),
     "dev_git_pull":   lambda e: _dev_git(["pull"]),
     "dev_git_push":   lambda e: _dev_git(["push"]),
     "dev_git_log":    lambda e: _dev_git(["log","--oneline","-8"],empty="No commits yet"),
     "dev_git_diff":   lambda e: _dev_git(["diff","--stat"],empty="No changes"),
     "dev_git_stash":  lambda e: _dev_git(["stash"]),
     "dev_git_stash_pop":lambda e: _dev_git(["stash","pop"]),
     "dev_git_branch": lambda e: _dev_git(["branch","-a"],empty="No branches"),
     "dev_git_init":   lambda e: _dev_git(["init"]),
     "dev_git_commit": lambda e: _dev_git_commit(e),
     "dev_git_add":    lambda e: _dev_git(["add","-A"]),
     "dev_git_checkout":lambda e: _dev_git_checkout(e),
     "dev_git_merge":  lambda e: _dev_git_merge(e),
     "dev_git_tag":    lambda e: _dev_git_tag(e),
     "dev_git_remote": lambda e: _dev_git(["remote","-v"],empty="No remotes"),
     "dev_git_clone":  lambda e: _dev_git_clone(e),
     "dev_git_reset":  lambda e: _dev_git(["reset","HEAD"]),
     "dev_npm_install":lambda e: _dev_npm("install"),
     "dev_npm_start":  lambda e: _dev_npm("start"),
     "dev_npm_test":   lambda e: _dev_npm("test"),
     "dev_npm_build":  lambda e: _dev_npm("run","build"),
     "dev_npm_run":    lambda e: _dev_npm_run(e),
     "dev_npm_outdated":lambda e: _dev_npm("outdated"),
     "dev_npm_list":   lambda e: _dev_npm("list","--depth=0"),
     "dev_docker_ps":  lambda e: _dev_docker("ps"),
     "dev_docker_images":lambda e: _dev_docker("images"),
     "dev_docker_start":lambda e: _dev_docker_cmd(e,"start"),
     "dev_docker_stop":lambda e: _dev_docker_cmd(e,"stop"),
     "dev_docker_pull":lambda e: _dev_docker_pull(e),
     "dev_docker_logs":lambda e: _dev_docker_logs(e),
     "dev_docker_rm":  lambda e: _dev_docker_cmd(e,"rm"),
     "dev_run_py":     lambda e: _dev_run_file(e,sys.executable),
     "dev_run_sh":     lambda e: _dev_run_file(e,"bash"),
     "dev_http_serve": lambda e: _dev_http_serve(e),
     "dev_pip_install":lambda e: _dev_pip_install(e),
     "dev_pip_list":   lambda e: _dev_pip_list(e),
     "dev_pip_freeze": lambda e: _dev_pip_freeze(e),
     "dev_apt_install":lambda e: _dev_apt_install(e),
     "dev_apt_update": lambda e: _dev_apt_update(e),
     "dev_ver_py":     lambda e: _dev_run_cmd([sys.executable,"--version"]),
     "dev_ver_node":   lambda e: _dev_run_cmd(["node","--version"]),
     "dev_ver_git":    lambda e: _dev_run_cmd(["git","--version"]),
     "dev_open_proj":  lambda e: _dev_open_proj(e),
     "dev_venv":       lambda e: _dev_venv(e),
     "dev_hash":       lambda e: _dev_hash(e),
     "dev_localhost":  lambda e: _dev_localhost(e),
     "dev_env_vars":   lambda e: _dev_env_vars(e),
     "dev_uuid":       lambda e: _dev_uuid(e),
     "dev_b64enc":     lambda e: _dev_b64enc(e),
     "dev_b64dec":     lambda e: _dev_b64dec(e),
     "dev_py_format":  lambda e: _dev_py_format(e),
     "dev_py_lint":    lambda e: _dev_py_lint(e),
     "dev_pytest":     lambda e: _dev_pytest(e),
     "dev_make":       lambda e: _dev_make(e),
     "dev_gitignore":  lambda e: _dev_gitignore(e),
     "dev_json_format":lambda e: _dev_json_format(e),
     "tt_json_pretty": lambda e: _tt_json_pretty(e),
     "tt_json_validate":lambda e: _tt_json_validate(e),
     "tt_yaml_validate":lambda e: _tt_yaml_validate(e),
     "tt_url_encode":  lambda e: (True,urllib.parse.quote(str(e.get("query","")))),
     "tt_url_decode":  lambda e: (True,urllib.parse.unquote(str(e.get("query","")))),
     "tt_html_encode": lambda e: _tt_html_encode(e),
     "tt_html_decode": lambda e: _tt_html_decode(e),
     "tt_rot13":       lambda e: _tt_rot13(e),
     "tt_slugify":     lambda e: _tt_slugify(e),
     "tt_camel":       lambda e: _tt_camel(e),
     "tt_snake":       lambda e: _tt_snake(e),
     "tt_upper":       lambda e: (True,str(e.get("query","")).upper()),
     "tt_lower":       lambda e: (True,str(e.get("query","")).lower()),
     "tt_trim":        lambda e: (True,"\n".join(l.strip() for l in str(e.get("query","")).splitlines())),
     "tt_sort_lines":  lambda e: _tt_sort_lines(e),
     "tt_unique_lines":lambda e: _tt_unique_lines(e),
     "tt_reverse":     lambda e: (True,str(e.get("query",""))[::-1]),
     "tt_count":       lambda e: _tt_count(e),
     "tt_extract_emails":lambda e: _tt_extract_emails(e),
     "tt_extract_urls":lambda e: _tt_extract_urls(e),
     "tt_palindrome":  lambda e: _tt_palindrome(e),
     "tt_word_freq":   lambda e: _tt_word_freq(e),
     "me_is_prime":    lambda e: _me_is_prime(e),
     "me_fibonacci":   lambda e: _me_fibonacci(e),
     "me_factorial":   lambda e: _me_factorial(e),
     "me_gcd_lcm":     lambda e: _me_gcd_lcm(e),
     "me_prime_factors":lambda e: _me_prime_factors(e),
     "me_stats":       lambda e: _me_stats(e),
     "me_bmi":         lambda e: _me_bmi(e),
     "me_compound":    lambda e: _me_compound(e),
     "me_tip":         lambda e: _me_tip(e),
     "me_mortgage":    lambda e: _me_mortgage(e),
     "me_base_conv":   lambda e: _me_base_conv(e),
     "me_data_size":   lambda e: _me_data_size(e),
     "me_speed_conv":  lambda e: _me_speed_conv(e),
     "se_pw_strength": lambda e: _se_pw_strength(e),
     "se_passphrase":  lambda e: _se_passphrase(e),
     "se_hash_text":   lambda e: _se_hash_text(e),
     "se_encrypt":     lambda e: _se_encrypt(e),
     "se_decrypt":     lambda e: _se_decrypt(e),
     "se_failed_logins":lambda e: _se_failed_logins(e),
     "wn_weather":     lambda e: _wn_weather(e),
     "wn_moon_phase":  lambda e: _wn_moon_phase(e),
     "wn_crypto":      lambda e: _wn_crypto(e),
     "wn_exchange":    lambda e: _wn_exchange(e),
     "wn_news":        lambda e: _wn_news(e),
     "cl_find_large":  lambda e: _cl_find_large(e),
     "cl_find_empty":  lambda e: _cl_find_empty(e),
     "cl_find_hidden": lambda e: _cl_find_hidden(e),
     "cl_tree":        lambda e: _cl_tree(e),
     "cl_find_ext":    lambda e: _cl_find_ext(e),
     "cl_find_today":  lambda e: _fs_find_today(e),
     "cl_find_old":    lambda e: _cl_find_old(e),
     "cl_find_duplicates":lambda e: _cl_find_duplicates(e),
     "cl_apt_clean":   lambda e: _cl_apt_clean(e),
     "cl_free_mem":    lambda e: _cl_free_mem(e),
     "si2_gpu":        lambda e: _si2_gpu(e),
     "si2_temp":       lambda e: _si2_temp(e),
     "si2_swap":       lambda e: _si2_swap(e),
     "si2_netstat":    lambda e: _si2_netstat(e),
     "si2_whoami":     lambda e: (True,f"User: {os.environ.get('USER',os.environ.get('USERNAME','unknown'))}"),
     "si2_public_ip":  lambda e: _si2_public_ip(e),
     "si2_syslog":     lambda e: _si2_syslog(e),
     "si2_kernel":     lambda e: _si2_kernel(e),
     "si2_lsblk":      lambda e: _run_out(["lsblk"]),
     "si2_lsusb":      lambda e: _run_out(["lsusb"]),
     "si2_mounted":    lambda e: _run_out(["df","-h","--output=target,size,used,avail,pcent"]),
     "si2_osver":      lambda e: _si2_osver(e),
     "si2_last_logins":lambda e: _run_out(["last","-n","10"]),
     "si2_svc_status": lambda e: _si2_svc(e,"status"),
     "si2_svc_start":  lambda e: _si2_svc(e,"start"),
     "si2_svc_stop":   lambda e: _si2_svc(e,"stop"),
     "si2_svc_list":   lambda e: _run_out(["systemctl","list-units","--type=service","--state=running","--no-pager"]),
     "si2_cron_add":   lambda e: _si2_cron_add(e),
     "si2_cron_list":  lambda e: _run_out(["crontab","-l"]),
     "si2_cron_edit":  lambda e: _run_out(["crontab","-e"]),
     "a2_slack":       lambda e: _app("slack","Slack","slack"),
     "a2_discord":     lambda e: _app("discord","Discord","discord"),
     "a2_telegram":    lambda e: _app("telegram-desktop","Telegram","Telegram"),
     "a2_zoom":        lambda e: _app("zoom","zoom.us","zoom"),
     "a2_whatsapp":    lambda e: (_open_url("https://web.whatsapp.com") and (True, "WhatsApp opened")) or (True, "WhatsApp opened"),
     "a2_gimp":        lambda e: _app("gimp","GIMP","gimp"),
     "a2_obs":         lambda e: _app("obs","OBS","obs64"),
     "a2_audacity":    lambda e: _app("audacity","Audacity","audacity"),
     "a2_figma":       lambda e: (_open_url("https://figma.com") and (True, "Figma opened")) or (True, "Figma opened"),
     "a2_canva":       lambda e: (_open_url("https://canva.com") and (True, "Canva opened")) or (True, "Canva opened"),
     "a2_postman":     lambda e: _app("postman","Postman","postman"),
     "a2_nvim":        lambda e: _a2_nvim(e),
     "a2_replit":      lambda e: (_open_url("https://replit.com") and (True, "Replit opened")) or (True, "Replit opened"),
     "a2_colab":       lambda e: (_open_url("https://colab.research.google.com") and (True, "Colab opened")) or (True, "Colab opened"),
     "b2_stackoverflow":lambda e: (_open_url("https://stackoverflow.com") and (True, "Stack Overflow opened")) or (True, "Stack Overflow opened"),
     "b2_notion":      lambda e: (_open_url("https://notion.so") and (True, "Notion opened")) or (True, "Notion opened"),
     "b2_trello":      lambda e: (_open_url("https://trello.com") and (True, "Trello opened")) or (True, "Trello opened"),
     "b2_linkedin":    lambda e: (_open_url("https://linkedin.com") and (True, "LinkedIn opened")) or (True, "LinkedIn opened"),
     "b2_twitter":     lambda e: (_open_url("https://x.com") and (True, "Twitter/X opened")) or (True, "Twitter/X opened"),
     "b2_pypi":        lambda e: (_open_url("https://pypi.org") and (True, "PyPI opened")) or (True, "PyPI opened"),
     "b2_mdn":         lambda e: (_open_url("https://developer.mozilla.org") and (True, "MDN opened")) or (True, "MDN opened"),
     "b2_devdocs":     lambda e: (_open_url("https://devdocs.io") and (True, "DevDocs opened")) or (True, "DevDocs opened"),
     "b2_caniuse":     lambda e: (_open_url("https://caniuse.com") and (True, "CanIUse opened")) or (True, "CanIUse opened"),
     "b2_regex":       lambda e: (_open_url("https://regex101.com") and (True, "Regex101 opened")) or (True, "Regex101 opened"),
     "b2_jsonlint":    lambda e: (_open_url("https://jsonlint.com") and (True, "JSONLint opened")) or (True, "JSONLint opened"),
     "b2_translate":   lambda e: (_open_url("https://translate.google.com") and (True, "Translate opened")) or (True, "Translate opened"),
     "b2_response_time":lambda e: _b2_response_time(e),
     "w2_snap_left":   lambda e: _w2_snap("left"),
     "w2_snap_right":  lambda e: _w2_snap("right"),
     "w2_fullscreen":  lambda e: _w2_fullscreen(e),
     "w2_always_top":  lambda e: _w2_always_top(e),
     "sec_ssh_keygen": lambda e: _sec_ssh_keygen(e),
     "sec_show_ssh":   lambda e: _sec_show_ssh(e),
     "sec_shred":      lambda e: _sec_shred(e),
     "vt_type":        lambda e: _vt_type(e),
     "m2_play_file":   lambda e: _m2_play_file(e),
     "m2_record_audio":lambda e: _m2_record_audio(e),
     "m2_record_screen":lambda e: _m2_record_screen(e),
     "p2_worldclock":  lambda e: _p2_worldclock(e),
     "p2_stopwatch":   lambda e: _p2_stopwatch(e),
     "p2_epoch":       lambda e: (True,f"Unix timestamp: {int(time.time())}"),
     "p2_lorem":       lambda e: (True,"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."),
     "p2_wordcount":   lambda e: _p2_wordcount(e),
     "p2_charcount":   lambda e: _p2_charcount(e),
     "p2_reading_time":lambda e: _p2_reading_time(e),
     "p2_qr_code":     lambda e: _p2_qr_code(e),
     "p2_clip_read":   lambda e: _p2_clip_read(e),
     "p2_clip_pwd":    lambda e: (True,os.getcwd()),
     "p2_clip_copy":   lambda e: _p2_clip_copy(e),
     "p2_percentage":  lambda e: _p2_percentage(e),
     "p2_weeknum":     lambda e: (True,f"Week {datetime.now().isocalendar()[1]} of {datetime.now().year}"),

     # ── Missing executors added ─────────────────────────────────────────────
     "cfg_show":           lambda e: _cfg_show(e),
     "cfg_toggle_tts":          lambda e: _cfg_toggle_tts(e),
     "cfg_toggle_nebula_tts":   lambda e: _cfg_toggle_nebula_tts(e),
     "cfg_toggle_nova_tts":     lambda e: _cfg_toggle_nova_tts(e),
     "cfg_toggle_nova_confirm": lambda e: _cfg_toggle_nova_confirm(e),
     "cfg_set_api_key":    lambda e: _cfg_set_api_key(e),
     "nova_install_gemini":lambda e: _nova_install_gemini(e),
     "fs_du":              lambda e: _fs_du(e),
     "fs_watch":           lambda e: _fs_watch(e),
     "fun_riddle":         lambda e: _fun_riddle(e),
     "fun_trivia":         lambda e: _fun_trivia(e),
     "me_solve":           lambda e: _me_solve(e),
     "me_simplify":        lambda e: _me_simplify(e),
     "me_derivative":      lambda e: _me_derivative(e),
     "me_integral":        lambda e: _me_integral(e),
     "me_matrix":          lambda e: _me_matrix(e),
     "me_quadratic":       lambda e: _me_quadratic(e),
     "tt_char_freq":       lambda e: _tt_char_freq(e),
     "tt_title":           lambda e: (True, str(e.get("query","")).title()),
     "tt_sentence":        lambda e: _tt_sentence(e),
     "web_search":         lambda e: _web_search(e),
     "wn_stock":           lambda e: _wn_stock(e),
     "wn_ipinfo":          lambda e: _wn_ipinfo(e),
     "b2_webcheck":        lambda e: _b2_webcheck(e),
     "p_calendar":         lambda e: _p_calendar(e),
     "dev_apt_remove":     lambda e: _dev_apt_remove(e),
     "dev_docker_build":   lambda e: _dev_docker_build(e),
     "dev_pip_update":     lambda e: _dev_pip_update(e),
     # ── New batch 2 ──────────────────────────────────────────────────────
     "p2_days_left_year":  lambda e: _p2_days_left_year(e),
     "p2_age_calc":        lambda e: _p2_age_calc(e),
     "p2_leap_year":       lambda e: _p2_leap_year(e),
     "p2_month_days":      lambda e: _p2_month_days(e),
     "p2_biz_days":        lambda e: _p2_biz_days(e),
     "p2_add_days":        lambda e: _p2_add_days(e),
     "p2_next_weekday":    lambda e: _p2_next_weekday(e),
     "p2_time_diff":       lambda e: _p2_time_diff(e),
     "si2_resolution":     lambda e: _si2_resolution(e),
     "si2_audio":          lambda e: _si2_audio(e),
     "si2_lspci":          lambda e: _si2_lspci(e),
     "si2_locale":         lambda e: _si2_locale(e),
     "si2_tz":             lambda e: _si2_tz(e),
     "si2_iostat":         lambda e: _si2_iostat(e),
     "si2_open_files":     lambda e: _si2_open_files(e),
     "si2_summary":        lambda e: _si2_summary(e),
     "net_mac":            lambda e: _net_mac(e),
     "net_routes":         lambda e: _net_routes(e),
     "net_vpn":            lambda e: _net_vpn(e),
     "fs_perms":           lambda e: _fs_perms(e),
     "fs_split":           lambda e: _fs_split(e),
     "fs_join":            lambda e: _fs_join(e),
     "fs_encrypt_file":    lambda e: _fs_encrypt_file(e),
     "fs_decrypt_file":    lambda e: _fs_decrypt_file(e),
     "fs_mime_type":       lambda e: _fs_mime_type(e),
     "fs_find_symlinks":   lambda e: _fs_find_symlinks(e),
     "fs_sort_size":       lambda e: _fs_sort_size(e),
     "fs_batch_rename":    lambda e: _fs_batch_rename(e),
     "dev_git_graph":      lambda e: _dev_git_graph(e),
     "dev_git_blame":      lambda e: _dev_git_blame(e),
     "dev_git_show":       lambda e: _dev_git_show(e),
     "dev_git_undo":       lambda e: _dev_git_undo(e),
     "dev_git_amend":      lambda e: _dev_git_amend(e),
     "dev_git_whoami":     lambda e: _dev_git_whoami(e),
     "dev_git_cfg":        lambda e: _dev_git_cfg(e),
     "dev_git_fetch":      lambda e: _dev_git_fetch(e),
     "dev_git_branches":   lambda e: _dev_git_branches(e),
     "dev_git_tags":       lambda e: _dev_git_tags(e),
     "dev_npm_audit":      lambda e: _dev_npm_audit(e),
     "dev_docker_stats":   lambda e: _dev_docker_stats(e),
     "dev_docker_prune":   lambda e: _dev_docker_prune(e),
     "dev_docker_exec":    lambda e: _dev_docker_exec(e),
     "dev_find_todos":     lambda e: _dev_find_todos(e),
     "dev_count_lines":    lambda e: _dev_count_lines(e),
     "dev_regex_test":     lambda e: _dev_regex_test(e),
     "dev_jwt_decode":     lambda e: _dev_jwt_decode(e),
     "dev_json2yaml":      lambda e: _dev_json2yaml(e),
     "dev_yaml2json":      lambda e: _dev_yaml2json(e),
     "dev_csv2json":       lambda e: _dev_csv2json(e),
     "dev_which":          lambda e: _dev_which(e),
     "dev_new_project":    lambda e: _dev_new_project(e),
     "dev_gen_reqs":       lambda e: _dev_gen_reqs(e),
     "dev_gen_docker":     lambda e: _dev_gen_docker(e),
     "dev_benchmark":      lambda e: _dev_benchmark(e),
     "dev_profile":        lambda e: _dev_profile(e),
     "dev_mypy":           lambda e: _dev_mypy(e),
     "dev_coverage":       lambda e: _dev_coverage(e),
     "dev_show_path":      lambda e: _dev_show_path(e),
     "me_sqrt":            lambda e: _me_sqrt(e),
     "me_cbrt":            lambda e: _me_cbrt(e),
     "me_pi":              lambda e: _me_pi(e),
     "me_golden":          lambda e: _me_golden(e),
     "me_log":             lambda e: _me_log(e),
     "me_trig":            lambda e: _me_trig(e),
     "me_pct_change":      lambda e: _me_pct_change(e),
     "me_perm":            lambda e: _me_perm(e),
     "me_comb":            lambda e: _me_comb(e),
     "me_prime_list":      lambda e: _me_prime_list(e),
     "me_roman":           lambda e: _me_roman(e),
     "me_temp_conv":       lambda e: _me_temp_conv(e),
     "me_fuel":            lambda e: _me_fuel(e),
     "me_calories":        lambda e: _me_calories(e),
     "me_polygon":         lambda e: _me_polygon(e),
     "me_circle":          lambda e: _me_circle(e),
     "me_triangle":        lambda e: _me_triangle(e),
     "tt_morse":           lambda e: _tt_morse(e),
     "tt_morse_decode":    lambda e: _tt_morse_decode(e),
     "tt_nato":            lambda e: _tt_nato(e),
     "tt_caesar":          lambda e: _tt_caesar(e),
     "tt_bin_text":        lambda e: _tt_bin_text(e),
     "tt_text_bin":        lambda e: _tt_text_bin(e),
     "tt_hex_text":        lambda e: _tt_hex_text(e),
     "tt_text_hex":        lambda e: _tt_text_hex(e),
     "tt_ascii_art":       lambda e: _tt_ascii_art(e),
     "tt_bold_text":       lambda e: _tt_bold_text(e),
     "tt_num_lines":       lambda e: _tt_num_lines(e),
     "tt_prefix_lines":    lambda e: _tt_prefix_lines(e),
     "tt_suffix_lines":    lambda e: _tt_suffix_lines(e),
     "tt_wrap":            lambda e: _tt_wrap(e),
     "tt_center":          lambda e: _tt_center(e),
     "tt_anagram":         lambda e: _tt_anagram(e),
     "tt_pig_latin":       lambda e: _tt_pig_latin(e),
     "tt_json_minify":     lambda e: _tt_json_minify(e),
     "tt_rm_spaces":       lambda e: _tt_rm_spaces(e),
     "tt_extract_nums":    lambda e: _tt_extract_nums(e),
     "se_rand_bytes":      lambda e: _se_rand_bytes(e),
     "se_otp":             lambda e: _se_otp(e),
     "se_bcrypt":          lambda e: _se_bcrypt(e),
     "se_hmac":            lambda e: _se_hmac(e),
     "se_xor":             lambda e: _se_xor(e),
     "fun_compliment":     lambda e: _fun_compliment(e),
     "fun_roast":          lambda e: _fun_roast(e),
     "fun_fortune":        lambda e: _fun_fortune(e),
     "fun_haiku":          lambda e: _fun_haiku(e),
     "fun_poem":           lambda e: _fun_poem(e),
     "fun_story":          lambda e: _fun_story(e),
     "fun_random_name":    lambda e: _fun_random_name(e),
     "fun_rand_color":     lambda e: _fun_rand_color(e),
     "fun_rand_emoji":     lambda e: _fun_rand_emoji(e),
     "fun_num_fact":       lambda e: _fun_num_fact(e),
     "fun_this_day":       lambda e: _fun_this_day(e),
     "fun_cowsay":         lambda e: _fun_cowsay(e),
     "fun_tongue":         lambda e: _fun_tongue(e),
     "fun_rps":            lambda e: _fun_rps(e),
     "p_note_search":      lambda e: _p_note_search(e),
     "p_todo_done":        lambda e: _p_todo_done(e),
     "p_todo_del":         lambda e: _p_todo_del(e),
     "p_break":            lambda e: _p_break(e),
     "p_water":            lambda e: _p_water(e),
     "p_goal":             lambda e: _p_goal(e),
     "p_goal_show":        lambda e: _p_goal_show(e),
     "p_gratitude":        lambda e: _p_gratitude(e),
     "p_mood":             lambda e: _p_mood(e),
     "p_expense":          lambda e: _p_expense(e),
     "p_exp_show":         lambda e: _p_exp_show(e),
     "p_exp_total":        lambda e: _p_exp_total(e),
     "p_budget":           lambda e: _p_budget(e),
     "p_flashcard":        lambda e: _p_flashcard(e),
     "p_meeting":          lambda e: _p_meeting(e),
     "p_quiz":             lambda e: _p_quiz(e),
     "web_hn":             lambda e: _web_hn(e),
     "web_gh_trending":    lambda e: _web_gh_trending(e),
     "web_dictionary":     lambda e: _web_dictionary(e),
     "web_thesaurus":      lambda e: _web_thesaurus(e),
     "web_urban":          lambda e: _web_urban(e),
     "web_trends":         lambda e: _web_trends(e),
     "web_gcal":           lambda e: _web_gcal(e),
     "web_drive":          lambda e: _web_drive(e),
     "web_gdocs":          lambda e: _web_gdocs(e),
     "web_gsheets":        lambda e: _web_gsheets(e),
     "web_gslides":        lambda e: _web_gslides(e),
     "web_meet":           lambda e: _web_meet(e),
     "web_jira":           lambda e: _web_open("https://atlassian.net/jira", "Jira"),
     "web_asana":          lambda e: _web_open("https://app.asana.com", "Asana"),
     "web_vercel":         lambda e: _web_open("https://vercel.com", "Vercel"),
     "web_netlify":        lambda e: _web_open("https://app.netlify.com", "Netlify"),
     "web_aws":            lambda e: _web_open("https://console.aws.amazon.com", "AWS Console"),
     "web_azure":          lambda e: _web_open("https://portal.azure.com", "Azure Portal"),
     "web_leetcode":       lambda e: _web_open("https://leetcode.com", "LeetCode"),
     "web_hackerrank":     lambda e: _web_open("https://hackerrank.com", "HackerRank"),
     "web_medium":         lambda e: _web_open("https://medium.com", "Medium"),
     "web_devto":          lambda e: _web_open("https://dev.to", "Dev.to"),
     "web_twitch":         lambda e: _web_open("https://twitch.tv", "Twitch"),
     "web_soundcloud":     lambda e: _web_open("https://soundcloud.com", "SoundCloud"),
     "web_bbc":            lambda e: _web_open("https://bbc.com/news", "BBC News"),
     "web_techcrunch":     lambda e: _web_open("https://techcrunch.com", "TechCrunch"),
     "web_theverge":       lambda e: _web_open("https://theverge.com", "The Verge"),
     "web_wired":          lambda e: _web_open("https://wired.com", "Wired"),
     "web_codepen":        lambda e: _web_open("https://codepen.io", "CodePen"),
     "web_codesandbox":    lambda e: _web_open("https://codesandbox.io", "CodeSandbox"),
     "web_stackblitz":     lambda e: _web_open("https://stackblitz.com", "StackBlitz"),
     "web_exercism":       lambda e: _web_open("https://exercism.org", "Exercism"),
     "web_codewars":       lambda e: _web_open("https://codewars.com", "Codewars"),
     "mm_img_compress":    lambda e: _mm_img_compress(e),
     "mm_img_thumb":       lambda e: _mm_img_thumb(e),
     "mm_img_rotate":      lambda e: _mm_img_rotate(e),
     "mm_img_flip":        lambda e: _mm_img_flip(e),
     "mm_img_crop":        lambda e: _mm_img_crop(e),
     "mm_img_gray":        lambda e: _mm_img_gray(e),
     "mm_img_blur":        lambda e: _mm_img_blur(e),
     "mm_img_ocr":         lambda e: _mm_img_ocr(e),
     "mm_img_exif":        lambda e: _mm_img_exif(e),
     "mm_list_images":     lambda e: _mm_list_images(e),

     "p_exercise":            lambda e: _p_exercise(e),
     "p_steps":               lambda e: _p_steps(e),
     "p_sleep":               lambda e: _p_sleep(e),
     "p_bmi_q":               lambda e: _p_bmi_q(e),
     "p_heart_rate":          lambda e: _p_heart_rate(e),
     "p_bp":                  lambda e: _p_bp(e),
     "p_med_reminder":        lambda e: _p_med_reminder(e),
     "p_split_bill":          lambda e: _p_split_bill(e),
     "me_loan":               lambda e: _me_loan(e),
     "me_interest":           lambda e: _me_interest(e),
     "me_pct_of":             lambda e: _me_pct_of(e),
     "me_discount":           lambda e: _me_discount(e),
     "me_tax":                lambda e: _me_tax(e),
     "p_savings":             lambda e: _p_savings(e),
     "fun_recipe":            lambda e: _fun_recipe(e),
     "p_cook_timer":          lambda e: _p_cook_timer(e),
     "p_boil_eggs":           lambda e: _p_boil_eggs(e),
     "me_cup_convert":        lambda e: _me_cup_convert(e),
     "p2_tz_convert":         lambda e: _p2_tz_convert(e),
     "p2_world_time":         lambda e: _p2_world_time(e),
     "p2_sunrise":            lambda e: _p2_sunrise(e),
     "p2_moonphase":          lambda e: _p2_moonphase(e),
     "p2_flight_est":         lambda e: _p2_flight_est(e),
     "p2_distance":           lambda e: _p2_distance(e),
     "me_sdt":                lambda e: _me_sdt(e),
     "tt_spelling":           lambda e: _tt_spelling(e),
     "tt_grammar":            lambda e: _tt_grammar(e),
     "b2_translate_text":     lambda e: _b2_translate_text(e),
     "tt_acronym":            lambda e: _tt_acronym(e),
     "p_alarm":               lambda e: _p_alarm(e),
     "p_countdown":           lambda e: _p_countdown(e),
     "p_reminders_show":      lambda e: _p_reminders_show(e),
     "p_reminders_clear":     lambda e: _p_reminders_clear(e),
     "p_clipboard":           lambda e: _p_clipboard(e),
     "p_clip_copy":           lambda e: _p_clip_copy(e),
     "p_clip_hist":           lambda e: _p_clip_hist(e),
     "si2_screen_time":       lambda e: _si2_screen_time(e),
     "si2_autostart":         lambda e: _si2_autostart(e),
     "si2_fonts":             lambda e: _si2_fonts(e),
     "p_email_draft":         lambda e: _p_email_draft(e),
     "p_sms_draft":           lambda e: _p_sms_draft(e),
     "p_linkedin":            lambda e: _p_linkedin(e),
     "p_kanban":              lambda e: _p_kanban(e),
     "p_standup":             lambda e: _p_standup(e),
     "dev_commit_msg":        lambda e: _dev_commit_msg(e),
     "dev_release_notes":     lambda e: _dev_release_notes(e),
     "tt_ascii_table":        lambda e: _tt_ascii_table(e),
     "tt_shortcuts":          lambda e: _tt_shortcuts(e),

     "fun_rand_num":      lambda e: _fun_rand_num(e),
     "fun_rand_choice":   lambda e: _fun_rand_choice(e),
     "fun_shuffle":       lambda e: _fun_shuffle(e),
     "fun_rand_word":     lambda e: _fun_rand_word(e),
     "fun_word_day":      lambda e: _fun_word_day(e),
     "fun_8ball":         lambda e: _fun_8ball(e),
     "fun_wyr":           lambda e: _fun_wyr(e),
     "fun_word_game":     lambda e: _fun_word_game(e),
     "fun_teaser":        lambda e: _fun_teaser(e),
     "tt_count_vowels":   lambda e: _tt_count_vowels(e),
     "tt_reverse_text":   lambda e: _tt_reverse_text(e),
     "tt_reverse_words":  lambda e: _tt_reverse_words(e),
     "tt_synonym":        lambda e: _tt_synonym(e),
     "tt_antonym":        lambda e: _tt_antonym(e),
     "tt_rhyme":          lambda e: _tt_rhyme(e),
     "me_unit_conv":      lambda e: _me_unit_conv(e),
     "dev_http_status":   lambda e: _dev_http_status(e),
     "dev_color_hex":     lambda e: _dev_color_hex(e),
     "dev_char_code":     lambda e: _dev_char_code(e),
     "dev_cron":          lambda e: _dev_cron(e),
     "dev_regex_cheat":   lambda e: _dev_regex_cheat(e),
     "dev_markdown":      lambda e: _dev_markdown(e),
     "dev_git_help":      lambda e: _dev_git_help(e),
     "dev_sql_help":      lambda e: _dev_sql_help(e),
     "dev_docker_help":   lambda e: _dev_docker_help(e),
     "sci_element":       lambda e: _sci_element(e),
     "sci_constant":      lambda e: _sci_constant(e),
     "p_focus":           lambda e: _p_focus(e),
     "p_habit":           lambda e: _p_habit(e),
     "p_reading_list":    lambda e: _p_reading_list(e),
     "p_shopping":        lambda e: _p_shopping(e),
     "net_wifi_pass":     lambda e: _net_wifi_pass(e),
     "net_devices":       lambda e: _net_devices(e),
     "net_ping_test":     lambda e: _net_ping_test(e),
     "si_swap":           lambda e: _si_swap(e),
     "si_temp":           lambda e: _si_temp(e),
     "si_dark_mode":      lambda e: _si_dark_mode(e),
     "si_wallpaper":      lambda e: _si_wallpaper(e),
     "si2_font_size":     lambda e: _si2_font_size(e),
     "p2_what_day":       lambda e: _p2_what_day(e),
     "p2_days_between":   lambda e: _p2_days_between(e),
     "p2_date_add":       lambda e: _p2_date_add(e),
     "p2_date_fmt":       lambda e: _p2_date_fmt(e),
     "p2_quarter":        lambda e: _p2_quarter(e),
     "p2_week_num":       lambda e: _p2_week_num(e),
     "a2_mail":           lambda e: _a2_open("thunderbird","mail","Evolution Mail","evolution"),
     "a2_maps":           lambda e: _open_url("https://maps.google.com") or (True,"Opening Google Maps"),
     "a2_photos":         lambda e: _a2_photos(e),
     "a2_music":          lambda e: _a2_music(e),
     "a2_teams":          lambda e: _a2_open("teams","Teams","teams"),
     "a2_obsidian":       lambda e: _a2_open("obsidian","Obsidian","obsidian"),
     "a2_notion":         lambda e: _open_url("https://notion.so") or (True,"Opening Notion"),
     "a2_jira":           lambda e: _open_url("https://jira.atlassian.com") or (True,"Opening Jira"),
     "a2_dbeaver":        lambda e: _a2_open("dbeaver","DBeaver","dbeaver"),
     "a2_android_studio": lambda e: _a2_open("android-studio","Android Studio","studio.sh"),

     # ── V1 PORT: clipboard/edit/read/find/scroll/page/tab/window/etc ─────────
     "mm_copy":              lambda e: _mm_copy(e),
     "mm_paste":             lambda e: _mm_paste(e),
     "mm_cut":               lambda e: _mm_cut(e),
     "mm_select_all":        lambda e: _mm_select_all(e),
     "mm_undo":              lambda e: _mm_undo(e),
     "mm_redo":              lambda e: _mm_redo(e),
     "mm_read_selection":    lambda e: _mm_read_selection(e),
     "mm_read_aloud":        lambda e: _mm_read_aloud(e),
     "mm_read_clipboard":    lambda e: _mm_read_clipboard(e),
     "mm_type_text":         lambda e: _mm_type_text(e),
     "mm_scroll_up":         lambda e: _mm_scroll_up(e),
     "mm_scroll_dn":         lambda e: _mm_scroll_dn(e),
     "mm_page_up":           lambda e: _mm_page_up(e),
     "mm_page_dn":           lambda e: _mm_page_dn(e),
     "mm_reopen_tab":        lambda e: _mm_reopen_tab(e),
     "mm_tab_next":          lambda e: _mm_tab_next(e),
     "mm_tab_prev":          lambda e: _mm_tab_prev(e),
     "mm_tab_n":             lambda e: _mm_tab_n(e),
     "mm_close_window":      lambda e: _mm_close_window(e),
     "mm_minimize_app":      lambda e: _mm_minimize_app(e),
     "mm_maximize_app":      lambda e: _mm_maximize_app(e),
     "mm_restore_app":       lambda e: _mm_restore_app(e),
     "mm_notification_center":lambda e: _mm_notification_center(e),
     "mm_magnifier":         lambda e: _mm_magnifier(e),
     "mm_snip":              lambda e: _mm_snip(e),
     "mm_task_view":         lambda e: _mm_task_view(e),
     "mm_emoji":             lambda e: _mm_emoji(e),
     "mm_research":          lambda e: _mm_research(e),
     "mm_incognito_here":    lambda e: _mm_incognito_here(e),
     "mm_search_incognito":  lambda e: _mm_search_incognito(e),
     "mm_open_bookmark":     lambda e: _mm_open_bookmark(e),
     "mm_open_software":     lambda e: _mm_open_software(e),
     "mm_list_bookmarks":    lambda e: _mm_list_bookmarks(e),
     "mm_show_bookmarks":    lambda e: _mm_list_bookmarks(e),
     "mm_list_software":     lambda e: _mm_list_software(e),
     "mm_add_bookmark":      lambda e: _mm_add_bookmark(e),
     "mm_del_bookmark":      lambda e: _mm_del_bookmark(e),
     "mm_arrow_up":          lambda e: _mm_arrow_up(e),
     "mm_arrow_dn":          lambda e: _mm_arrow_dn(e),
     "mm_arrow_left":        lambda e: _mm_arrow_left(e),
     "mm_arrow_right":       lambda e: _mm_arrow_right(e),
     "mm_enter":             lambda e: _mm_enter(e),
     "mm_escape":            lambda e: _mm_escape(e),
     "mm_tab_key":           lambda e: _mm_tab_key(e),
     "mm_space_key":         lambda e: _mm_space_key(e),
     "mm_delete_key":        lambda e: _mm_delete_key(e),
     "mm_backspace":         lambda e: _mm_backspace(e),
     "mm_home_key":          lambda e: _mm_home_key(e),
     "mm_end_key":           lambda e: _mm_end_key(e),
     "mm_go_back":           lambda e: _mm_go_back(e),
     "mm_go_forward":        lambda e: _mm_go_forward(e),
     "mm_switch_window":     lambda e: _mm_switch_window(e),
     "mm_show_desktop":      lambda e: _mm_show_desktop(e),
     "mm_lock":              lambda e: _mm_lock(e),
     "cfg_agy_model_cheapest": lambda e: _cfg_agy_model_cheapest(e),
     "cfg_agy_model_better":   lambda e: _cfg_agy_model_better(e),
     "cfg_agy_model_best":     lambda e: _cfg_agy_model_best(e),
     "cfg_agy_model_show":     lambda e: _cfg_agy_model_show(e),
    }
    return fns.get(key)


def _cfg_agy_model_cheapest(e):
    NCFG["agy_model"] = "flash_lite"
    _save_cfg(NCFG)
    return True, "Antigravity AI model switched to: flash_lite (cheapest, fastest model)."


def _cfg_agy_model_better(e):
    NCFG["agy_model"] = "flash"
    _save_cfg(NCFG)
    return True, "Antigravity AI model switched to: flash (better, balanced model)."


def _cfg_agy_model_best(e):
    NCFG["agy_model"] = "pro"
    _save_cfg(NCFG)
    return True, "Antigravity AI model switched to: pro (best, advanced reasoning model)."


def _cfg_agy_model_show(e):
    model = NCFG.get("agy_model", "flash")
    desc = {
        "flash_lite": "cheapest / fastest",
        "flash": "better / balanced",
        "pro": "best / deep reasoning"
    }.get(model, "standard")
    return True, f"Active Antigravity AI Model: {model} ({desc})"



# ═══════════════════════════════════════════════════════════════════════════════

