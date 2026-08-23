"""
Nebula v9 — Media, Webcam, Screenshot, Window, and Clipboard Executors
"""
import os
import time
import subprocess
from pathlib import Path
from typing import Tuple

from config import IS_WIN, IS_MAC, IS_LINUX
from executors.common import _send_keys, _run


# ── Consolidated Clipboard & Macro Operations ─────────────────────────────────
def _clip_copy_sel(e) -> Tuple[bool, str]:
    """Copy current selection to clipboard."""
    _send_keys("ctrl+c" if (IS_WIN or IS_LINUX) else "command+c")
    return True, "Copied"


def _mm_copy(e) -> Tuple[bool, str]:
    """Delegates to consolidated clipboard copy."""
    return _clip_copy_sel(e)


def _clip_cut(e) -> Tuple[bool, str]:
    """Cut current selection to clipboard."""
    _send_keys("ctrl+x" if (IS_WIN or IS_LINUX) else "command+x")
    return True, "Cut"


def _mm_cut(e) -> Tuple[bool, str]:
    """Delegates to consolidated clipboard cut."""
    return _clip_cut(e)


def _clip_paste(e) -> Tuple[bool, str]:
    """Paste clipboard contents."""
    _send_keys("ctrl+v" if (IS_WIN or IS_LINUX) else "command+v")
    return True, "Pasted"


def _mm_paste(e) -> Tuple[bool, str]:
    """Delegates to consolidated clipboard paste."""
    return _clip_paste(e)


def _mm_select_all(e) -> Tuple[bool, str]:
    _send_keys("ctrl+a" if (IS_WIN or IS_LINUX) else "command+a")
    return True, "Selected all"


def _mm_undo(e) -> Tuple[bool, str]:
    _send_keys("ctrl+z" if (IS_WIN or IS_LINUX) else "command+z")
    return True, "Undone"


def _mm_redo(e) -> Tuple[bool, str]:
    _send_keys("ctrl+y" if IS_WIN else "ctrl+shift+z")
    return True, "Redone"


# ── Consolidated Window Sizing ───────────────────────────────────────────────
def _win_max(e) -> Tuple[bool, str]:
    """Maximize currently active window."""
    if IS_WIN:
        _send_keys("win+Up")
    elif IS_LINUX:
        _run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,maximized_vert,maximized_horz"])
    return True, "Window maximized"


def _mm_maximize_app(e) -> Tuple[bool, str]:
    """Delegates to consolidated _win_max."""
    return _win_max(e)


def _win_min_all(e) -> Tuple[bool, str]:
    """Show desktop / minimize all windows."""
    if IS_WIN:
        _send_keys("win+d")
    elif IS_MAC:
        _send_keys("F11")
    else:
        _run(["xdotool", "key", "super+d"])
    return True, "Desktop displayed"


def _mm_minimize_app(e) -> Tuple[bool, str]:
    """Delegates to consolidated _win_min_all."""
    return _win_min_all(e)


# ── Screenshot & Media Playback ──────────────────────────────────────────────
def _sys_ss(e) -> Tuple[bool, str]:
    """Capture full screen screenshot."""
    shots_dir = Path.home() / "Pictures" / "Screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    filename = f"screenshot_{int(time.time())}.png"
    target = shots_dir / filename
    try:
        if IS_WIN:
            try:
                import pyautogui
                pyautogui.screenshot(str(target))
            except Exception:
                _send_keys("win+PrintScreen")
        elif IS_MAC:
            subprocess.run(["screencapture", str(target)])
        else:
            for cmd in (["gnome-screenshot", "-f", str(target)], ["scrot", str(target)], ["import", "-window", "root", str(target)]):
                ok, _ = _run(cmd)
                if ok:
                    break
            else:
                _send_keys("Print")
        return True, f"Screenshot saved: {target}"
    except Exception as ex:
        return False, f"Screenshot failed: {ex}"


def _mm_screenshot(e) -> Tuple[bool, str]:
    return _sys_ss(e)


def _mm_play(e) -> Tuple[bool, str]:
    _send_keys("MediaPlayPause")
    return True, "Play / Pause toggled"


def _mm_next(e) -> Tuple[bool, str]:
    _send_keys("MediaNextTrack")
    return True, "Next track"


def _mm_prev(e) -> Tuple[bool, str]:
    _send_keys("MediaPrevTrack")
    return True, "Previous track"


def _mm_webcam_photo(e) -> Tuple[bool, str]:
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            pics_dir = Path.home() / "Pictures"
            pics_dir.mkdir(parents=True, exist_ok=True)
            path = pics_dir / f"webcam_{int(time.time())}.jpg"
            cv2.imwrite(str(path), frame)
            return True, f"Photo captured: {path}"
        return False, "Failed to read from camera"
    except Exception as ex:
        return False, f"Webcam error: {ex}"
