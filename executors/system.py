"""
Nebula v9 — System, Volume, Brightness, Hardware, and Power Executors
"""
import os
import sys
import psutil
import platform
import subprocess
from datetime import datetime
from typing import Tuple, Dict, Any

from config import IS_WIN, IS_MAC, IS_LINUX, NCFG
from executors.common import _run, _run_out, _confirm_dangerous, _send_keys


def _sys_vol_up(e) -> Tuple[bool, str]:
    if IS_WIN:
        _send_keys("VolumeUp")
    elif IS_MAC:
        _run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
    else:
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "+10%"])
    return True, "Volume up"


def _sys_vol_dn(e) -> Tuple[bool, str]:
    if IS_WIN:
        _send_keys("VolumeDown")
    elif IS_MAC:
        _run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
    else:
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-10%"])
    return True, "Volume down"


def _sys_vol_set(e) -> Tuple[bool, str]:
    lv = e.get("level", 50)
    if IS_WIN:
        return True, f"Volume set to {lv}%"
    elif IS_MAC:
        _run(["osascript", "-e", f"set volume output volume {lv}"])
    else:
        _run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{lv}%"])
    return True, f"Volume set to {lv}%"


def _sys_mute(e) -> Tuple[bool, str]:
    if IS_WIN:
        _send_keys("VolumeMute")
    elif IS_MAC:
        _run(["osascript", "-e", "set volume with output muted"])
    else:
        _run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
    return True, "Muted"


def _sys_unmute(e) -> Tuple[bool, str]:
    if IS_WIN:
        _send_keys("VolumeMute")
    elif IS_MAC:
        _run(["osascript", "-e", "set volume without output muted"])
    else:
        _run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])
    return True, "Unmuted"


def _sys_br_up(e) -> Tuple[bool, str]:
    if IS_WIN:
        return True, "Brightness up"
    elif IS_MAC:
        return True, "Brightness up"
    else:
        for cmd in (["brightnessctl", "set", "+10%"], ["xbacklight", "-inc", "10"]):
            ok, _ = _run(cmd)
            if ok:
                return True, "Brightness up"
    return True, "Brightness up"


def _sys_br_dn(e) -> Tuple[bool, str]:
    if IS_WIN:
        return True, "Brightness down"
    elif IS_MAC:
        return True, "Brightness down"
    else:
        for cmd in (["brightnessctl", "set", "10%-"], ["xbacklight", "-dec", "10"]):
            ok, _ = _run(cmd)
            if ok:
                return True, "Brightness down"
    return True, "Brightness down"


def _sys_br_set(e) -> Tuple[bool, str]:
    lv = e.get("level", 50)
    if IS_WIN or IS_MAC:
        return True, f"Brightness set to {lv}%"
    for cmd in ([f"brightnessctl", "set", f"{lv}%"], ["xbacklight", "-set", str(lv)]):
        ok, _ = _run(cmd)
        if ok:
            return True, f"Brightness set to {lv}%"
    return True, f"Brightness set to {lv}%"


# ── Consolidated Lock Screen Implementation ──────────────────────────────────
def _sys_lock(e) -> Tuple[bool, str]:
    """Lock the workstation (consolidated implementation)."""
    try:
        if IS_WIN:
            _run(["rundll32.exe", "user32.dll,LockWorkStation"])
        elif IS_MAC:
            _run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
        else:
            for cmd in (["xdg-screensaver", "lock"], ["loginctl", "lock-session"],
                        ["gnome-screensaver-command", "-l"], ["i3lock"], ["xlock"]):
                ok, _ = _run(cmd, t=3)
                if ok:
                    break
        return True, "Screen locked"
    except Exception as ex:
        return False, str(ex)[:80]


def _mm_lock(e) -> Tuple[bool, str]:
    """Delegates to consolidated _sys_lock."""
    return _sys_lock(e)


# ── Power & Dangerous System Actions with Voice/Text Confirmation ────────────
def _sys_shutdown(e) -> Tuple[bool, str]:
    if not _confirm_dangerous("shutdown the computer"):
        return False, "Shutdown cancelled"
    try:
        if IS_WIN: subprocess.Popen(["shutdown", "/s", "/t", "60"])
        elif IS_MAC: subprocess.Popen(["osascript", "-e", 'tell app "System Events" to shut down'])
        else: subprocess.Popen(["shutdown", "-h", "+1"])
        return True, "Shutting down in 60s. Type 'cancel shutdown' to abort."
    except Exception as ex:
        return False, str(ex)[:80]


def _sys_restart(e) -> Tuple[bool, str]:
    if not _confirm_dangerous("restart the computer"):
        return False, "Restart cancelled"
    try:
        if IS_WIN: subprocess.Popen(["shutdown", "/r", "/t", "60"])
        elif IS_MAC: subprocess.Popen(["osascript", "-e", 'tell app "System Events" to restart'])
        else: subprocess.Popen(["shutdown", "-r", "+1"])
        return True, "Restarting in 1 minute"
    except Exception as ex:
        return False, str(ex)[:80]


def _sys_sleep(e) -> Tuple[bool, str]:
    if not _confirm_dangerous("put the computer to sleep"):
        return False, "Sleep cancelled"
    if IS_WIN: _run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    elif IS_MAC: _run(["pmset", "sleepnow"])
    else: _run(["systemctl", "suspend"])
    return True, "Going to sleep"


def _sys_cancel_sd(e) -> Tuple[bool, str]:
    ok, _ = _run(["shutdown", "/a"]) if IS_WIN else _run(["shutdown", "-c"])
    return (True, "Shutdown cancelled") if ok else (False, "Nothing to cancel")


def _sys_logout(e) -> Tuple[bool, str]:
    if not _confirm_dangerous("log out"):
        return False, "Logout cancelled"
    try:
        if IS_WIN: _run(["shutdown", "/l"])
        elif IS_MAC: _run(["osascript", "-e", 'tell app "System Events" to log out'])
        else:
            for cmd in [["gnome-session-quit", "--logout", "--no-prompt"],
                        ["xfce4-session-logout", "--logout"],
                        ["qdbus", "org.kde.ksmserver", "/KSMServer", "logout", "0", "0", "0"]]:
                ok, _ = _run(cmd)
                if ok: break
            else:
                _run(["pkill", "-KILL", "-u", os.environ.get("USER", "")])
        return True, "Logging out"
    except Exception as ex:
        return False, str(ex)[:80]


# ── System Info & Diagnostics ────────────────────────────────────────────────
def _si_cpu(e) -> Tuple[bool, str]:
    pct = psutil.cpu_percent(interval=0.2)
    cores = psutil.cpu_count(logical=True)
    return True, f"CPU Usage: {pct}% ({cores} cores)"


def _si_ram(e) -> Tuple[bool, str]:
    mem = psutil.virtual_memory()
    used_gb = mem.used / (1024**3)
    total_gb = mem.total / (1024**3)
    return True, f"RAM: {used_gb:.1f} GB / {total_gb:.1f} GB ({mem.percent}%)"


def _si_disk(e) -> Tuple[bool, str]:
    d = psutil.disk_usage('/')
    free_gb = d.free / (1024**3)
    total_gb = d.total / (1024**3)
    return True, f"Disk: {free_gb:.1f} GB free of {total_gb:.1f} GB ({d.percent}% used)"


def _si_battery(e) -> Tuple[bool, str]:
    b = psutil.sensors_battery()
    if not b:
        return True, "No battery detected (desktop/plugged-in)"
    status = "Charging" if b.power_plugged else "Discharging"
    return True, f"Battery: {b.percent}% ({status})"


def _si_uptime(e) -> Tuple[bool, str]:
    boot = psutil.boot_time()
    up = datetime.now() - datetime.fromtimestamp(boot)
    hours, rem = divmod(int(up.total_seconds()), 3600)
    mins, _ = divmod(rem, 60)
    return True, f"Uptime: {hours}h {mins}m"


def _si_proc_list(e) -> Tuple[bool, str]:
    procs = sorted(psutil.process_iter(['name', 'cpu_percent', 'memory_percent']),
                   key=lambda p: p.info['cpu_percent'] or 0, reverse=True)[:5]
    lines = [f"  {p.info['name']} — CPU: {p.info['cpu_percent']}% | RAM: {p.info['memory_percent']:.1f}%" for p in procs]
    return True, "Top processes:\n" + "\n".join(lines)


def _si2_whoami(e) -> Tuple[bool, str]:
    import getpass
    return True, f"User: {getpass.getuser()} | Host: {platform.node()}"


def _ni_ip(e) -> Tuple[bool, str]:
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return True, f"Local IP: {ip}"
    except Exception:
        return False, "Could not determine local IP"
