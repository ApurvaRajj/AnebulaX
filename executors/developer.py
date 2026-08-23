"""
Nebula v9 — Developer Tools, Git, Docker, NPM, and File System Executors
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Tuple

from config import IS_WIN, IS_MAC, IS_LINUX
from executors.common import _run_out, _run, _app


def _dev_git(args: list, empty: str = "") -> Tuple[bool, str]:
    return _run_out(["git"] + args, empty=empty)


def _dev_git_commit(e) -> Tuple[bool, str]:
    msg = e.get("query", "update").strip()
    return _run_out(["git", "commit", "-m", msg])


def _dev_git_checkout(e) -> Tuple[bool, str]:
    branch = e.get("query", "main").strip()
    return _run_out(["git", "checkout", branch])


def _dev_git_merge(e) -> Tuple[bool, str]:
    branch = e.get("query", "").strip()
    return _run_out(["git", "merge", branch])


def _dev_git_clone(e) -> Tuple[bool, str]:
    repo = e.get("url", "") or e.get("query", "")
    return _run_out(["git", "clone", repo])


def _dev_npm(action: str, *extra) -> Tuple[bool, str]:
    return _run_out(["npm", action] + list(extra))


def _dev_npm_run(e) -> Tuple[bool, str]:
    script = e.get("query", "dev").strip()
    return _run_out(["npm", "run", script])


def _dev_docker(action: str) -> Tuple[bool, str]:
    return _run_out(["docker", action])


def _dev_docker_cmd(e, action: str) -> Tuple[bool, str]:
    container = e.get("query", "").strip()
    return _run_out(["docker", action, container])


def _fs_mkdir(e) -> Tuple[bool, str]:
    name = e.get("query", "") or e.get("name", "new_folder")
    p = Path(name)
    p.mkdir(parents=True, exist_ok=True)
    return True, f"Created directory: {p.absolute()}"


def _fs_del_file(e) -> Tuple[bool, str]:
    name = e.get("query", "") or e.get("name", "")
    if not name:
        return False, "Specify file to delete"
    p = Path(name)
    if p.exists() and p.is_file():
        p.unlink()
        return True, f"Deleted file: {p.name}"
    return False, f"File not found: {name}"


def _app_chrome(e) -> Tuple[bool, str]:
    return _app("google-chrome", "Google Chrome", "chrome")


def _app_firefox(e) -> Tuple[bool, str]:
    return _app("firefox", "Firefox", "firefox")


def _app_brave(e) -> Tuple[bool, str]:
    return _app("brave-browser", "Brave Browser", "brave")


def _app_edge(e) -> Tuple[bool, str]:
    return _app("microsoft-edge", "Microsoft Edge", "msedge")


def _app_vscode(e) -> Tuple[bool, str]:
    return _app("code", "Visual Studio Code", "code")


def _app_terminal(e) -> Tuple[bool, str]:
    if IS_WIN:
        subprocess.Popen(["cmd", "/c", "start", "wt"], shell=True)
    elif IS_MAC:
        subprocess.Popen(["open", "-a", "Terminal"])
    else:
        for t in ["gnome-terminal", "konsole", "xfce4-terminal", "alacritty", "kitty", "xterm"]:
            if shutil.which(t):
                subprocess.Popen([t], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                break
    return True, "Terminal opened"


def _app_calc(e) -> Tuple[bool, str]:
    return _app("gnome-calculator", "Calculator", "calc")


def _app_notepad(e) -> Tuple[bool, str]:
    return _app("gedit", "TextEdit", "notepad")


def _app_spotify(e) -> Tuple[bool, str]:
    return _app("spotify", "Spotify", "spotify")


def _app_vlc(e) -> Tuple[bool, str]:
    return _app("vlc", "VLC", "vlc")


def _app_explorer(e) -> Tuple[bool, str]:
    return _app("nautilus", "Finder", "explorer")


def _app_settings(e) -> Tuple[bool, str]:
    return _app("gnome-control-center", "System Settings", "ms-settings:")
